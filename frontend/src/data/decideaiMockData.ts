import { UserRole, ExpertStatus, AvailabilityStatus, Language, ToRStatus } from '../types/enums';

// Data for global state store
export const mockStore = {
  currentUser: {
    id: "user-1" as const,
    name: "Sarah Mueller" as const,
    email: "sarah.mueller@university.de" as const,
    role: UserRole.HR_MANAGER,
    preferences: {
      language: Language.ENGLISH,
      theme: "light" as const,
      notifications: true
    }
  },
  experts: [
    {
      id: "expert-1" as const,
      name: "Dr. Hiroshi Tanaka" as const,
      email: "h.tanaka@research.jp" as const,
      phone: "+81-3-1234-5678" as const,
      status: ExpertStatus.ACTIVE,
      availability: AvailabilityStatus.AVAILABLE,
      yearsExperience: 12,
      rating: 4.8,
      languages: [Language.JAPANESE, Language.ENGLISH],
      sectors: ["Artificial Intelligence" as const, "Machine Learning" as const, "Data Science" as const],
      regions: ["Tokyo" as const, "Osaka" as const, "Remote" as const],
      roles: ["Senior AI Researcher" as const, "Technical Consultant" as const],
      lastActive: new Date('2024-01-15T10:30:00Z')
    },
    {
      id: "expert-2" as const,
      name: "Prof. Anna Schmidt" as const,
      email: "a.schmidt@tu-berlin.de" as const,
      phone: "+49-30-1234-5678" as const,
      status: ExpertStatus.ACTIVE,
      availability: AvailabilityStatus.BUSY,
      yearsExperience: 15,
      rating: 4.9,
      languages: [Language.GERMAN, Language.ENGLISH],
      sectors: ["Renewable Energy" as const, "Engineering" as const, "Sustainability" as const],
      regions: ["Berlin" as const, "Munich" as const, "Remote" as const],
      roles: ["Professor" as const, "Research Director" as const],
      lastActive: new Date('2024-01-14T14:20:00Z')
    }
  ],
  torDrafts: [
    {
      id: "tor-1" as const,
      title: "AI Ethics Research Consultant" as const,
      status: ToRStatus.DRAFT,
      createdAt: new Date('2024-01-10T09:00:00Z'),
      updatedAt: new Date('2024-01-12T16:30:00Z'),
      requiredSkills: ["AI Ethics" as const, "Policy Development" as const, "Research" as const],
      estimatedDuration: "3 months" as const,
      budget: "€15,000" as const
    }
  ],
  recentActivity: [
    {
      id: "activity-1" as const,
      type: "expert_matched" as const,
      description: "Dr. Hiroshi Tanaka matched to AI Ethics project" as const,
      timestamp: new Date('2024-01-15T11:00:00Z')
    },
    {
      id: "activity-2" as const,
      type: "tor_created" as const,
      description: "New ToR created: AI Ethics Research Consultant" as const,
      timestamp: new Date('2024-01-10T09:00:00Z')
    }
  ]
};

// Data returned by API queries
export const mockQuery = {
  searchResults: [
    {
      id: "expert-1" as const,
      matchScore: 0.95,
      relevantSkills: ["AI" as const, "Machine Learning" as const],
      availability: "Available immediately" as const
    }
  ],
  dashboardStats: {
    totalExperts: 1247,
    activeToRs: 23,
    completedProjects: 156,
    averageRating: 4.7
  }
};

// Data passed as props to the root component
export const mockRootProps = {
  initialData: {
    user: mockStore.currentUser,
    expertCount: 1247,
    activeProjects: 23
  },
  config: {
    enableOfflineMode: true,
    cacheTimeout: 300000,
    maxSearchResults: 50
  }
};