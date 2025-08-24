import { ReactNode } from 'react';
import styles from './ErrorMessage.module.css';
import Button from './Button';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
  children?: ReactNode;
}

export default function ErrorMessage({
  title = 'Error',
  message,
  onRetry,
  className = '',
  children
}: ErrorMessageProps) {
  return (
    <div className={`${styles.errorContainer} ${className}`}>
      <div className={styles.errorIcon}>⚠️</div>
      <div className={styles.errorContent}>
        <h3 className={styles.errorTitle}>{title}</h3>
        <p className={styles.errorMessage}>{message}</p>
        {children}
        {onRetry && (
          <Button 
            variant="secondary" 
            size="sm" 
            onClick={onRetry}
            className={styles.retryButton}
          >
            Try Again
          </Button>
        )}
      </div>
    </div>
  );
}