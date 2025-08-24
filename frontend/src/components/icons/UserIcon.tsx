interface UserIconProps {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export default function UserIcon({ 
  width = 24, 
  height = 24, 
  color = 'currentColor',
  className 
}: UserIconProps) {
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
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}