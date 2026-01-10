import React from 'react';

interface FeatureGateProps {
    requiredTier: 'text_only' | 'standard' | 'pro';
    currentTier: string;
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

const TIER_LEVELS = {
    text_only: 1,
    standard: 2,
    pro: 3
};

export function FeatureGate({ requiredTier, currentTier, children, fallback }: FeatureGateProps) {
    const currentLevel = TIER_LEVELS[currentTier as keyof typeof TIER_LEVELS] || 1;
    const requiredLevel = TIER_LEVELS[requiredTier];

    const isEnabled = currentLevel >= requiredLevel;

    if (isEnabled) {
        return <>{children}</>;
    }

    if (fallback) {
        return <>{fallback}</>;
    }

    return (
        <div className="locked-feature">
            <div className="lock-icon">🔒</div>
            <div className="lock-message">
                Requires {requiredTier === 'pro' ? 'aiDAPTIV+' : `${requiredTier} tier`}
            </div>
        </div>
    );
}
