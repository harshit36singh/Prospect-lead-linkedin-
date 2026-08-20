interface StatTileProps {
  label: string;
  value: string | number;
}

function formatValue(value: string | number): string {
  if (typeof value === "string") return value;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return String(value);
}

export function StatTile({ label, value }: StatTileProps) {
  return (
    <div className="stat-tile">
      <span className="stat-tile-value">{formatValue(value)}</span>
      <span className="stat-tile-label">{label}</span>
    </div>
  );
}
