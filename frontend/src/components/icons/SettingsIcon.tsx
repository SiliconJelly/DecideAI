interface SettingsIconProps {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export default function SettingsIcon({ 
  width = 24, 
  height = 24, 
  color = 'currentColor',
  className 
}: SettingsIconProps) {
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
      <circle cx="12" cy="12" r="3" />
      <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m11-7a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2m-6 0a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2" />
    </svg>
  );
}