interface DashboardIconProps {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export default function DashboardIcon({ 
  width = 24, 
  height = 24, 
  color = 'currentColor',
  className 
}: DashboardIconProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}