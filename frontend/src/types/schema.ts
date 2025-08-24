import { UserRole, ExpertStatus, AvailabilityStatus, Language, ToRStatus } from './enums';

// Props types (data passed to components)
export interface DashboardProps {
  user: UserInfo;
  stats: DashboardStats;
  recentActivity: ActivityItem[];
  quickActions: QuickAction[];
}

export interface ExpertSearchProps {
  initialResults: ExpertSearchResult[];
  filters: FilterOptions;
  searchQuery: string;
  totalCount: number;
}

export interface ExpertProfileProps {
  expert: ExpertProfile;
  ratings: Rating[];
  engagements: Engagement[];
  isEditable: boolean;
}

export interface ToRCreatorProps {
  initialData?: Partial<ToRDraft>;
  availableSkills: string[];
  templates: ToRTemplate[];
}

// Store types (global state data)
export interface StoreTypes {
  user: UserInfo;
  experts: ExpertProfile[];
  torDrafts: ToRDraft[];
  searchFilters: FilterState;
  ui: UIState;
  cache: CacheState;
}

export interface UserInfo {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  preferences: UserPreferences;
}

export interface ExpertProfile {
  id: string;
  name: string;
  email: string;
  phone?: string;
  status: ExpertStatus;
  availability: AvailabilityStatus;
  yearsExperience: number;
  rating: number;
  languages: Language[];
  sectors: string[];
  regions: string[];
  roles: string[];
  lastActive: Date;
}

export interface ToRDraft {
  id: string;
  title: string;
  status: ToRStatus;
  createdAt: Date;
  updatedAt: Date;
  requiredSkills: string[];
  estimatedDuration: string;
  budget: string;
}

// Query types (API response data)
export interface QueryTypes {
  searchResults: ExpertSearchResult[];
  dashboardStats: DashboardStats;
  expertDetails: ExpertProfile;
  torList: ToRDraft[];
}

export interface ExpertSearchResult {
  id: string;
  matchScore: number;
  relevantSkills: string[];
  availability: string;
}

export interface DashboardStats {
  totalExperts: number;
  activeToRs: number;
  completedProjects: number;
  averageRating: number;
}

export interface UserPreferences {
  language: Language;
  theme: string;
  notifications: boolean;
}

export interface ActivityItem {
  id: string;
  type: string;
  description: string;
  timestamp: Date;
}

export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  href: string;
}

export interface FilterOptions {
  skills: string[];
  sectors: string[];
  regions: string[];
  languages: Language[];
  availability: AvailabilityStatus[];
  experienceMin: number;
  experienceMax: number;
}

export interface FilterState {
  active: FilterOptions;
  saved: SavedFilter[];
}

export interface SavedFilter {
  id: string;
  name: string;
  filters: FilterOptions;
}

export interface UIState {
  sidebarOpen: boolean;
  currentView: string;
  loading: boolean;
  notifications: Notification[];
}

export interface CacheState {
  experts: Record<string, ExpertProfile>;
  searchResults: Record<string, ExpertSearchResult[]>;
  lastUpdated: Record<string, Date>;
}

export interface Rating {
  id: string;
  rating: number;
  comment: string;
  createdAt: Date;
  createdBy: string;
}

export interface Engagement {
  id: string;
  projectTitle: string;
  duration: string;
  rating: number;
  completedAt: Date;
}

export interface ToRTemplate {
  id: string;
  name: string;
  description: string;
  template: Partial<ToRDraft>;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}