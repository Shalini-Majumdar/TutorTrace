export function toPercentage(value) {
  if (value == null || isNaN(value)) return 0;
  return Math.round(value * 100);
}

export function masteryBand(mastery) {
  if (mastery == null) return { key: 'unknown', label: 'Not yet assessed', color: 'ink' };
  if (mastery < 0.3) return { key: 'low', label: 'Needs attention', color: 'coral' };
  if (mastery < 0.6) return { key: 'developing', label: 'Developing', color: 'amber' };
  if (mastery < 0.8) return { key: 'strong', label: 'Strong', color: 'teal' };
  return { key: 'high', label: 'High mastery', color: 'sage' };
}

export function difficultyLabel(level) {
  if (level === 1) return 'Easy';
  if (level === 2) return 'Medium';
  if (level === 3) return 'Hard';
  return `Level ${level}`;
}

export function confidenceToValue(level) {
  if (level === 'low') return 0.25;
  if (level === 'medium') return 0.5;
  if (level === 'high') return 0.85;
  return null;
}

export function formatTimestamp(unixSeconds) {
  if (!unixSeconds) return 'Not yet practiced';
  const date = new Date(unixSeconds * 1000);
  const now = new Date();
  const diffMs = now - date;
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return 'Practiced just now';
  if (diffHours < 24) return `Practiced ${diffHours}h ago`;
  if (diffDays === 1) return 'Practiced yesterday';
  if (diffDays < 7) return `Practiced ${diffDays}d ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export function formatTimeTaken(seconds) {
  if (seconds == null) return '';
  if (seconds < 10) return `${seconds.toFixed(1)}s`;
  return `${Math.round(seconds)}s`;
}
