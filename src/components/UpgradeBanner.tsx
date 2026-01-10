import { AlertTriangle } from 'lucide-react';

interface UpgradeBannerProps {
  currentTier: string;
  onEnableAiDAPTIV: () => void;
}

export function UpgradeBanner({ currentTier, onEnableAiDAPTIV }: UpgradeBannerProps) {
  if (currentTier === 'pro') {
    return null;
  }

  const getMessage = () => {
    if (currentTier === 'text_only') {
      return 'Image and video analysis disabled. Enable aiDAPTIV+ to unlock all features.';
    }
    return 'Video analysis and infographic generation require aiDAPTIV+.';
  };

  const getDisabledFeatures = () => {
    if (currentTier === 'text_only') {
      return ['Image Analysis', 'Video Analysis', 'Infographic Generation'];
    }
    return ['Video Analysis', 'Infographic Generation', 'Parallel Multi-Agent'];
  };

  return (
    <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-xl p-5 mb-6 shadow-lg shadow-red-500/30">
      <div className="flex items-center gap-4">
        <AlertTriangle className="text-white flex-shrink-0" size={24} />
        <div className="flex-1">
          <div className="text-white font-semibold text-base mb-1">
            Limited Mode Active
          </div>
          <div className="text-white/95 text-sm mb-2">
            {getMessage()}
          </div>
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="text-white/90 font-medium">Disabled:</span>
            {getDisabledFeatures().map((feature, i) => (
              <span key={i} className="bg-white/20 px-2 py-1 rounded-lg text-white">
                {feature}
              </span>
            ))}
          </div>
        </div>
        <button
          className="bg-white text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all hover:-translate-y-0.5 hover:shadow-lg flex-shrink-0"
          onClick={() => {
            console.log('UpgradeBanner: Enable aiDAPTIV+ clicked');
            onEnableAiDAPTIV();
          }}
        >
          Enable aiDAPTIV+
        </button>
      </div>
    </div>
  );
}
