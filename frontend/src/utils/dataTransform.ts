// Data transformation utilities between frontend and backend formats

import { ExpertProfile } from '../types/schema';
import { BackendExpert } from '../services/api';
import { ExpertStatus, AvailabilityStatus, Language } from '../types/enums';

export function transformBackendExpertToFrontend(backendExpert: BackendExpert): ExpertProfile {
  return {
    id: backendExpert.id,
    name: backendExpert.name,
    email: backendExpert.email,
    phone: backendExpert.phone,
    status: backendExpert.is_active ? ExpertStatus.ACTIVE : ExpertStatus.INACTIVE,
    availability: AvailabilityStatus.AVAILABLE, // Default, backend doesn't have this field yet
    yearsExperience: backendExpert.years_experience || 0,
    rating: 4.5, // Default rating, backend doesn't have this field yet
    languages: transformLanguageStringsToEnums(backendExpert.languages || []),
    sectors: backendExpert.sectors || [],
    regions: backendExpert.regions || [],
    roles: backendExpert.roles || [],
    lastActive: new Date(backendExpert.updated_at)
  };
}

export function transformFrontendExpertToBackend(frontendExpert: Partial<ExpertProfile>) {
  return {
    name: frontendExpert.name,
    email: frontendExpert.email,
    phone: frontendExpert.phone,
    bio: '', // Frontend doesn't have bio field yet
    roles: frontendExpert.roles,
    sectors: frontendExpert.sectors,
    regions: frontendExpert.regions,
    languages: frontendExpert.languages?.map(lang => lang.toString()),
    years_experience: frontendExpert.yearsExperience
  };
}

function transformLanguageStringsToEnums(languages: string[]): Language[] {
  return languages.map(lang => {
    const lowerLang = lang.toLowerCase();
    switch (lowerLang) {
      case 'german':
      case 'deutsch':
        return Language.GERMAN;
      case 'japanese':
      case '日本語':
        return Language.JAPANESE;
      case 'english':
      default:
        return Language.ENGLISH;
    }
  });
}

export function createMockAvailabilityStatus(): AvailabilityStatus {
  const statuses = [AvailabilityStatus.AVAILABLE, AvailabilityStatus.BUSY, AvailabilityStatus.UNAVAILABLE];
  return statuses[Math.floor(Math.random() * statuses.length)];
}

export function createMockRating(): number {
  return Math.round((Math.random() * 2 + 3) * 10) / 10; // Random rating between 3.0 and 5.0
}

export function handleApiError(error: any): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.detail) {
    return error.detail;
  }
  
  return 'An unexpected error occurred';
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateExpertData(data: any): string[] {
  const errors: string[] = [];
  
  if (!data.name?.trim()) {
    errors.push('Name is required');
  }
  
  if (!data.email?.trim()) {
    errors.push('Email is required');
  } else if (!isValidEmail(data.email)) {
    errors.push('Invalid email format');
  }
  
  if (data.years_experience && (data.years_experience < 0 || data.years_experience > 50)) {
    errors.push('Years of experience must be between 0 and 50');
  }
  
  return errors;
}