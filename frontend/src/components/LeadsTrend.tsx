interface LeadsTrendProps {
  points: number[];
  accentColor?: string;
}

const WIDTH = 280;
const HEIGHT = 64;
const PADDING = 8;

export function LeadsTrend({ points, accentColor = "#eb6834" }: LeadsTrendProps) {
  if (points.length === 0) {
    return <div className="leads-trend-empty">No runs yet</div>;
  }

  const max = Math.max(...points, 1);
  const min = 0;
  const range = max - min || 1;
  const stepX = points.length > 1 ? (WIDTH - PADDING * 2) / (points.length - 1) : 0;

  const coords = points.map((value, i) => {
    const x = PADDING + i * stepX;
    const y = HEIGHT - PADDING - ((value - min) / range) * (HEIGHT - PADDING * 2);
    return [x, y] as const;
  });

  const linePath = coords.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
  const areaPath = `${linePath} L${coords[coords.length - 1][0]},${HEIGHT - PADDING} L${coords[0][0]},${HEIGHT - PADDING} Z`;
  const [lastX, lastY] = coords[coords.length - 1];

  return (
    <svg
      className="leads-trend-svg"
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      width="100%"
      height={HEIGHT}
      role="img"
      aria-label={`Leads per run trend, latest value ${points[points.length - 1]}`}
    >
      <path d={areaPath} fill={accentColor} opacity={0.1} stroke="none" />
      <path d={linePath} fill="none" stroke={accentColor} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={lastX} cy={lastY} r={4} fill={accentColor} stroke="#fcfcfb" strokeWidth={2} />
    </svg>
  );
}
