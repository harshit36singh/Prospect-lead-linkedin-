interface GradeBarProps {
  hot: number;
  warm: number;
  cold: number;
}

const SEGMENTS: { key: "hot" | "warm" | "cold"; label: string; color: string }[] = [
  { key: "hot", label: "Hot", color: "#e34948" },
  { key: "warm", label: "Warm", color: "#eda100" },
  { key: "cold", label: "Cold", color: "#2a78d6" },
];

export function GradeBar({ hot, warm, cold }: GradeBarProps) {
  const total = hot + warm + cold;
  const counts = { hot, warm, cold };

  return (
    <div className="grade-bar-widget">
      <div className="grade-bar-track">
        {total === 0 ? (
          <div className="grade-bar-empty" />
        ) : (
          SEGMENTS.map((segment) => {
            const count = counts[segment.key];
            if (count === 0) return null;
            const widthPct = (count / total) * 100;
            return (
              <div
                key={segment.key}
                className="grade-bar-segment"
                style={{ width: `${widthPct}%`, backgroundColor: segment.color }}
              />
            );
          })
        )}
      </div>
      <ul className="grade-bar-legend">
        {SEGMENTS.map((segment) => (
          <li key={segment.key}>
            <span className="legend-swatch" style={{ backgroundColor: segment.color }} />
            <span className="legend-label">{segment.label}</span>
            <span className="legend-count">{counts[segment.key]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
