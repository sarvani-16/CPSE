import React from 'react';

interface ConfidenceBadgeProps {
  score?: number;
  threshold?: number;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ score = 0, threshold = 0.85 }) => {
  const pct = Math.round(score * 100);
  const isHigh = score >= threshold;
  const isMedium = score >= 0.70 && score < threshold;

  const colorClass = isHigh ? 'highlight-success' : isMedium ? 'highlight-gold' : 'highlight-danger';

  return (
    <div className="confidence-pill-wrap">
      <span className={`confidence-val ${colorClass}`}>{pct}%</span>
      <div className="confidence-track">
        <div
          className={`confidence-bar ${isHigh ? 'bg-success' : isMedium ? 'bg-gold' : 'bg-danger'}`}
          style={{ width: `${pct}%` }}
        ></div>
      </div>
    </div>
  );
};
