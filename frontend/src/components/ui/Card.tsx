import { ReactNode } from 'react';
import styles from './Card.module.css';

interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
}

export default function Card({
  children,
  variant = 'default',
  padding = 'md',
  className = '',
  onClick
}: CardProps) {
  const cardClasses = [
    styles.card,
    styles[variant],
    styles[`padding-${padding}`],
    onClick && styles.clickable,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses} onClick={onClick}>
      {children}
    </div>
  );
}