import styles from './LoadingSpinner.module.css';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'neutral';
  className?: string;
}

export default function LoadingSpinner({ 
  size = 'md', 
  color = 'primary',
  className = '' 
}: LoadingSpinnerProps) {
  const spinnerClasses = [
    styles.spinner,
    styles[size],
    styles[color],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={spinnerClasses}>
      <div className={styles.circle}></div>
    </div>
  );
}