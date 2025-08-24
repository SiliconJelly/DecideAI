interface FilterIconProps {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export default function FilterIcon({ 
  width = 24, 
  height = 24, 
  color = 'currentColor',
  className 
}: FilterIconProps) {
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
      <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46" />
    </svg>
  );
}