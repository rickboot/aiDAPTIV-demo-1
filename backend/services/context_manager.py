import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

# Try to import ChromaClient, handle if not installed yet
try:
    from backend.vector_db.chroma_client import ChromaClient
except ImportError:
    try:
        from vector_db.chroma_client import ChromaClient
    except ImportError:
        ChromaClient = None

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages the hierarchical memory system:
    1. Active Context (RAM): Immediate context for LLM
    2. Recent Context (SSD): Offloaded by aiDAPTIV+ automatically
    3. Long-term Memory (Vector DB): Archivally stored knowledge
    """
    
    def __init__(self, use_vector_db: bool = True):
        self.active_documents = []  # List of current documents in active context
        self.total_tokens = 0
        self.max_tokens_ram = 60000  # Target RAM limit before pruning to Vector DB
        
        self.chroma_client = None
        if use_vector_db and ChromaClient:
            try:
                self.chroma_client = ChromaClient()
                logger.info("ContextManager initialized with Vector DB support")
            except Exception as e:
                logger.error(f"Failed to initialize Vector DB in ContextManager: {e}")
        
    def add_document(self, document: Dict[str, Any], token_count: int) -> Dict[str, Any]:
        """
        Add a document to the context system.
        Stores in both active context AND Vector DB for RAG retrieval.
        If active context exceeds limit, prune oldest documents to Vector DB.
        
        Returns status dict with optional RAG storage info.
        """
        # Add to active list
        doc_with_meta = document.copy()
        doc_with_meta["added_at"] = time.time()
        doc_with_meta["tokens"] = token_count
        
        self.active_documents.append(doc_with_meta)
        self.total_tokens += token_count
        
        rag_storage_info = None
        
        # RAG: Store document in Vector DB immediately for retrieval
        if self.chroma_client:
            try:
                content = document.get("content") or document.get("text", "")
                if content:
                    chroma_doc = {
                        "id": f"{document.get('name', 'doc')}_{int(time.time())}",
                        "content": content,
                        "metadata": {
                            "source": document.get("category", "unknown"),
                            "title": document.get("name", "untitled"),
                            "added_at": datetime.utcnow().isoformat(),
                            "tokens": token_count
                        }
                    }
                    added_count = self.chroma_client.add_documents([chroma_doc])
                    total_count = self.chroma_client.count()
                    logger.info(f"RAG: Stored document '{document.get('name')}' in Vector DB ({added_count} added, total: {total_count})")
                    
                    # Store RAG info for event emission
                    rag_storage_info = {
                        "stored": True,
                        "document_name": document.get('name', 'untitled'),
                        "document_category": document.get("category", "unknown"),
                        "tokens": token_count,
                        "total_documents_in_db": total_count
                    }
            except Exception as e:
                logger.warning(f"Failed to store document in Vector DB: {e}")
        
        logger.info(f"Added document to active context. Total tokens: {self.total_tokens}")
        
        # Check if pruning is needed
        pruned_count = 0
        if self.total_tokens > self.max_tokens_ram:
            pruned_count = self._prune_context()
            
        result = {
            "status": "success",
            "active_docs": len(self.active_documents),
            "total_tokens": self.total_tokens,
            "pruned": pruned_count
        }
        
        # Add RAG storage info if available
        if rag_storage_info:
            result["rag_storage"] = rag_storage_info
            
        return result
        
    def _prune_context(self) -> int:
        """
        Move oldest documents from Active Context to Vector DB until under limit.
        Returns number of documents pruned.
        """
        if not self.chroma_client:
            logger.warning("Vector DB not available, cannot prune context safely")
            return 0
            
        pruned_count = 0
        
        # Sort by added time (oldest first)
        # In practice, active_documents is already sorted by append order
        
        while self.total_tokens > (self.max_tokens_ram * 0.9):  # Prune down to 90%
            if not self.active_documents:
                break
                
            # Pop oldest document
            doc = self.active_documents.pop(0)
            doc_tokens = doc.get("tokens", 0)
            self.total_tokens -= doc_tokens
            
            # Archive to Vector DB
            # Ensure doc has 'content' key, mapping from 'text' if needed
            content = doc.get("content") or doc.get("text")
            if content:
                # Prepare for Chroma
                chroma_doc = {
                    "content": content,
                    "metadata": {
                        "source": doc.get("category", "unknown"),
                        "title": doc.get("name", "untitled"),
                        "archived_at": datetime.utcnow().isoformat()
                    }
                }
                
                # Add to Vector DB
                self.chroma_client.add_documents([chroma_doc])
                pruned_count += 1
                logger.info(f"Pruned document '{doc.get('name')}' ({doc_tokens} tokens) to Vector DB")
            else:
                logger.warning(f"Skipping pruning for doc '{doc.get('name')}' - no content")
                
        return pruned_count

    def retrieve_context(self, query: str, max_tokens: int = 5000, exclude_titles: set = None) -> tuple[List[Dict], Dict]:
        """
        Retrieve relevant context from Vector DB for a specific query.
        Used to temporarily augment active context (RAG).
        
        Args:
            query: Search query text
            max_tokens: Maximum tokens to retrieve
            exclude_titles: Set of document titles to exclude from results
        """
        if not self.chroma_client:
            logger.debug("RAG: ChromaDB client not available, skipping retrieval")
            return [], {
                "query_preview": query[:100],
                "query_length": len(query),
                "candidates_found": 0,
                "documents_retrieved": 0,
                "tokens_retrieved": 0,
                "tokens_limit": max_tokens,
                "excluded_count": 0,
                "retrieved_document_names": []
            }
        
        if exclude_titles is None:
            exclude_titles = set()
        
        logger.info(f"RAG: Querying Vector DB with query (first 100 chars): {query[:100]}...")
        logger.debug(f"RAG: Excluding {len(exclude_titles)} document titles from results")
            
        # Request more results than needed, since we'll filter some out
        results = self.chroma_client.query_similar(query, n_results=10)
        logger.info(f"RAG: ChromaDB returned {len(results)} candidate documents")
        
        retrieved_docs = []
        current_tokens = 0
        excluded_count = 0
        
        for res in results:
            # Skip documents that match excluded titles
            metadata = res.get("metadata", {})
            doc_title = metadata.get("title", "").lower()
            if doc_title in exclude_titles:
                excluded_count += 1
                logger.debug(f"RAG: Excluded document '{doc_title}' (in current batch)")
                continue
            
            # Estimate tokens (rough approx 4 chars/token)
            text = res.get("content", "")
            if not text:
                continue
                
            tokens = len(text) // 4
            
            if current_tokens + tokens > max_tokens:
                logger.debug(f"RAG: Token limit reached ({current_tokens}/{max_tokens}), stopping retrieval")
                break
            
            doc_name = metadata.get("title", "Unknown")
            logger.debug(f"RAG: Including document '{doc_name}' ({tokens} tokens, total: {current_tokens + tokens}/{max_tokens})")
            retrieved_docs.append({
                "content": text,
                "metadata": metadata,
                "source": "long_term_memory"
            })
            current_tokens += tokens
        
        logger.info(f"RAG: Retrieved {len(retrieved_docs)} documents ({current_tokens} tokens), excluded {excluded_count} duplicates")
        
        # Return retrieval info along with documents
        retrieval_info = {
            "query_preview": query[:100],
            "query_length": len(query),
            "candidates_found": len(results),
            "documents_retrieved": len(retrieved_docs),
            "tokens_retrieved": current_tokens,
            "tokens_limit": max_tokens,
            "excluded_count": excluded_count,
            "retrieved_document_names": [doc.get("metadata", {}).get("title", "Unknown") for doc in retrieved_docs]
        }
        
        return retrieved_docs, retrieval_info

    def get_context_stats(self) -> Dict[str, Any]:
        """Return current memory stats."""
        return {
            "active_docs": len(self.active_documents),
            "active_tokens": self.total_tokens,
            "vector_db_docs": self.chroma_client.count() if self.chroma_client else 0
        }

    def save_state(self, file_path: Path):
        """Save active context state to disk."""
        try:
            state = {
                "total_tokens": self.total_tokens,
                "active_documents": self.active_documents
            }
            with open(file_path, 'w') as f:
                json.dump(state, f, default=str, indent=2)
            logger.info(f"Saved context state to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save context state: {e}")

    def load_state(self, file_path: Path):
        """Load active context state from disk."""
        try:
            if not file_path.exists():
                return
            
            with open(file_path, 'r') as f:
                state = json.load(f)
                
            self.total_tokens = state.get("total_tokens", 0)
            self.active_documents = state.get("active_documents", [])
            logger.info(f"Loaded context state: {len(self.active_documents)} docs, {self.total_tokens} tokens")
        except Exception as e:
            logger.error(f"Failed to load context state: {e}")
