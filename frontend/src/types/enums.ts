// Enums for DecideAI HR System

export enum UserRole {
  ADMIN = 'admin',
  HR_MANAGER = 'hr_manager',
  STAFF = 'staff',
  VIEWER = 'viewer'
}

export enum ExpertStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending'
}

export enum AvailabilityStatus {
  AVAILABLE = 'available',
  BUSY = 'busy',
  UNAVAILABLE = 'unavailable'
}

export enum Language {
  GERMAN = 'german',
  JAPANESE = 'japanese',
  ENGLISH = 'english'
}

export enum ToRStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived'
}

export enum ActionType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  VIEW = 'view',
  EXPORT = 'export'
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error'
}

export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc'
}

export enum ViewMode {
  GRID = 'grid',
  LIST = 'list',
  TABLE = 'table'
}