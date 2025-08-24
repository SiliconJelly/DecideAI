'use client';

import { useState } from 'react';
import styles from './ExpertForm.module.css';
import Input from '../ui/Input';
import Button from '../ui/Button';
import Card from '../ui/Card';
import ErrorMessage from '../ui/ErrorMessage';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useApiMutation } from '../../hooks/useApi';
import { apiService } from '../../services/api';
import { validateExpertData } from '../../utils/dataTransform';

interface ExpertFormProps {
  onSuccess?: (expert: any) => void;
  onCancel?: () => void;
}

export default function ExpertForm({ onSuccess, onCancel }: ExpertFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    bio: '',
    roles: '',
    sectors: '',
    regions: '',
    languages: '',
    years_experience: 0,
    file: null as File | null
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const { mutate, loading, error } = useApiMutation();

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear validation errors when user starts typing
    if (validationErrors.length > 0) {
      setValidationErrors([]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFormData(prev => ({ ...prev, file }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form data
    const errors = validateExpertData(formData);
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    if (!formData.file) {
      setValidationErrors(['CV file is required']);
      return;
    }

    try {
      const expertData = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone || undefined,
        bio: formData.bio || undefined,
        roles: formData.roles ? formData.roles.split(',').map(r => r.trim()) : undefined,
        sectors: formData.sectors ? formData.sectors.split(',').map(s => s.trim()) : undefined,
        regions: formData.regions ? formData.regions.split(',').map(r => r.trim()) : undefined,
        languages: formData.languages ? formData.languages.split(',').map(l => l.trim()) : undefined,
        years_experience: formData.years_experience || undefined,
        file: formData.file
      };

      const result = await mutate(apiService.submitExpert, expertData);
      onSuccess?.(result);
    } catch (err) {
      // Error is handled by the mutation hook
      console.error('Failed to submit expert:', err);
    }
  };

  return (
    <Card className={styles.expertForm}>
      <div className={styles.formHeader}>
        <h2>Submit Expert Profile</h2>
        <p>Add a new expert to the DecideAI system</p>
      </div>

      {validationErrors.length > 0 && (
        <ErrorMessage
          title="Validation Errors"
          message="Please fix the following issues:"
        >
          <ul className={styles.errorList}>
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </ErrorMessage>
      )}

      {error && (
        <ErrorMessage
          title="Submission Failed"
          message={error}
        />
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGrid}>
          <Input
            label="Full Name"
            placeholder="Enter expert's full name"
            value={formData.name}
            onChange={(value) => handleInputChange('name', value)}
            required
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="expert@example.com"
            value={formData.email}
            onChange={(value) => handleInputChange('email', value)}
            required
          />

          <Input
            label="Phone Number"
            type="tel"
            placeholder="+1 (555) 123-4567"
            value={formData.phone}
            onChange={(value) => handleInputChange('phone', value)}
          />

          <Input
            label="Years of Experience"
            type="number"
            placeholder="0"
            value={formData.years_experience.toString()}
            onChange={(value) => handleInputChange('years_experience', parseInt(value) || 0)}
          />

          <Input
            label="Roles (comma-separated)"
            placeholder="Senior Researcher, Consultant"
            value={formData.roles}
            onChange={(value) => handleInputChange('roles', value)}
          />

          <Input
            label="Sectors (comma-separated)"
            placeholder="AI, Machine Learning, Data Science"
            value={formData.sectors}
            onChange={(value) => handleInputChange('sectors', value)}
          />

          <Input
            label="Regions (comma-separated)"
            placeholder="Remote, New York, London"
            value={formData.regions}
            onChange={(value) => handleInputChange('regions', value)}
          />

          <Input
            label="Languages (comma-separated)"
            placeholder="English, German, Japanese"
            value={formData.languages}
            onChange={(value) => handleInputChange('languages', value)}
          />
        </div>

        <div className={styles.textareaGroup}>
          <label className={styles.label}>Bio</label>
          <textarea
            className={styles.textarea}
            placeholder="Brief description of the expert's background and expertise..."
            value={formData.bio}
            onChange={(e) => handleInputChange('bio', e.target.value)}
            rows={4}
          />
        </div>

        <div className={styles.fileGroup}>
          <label className={styles.label}>CV Upload *</label>
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            className={styles.fileInput}
            required
          />
          {formData.file && (
            <p className={styles.fileName}>Selected: {formData.file.name}</p>
          )}
        </div>

        <div className={styles.formActions}>
          {onCancel && (
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
            loading={loading}
          >
            {loading ? 'Submitting...' : 'Submit Expert'}
          </Button>
        </div>
      </form>
    </Card>
  );
}