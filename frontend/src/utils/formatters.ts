import { Language, AvailabilityStatus, ExpertStatus, ToRStatus, UserRole } from '../types/enums';

export const formatExperienceYears = (years: number): string => {
  if (years === 0) return 'Less than 1 year';
  if (years === 1) return '1 year';
  return `${years} years`;
};

export const formatLanguage = (language: Language): string => {
  const languageMap = {
    [Language.GERMAN]: 'Deutsch',
    [Language.JAPANESE]: '日本語',
    [Language.ENGLISH]: 'English'
  };
  return languageMap[language] || language;
};

export const formatAvailabilityStatus = (status: AvailabilityStatus): string => {
  const statusMap = {
    [AvailabilityStatus.AVAILABLE]: 'Available',
    [AvailabilityStatus.BUSY]: 'Currently Busy',
    [AvailabilityStatus.UNAVAILABLE]: 'Unavailable'
  };
  return statusMap[status] || status;
};

export const formatExpertStatus = (status: ExpertStatus): string => {
  const statusMap = {
    [ExpertStatus.ACTIVE]: 'Active',
    [ExpertStatus.INACTIVE]: 'Inactive',
    [ExpertStatus.PENDING]: 'Pending Review'
  };
  return statusMap[status] || status;
};

export const formatToRStatus = (status: ToRStatus): string => {
  const statusMap = {
    [ToRStatus.DRAFT]: 'Draft',
    [ToRStatus.PUBLISHED]: 'Published',
    [ToRStatus.ARCHIVED]: 'Archived'
  };
  return statusMap[status] || status;
};

export const formatUserRole = (role: UserRole): string => {
  const roleMap = {
    [UserRole.ADMIN]: 'Administrator',
    [UserRole.HR_MANAGER]: 'HR Manager',
    [UserRole.STAFF]: 'Staff Member',
    [UserRole.VIEWER]: 'Viewer'
  };
  return roleMap[role] || role;
};

export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

export const formatDateTime = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

export const formatRating = (rating: number): string => {
  return `${rating.toFixed(1)}/5.0`;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};