import React from 'react';
import { Clock, Zap, Layers, TrendingUp } from 'lucide-react';

interface PerformanceMetrics {
    time_seconds: number;
    model_swaps: number;
    features_enabled: number;
    quality_score: number;
}

interface PerformanceComparisonProps {
    baseline: PerformanceMetrics;
    current: PerformanceMetrics;
}

export function PerformanceComparison({ baseline, current }: PerformanceComparisonProps) {
    const calculateImprovement = (baseValue: number, currentValue: number, inverse: boolean = false) => {
        if (baseValue === 0) return 0;
        const improvement = inverse
            ? ((baseValue - currentValue) / baseValue) * 100
            : ((currentValue - baseValue) / baseValue) * 100;
        return Math.round(improvement);
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    return (
        <div className="performance-comparison">
            <h3 className="comparison-title">Performance Comparison</h3>

            <div className="metrics-grid">
                <MetricCard
                    icon={<Clock size={20} />}
                    label="Analysis Time"
                    baseline={formatTime(baseline.time_seconds)}
                    current={formatTime(current.time_seconds)}
                    improvement={calculateImprovement(baseline.time_seconds, current.time_seconds, true)}
                    inverse
                />

                <MetricCard
                    icon={<Zap size={20} />}
                    label="Model Swaps"
                    baseline={baseline.model_swaps.toString()}
                    current={current.model_swaps.toString()}
                    improvement={calculateImprovement(baseline.model_swaps, current.model_swaps, true)}
                    inverse
                />

                <MetricCard
                    icon={<Layers size={20} />}
                    label="Features Enabled"
                    baseline={`${baseline.features_enabled}/5`}
                    current={`${current.features_enabled}/5`}
                    improvement={calculateImprovement(baseline.features_enabled, current.features_enabled)}
                />

                <MetricCard
                    icon={<TrendingUp size={20} />}
                    label="Quality Score"
                    baseline={`${baseline.quality_score}/10`}
                    current={`${current.quality_score}/10`}
                    improvement={calculateImprovement(baseline.quality_score, current.quality_score)}
                />
            </div>

            <style jsx>{`
        .performance-comparison {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 24px;
          margin-top: 24px;
        }
        
        .comparison-title {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 20px;
          color: white;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }
      `}</style>
        </div>
    );
}

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    baseline: string;
    current: string;
    improvement: number;
    inverse?: boolean;
}

function MetricCard({ icon, label, baseline, current, improvement, inverse = false }: MetricCardProps) {
    const isPositive = inverse ? improvement > 0 : improvement > 0;

    return (
        <div className="metric-card">
            <div className="metric-header">
                <div className="metric-icon">{icon}</div>
                <div className="metric-label">{label}</div>
            </div>

            <div className="metric-values">
                <div className="value-row">
                    <span className="value-label">Without aiDAPTIV+:</span>
                    <span className="value">{baseline}</span>
                </div>
                <div className="value-row current">
                    <span className="value-label">With aiDAPTIV+:</span>
                    <span className="value highlighted">{current}</span>
                </div>
            </div>

            {improvement !== 0 && (
                <div className={`improvement ${isPositive ? 'positive' : 'negative'}`}>
                    {isPositive ? '↑' : '↓'} {Math.abs(improvement)}% {isPositive ? 'better' : 'worse'}
                </div>
            )}

            <style jsx>{`
        .metric-card {
          background: rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          padding: 16px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
        }
        
        .metric-icon {
          color: #60a5fa;
        }
        
        .metric-label {
          font-size: 14px;
          font-weight: 500;
          color: rgba(255, 255, 255, 0.9);
        }
        
        .metric-values {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 12px;
        }
        
        .value-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 13px;
        }
        
        .value-label {
          color: rgba(255, 255, 255, 0.6);
        }
        
        .value {
          color: rgba(255, 255, 255, 0.8);
          font-weight: 500;
        }
        
        .value.highlighted {
          color: #60a5fa;
          font-weight: 600;
        }
        
        .improvement {
          font-size: 12px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 4px;
          text-align: center;
        }
        
        .improvement.positive {
          background: rgba(34, 197, 94, 0.2);
          color: #22c55e;
        }
        
        .improvement.negative {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }
      `}</style>
        </div>
    );
}
