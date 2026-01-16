"""
Video processing service for hybrid audio + visual analysis.
Extracts audio (Whisper) and frames (for LLaVA) from video files.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)

# Try to import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available. Install with: pip install openai-whisper")

# Try to import cv2 for frame extraction
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Install with: pip install opencv-python")


class VideoProcessor:
    """Process video files: extract audio transcript and key frames."""
    
    def __init__(self):
        self.whisper_model = None
        self.whisper_loaded = False
        # Lazy load Whisper model on first use (so we can emit status events)
    
    def _ensure_whisper_loaded(self) -> bool:
        """
        Lazy load Whisper model on first use.
        Returns True if model is available, False otherwise.
        """
        if self.whisper_loaded:
            return self.whisper_model is not None
        
        if not WHISPER_AVAILABLE:
            return False
        
        try:
            # Use smaller model in dev mode for faster loading
            import config as app_config
            whisper_model_size = "tiny" if app_config.DEV_MODE else "base"
            logger.info(f"Loading Whisper model ({whisper_model_size}) for audio transcription...")
            self.whisper_model = whisper.load_model(whisper_model_size)
            self.whisper_loaded = True
            logger.info(f"Whisper model ({whisper_model_size}) loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
            self.whisper_loaded = True  # Mark as attempted
            return False
    
    def extract_audio_transcript(self, video_path: str) -> Optional[str]:
        """
        Extract audio from video and transcribe using Whisper.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Transcribed text or None if failed
        """
        if not self._ensure_whisper_loaded():
            logger.warning("Whisper not available, cannot transcribe audio")
            return None
        
        try:
            logger.info(f"Transcribing audio from video: {Path(video_path).name}")
            result = self.whisper_model.transcribe(video_path)
            transcript = result.get("text", "").strip()
            
            if transcript:
                logger.info(f"Transcribed {len(transcript)} characters from audio")
                return transcript
            else:
                logger.warning("Whisper returned empty transcript")
                return None
                
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return None
    
    def extract_key_frames(self, video_path: str, num_frames: int = 10, output_dir: Optional[Path] = None) -> List[str]:
        """
        Extract key frames from video for visual analysis.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (evenly spaced)
            output_dir: Directory to save frames (creates temp dir if None)
            
        Returns:
            List of paths to extracted frame images
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available, cannot extract frames")
            return []
        
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                logger.error(f"Video file not found: {video_path}")
                return []
            
            # Create output directory
            if output_dir is None:
                output_dir = Path(tempfile.mkdtemp(prefix="video_frames_"))
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video: {total_frames} frames, {fps:.2f} fps, {duration:.1f}s duration")
            
            # Calculate frame indices to extract (evenly spaced)
            if total_frames == 0:
                logger.warning("Video has 0 frames")
                cap.release()
                return []
            
            frame_indices = []
            if num_frames >= total_frames:
                # Extract all frames
                frame_indices = list(range(total_frames))
            else:
                # Extract evenly spaced frames
                step = total_frames / (num_frames + 1)
                frame_indices = [int(i * step) for i in range(1, num_frames + 1)]
            
            extracted_frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count in frame_indices:
                    # Save frame
                    frame_filename = output_dir / f"frame_{frame_count:06d}.jpg"
                    cv2.imwrite(str(frame_filename), frame)
                    extracted_frames.append(str(frame_filename))
                    logger.debug(f"Extracted frame {frame_count} -> {frame_filename.name}")
                
                frame_count += 1
                if len(extracted_frames) >= num_frames:
                    break
            
            cap.release()
            
            logger.info(f"Extracted {len(extracted_frames)} frames from video")
            return extracted_frames
            
        except Exception as e:
            logger.error(f"Failed to extract frames: {e}")
            return []
    
    def process_video(self, video_path: str, num_frames: int = 10) -> Dict[str, any]:
        """
        Process video: extract audio transcript and key frames.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            
        Returns:
            Dict with 'transcript' (str), 'frame_paths' (List[str]), and 'whisper_loaded' (bool)
        """
        result = {
            "transcript": None,
            "frame_paths": [],
            "video_path": video_path,
            "success": False,
            "whisper_loaded": False
        }
        
        # Extract audio transcript (this will lazy-load Whisper if needed)
        was_loaded_before = self.whisper_loaded
        transcript = self.extract_audio_transcript(video_path)
        result["transcript"] = transcript
        result["whisper_loaded"] = self.whisper_loaded and not was_loaded_before  # True if just loaded
        
        # Extract key frames
        frame_paths = self.extract_key_frames(video_path, num_frames)
        result["frame_paths"] = frame_paths
        
        # Mark as successful if we got at least transcript or frames
        result["success"] = (transcript is not None) or (len(frame_paths) > 0)
        
        if result["success"]:
            logger.info(f"Successfully processed video: transcript={transcript is not None}, frames={len(frame_paths)}")
        else:
            logger.warning(f"Failed to process video: {video_path}")
        
        return result
