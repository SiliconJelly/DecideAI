import { ReactNode, forwardRef } from 'react';
import styles from './Input.module.css';

interface InputProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  type?: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url';
  disabled?: boolean;
  error?: string;
  required?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  className?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  disabled = false,
  error,
  required = false,
  leftIcon,
  rightIcon,
  className = ''
}, ref) => {
  const inputClasses = [
    styles.input,
    leftIcon && styles.hasLeftIcon,
    rightIcon && styles.hasRightIcon,
    error && styles.error,
    disabled && styles.disabled,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={styles.container}>
      {label && (
        <label className={styles.label}>
          {label}
          {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <div className={styles.inputWrapper}>
        {leftIcon && <div className={styles.leftIcon}>{leftIcon}</div>}
        <input
          ref={ref}
          type={type}
          className={inputClasses}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={disabled}
          required={required}
        />
        {rightIcon && <div className={styles.rightIcon}>{rightIcon}</div>}
      </div>
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;