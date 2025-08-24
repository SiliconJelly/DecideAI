interface SearchIconProps {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export default function SearchIcon({ 
  width = 24, 
  height = 24, 
  color = 'currentColor',
  className 
}: SearchIconProps) {
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
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}