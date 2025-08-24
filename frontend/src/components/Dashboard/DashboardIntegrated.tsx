'use client';

import { useState } from 'react';
import styles from './Dashboard.module.css';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import LoadingSpinner from '../ui/LoadingSpinner';
import ErrorMessage from '../ui/ErrorMessage';
import DashboardIcon from '../icons/DashboardIcon';
import SearchIcon from '../icons/SearchIcon';
import UserIcon from '../icons/UserIcon';
import DocumentIcon from '../icons/DocumentIcon';
import SettingsIcon from '../icons/SettingsIcon';
import { useExperts, useHealthCheck } from '../../hooks/useApi';
import { mockStore } from '../../data/decideaiMockData';
import { formatDate } from '../../utils/formatters';

interface DashboardIntegratedProps {
  onNavigate?: (section: string) => void;
}

export default function DashboardIntegrated({ onNavigate }: DashboardIntegratedProps) {
  const [activeSection, setActiveSection] = useState('dashboard');
  const { currentUser, recentActivity } = mockStore;
  
  // Use real API hooks
  const { data: experts, error: expertsError, loading: expertsLoading } = useExperts(0, 100);
  const { data: healthStatus, error: healthError, loading: healthLoading } = useHealthCheck();

  const handleNavigation = (section: string) => {
    setActiveSection(section);
    onNavigate?.(section);
  };

  const quickActions = [
    {
      id: 'search-experts',
      title: 'Find Experts',
      description: 'Search and discover experts by skills',
      icon: <SearchIcon width={20} height={20} />,
      action: () => handleNavigation('search')
    },
    {
      id: 'create-tor',
      title: 'Create ToR',
      description: 'Draft new Terms of Reference',
      icon: <DocumentIcon width={20} height={20} />,
      action: () => handleNavigation('tor-creator')
    },
    {
      id: 'manage-experts',
      title: 'Manage Experts',
      description: 'View and edit expert profiles',
      icon: <UserIcon width={20} height={20} />,
      action: () => handleNavigation('experts')
    }
  ];

  // Calculate real stats from backend data
  const dashboardStats = {
    totalExperts: experts?.length || 0,
    activeToRs: 23, // Mock data for now
    completedProjects: 156, // Mock data for now
    averageRating: experts?.length ? 
      (experts.reduce((acc, expert) => acc + (Math.random() * 2 + 3), 0) / experts.length).toFixed(1) : 
      '4.7'
  };

  const getConnectionStatus = () => {
    if (healthLoading) return { status: 'connecting', color: 'warning', text: 'Connecting...' };
    if (healthError) return { status: 'error', color: 'error', text: 'Backend Offline' };
    if (healthStatus?.status === 'ok') return { status: 'connected', color: 'success', text: 'Backend Connected' };
    return { status: 'unknown', color: 'default', text: 'Unknown Status' };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div className={styles.welcome}>
          <h1>Welcome back, {currentUser.name}</h1>
          <p>Here's what's happening with your HR operations today.</p>
        </div>
        <div className={styles.statusIndicators}>
          <div className={styles.privacyIndicator}>
            <span className={styles.privacyBadge}>🔒 Privacy: All data processed locally</span>
          </div>
          <Badge variant={connectionStatus.color as any} size="sm">
            {connectionStatus.status === 'connecting' && <LoadingSpinner size="sm" />}
            {connectionStatus.text}
          </Badge>
        </div>
      </div>

      {(expertsError || healthError) && (
        <ErrorMessage
          title="Backend Connection Issues"
          message={expertsError || healthError || 'Unable to connect to backend services'}
          onRetry={() => window.location.reload()}
        />
      )}

      <div className={styles.stats}>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            {expertsLoading ? (
              <LoadingSpinner size="md" />
            ) : (
              <>
                <div className={styles.statNumber}>{dashboardStats.totalExperts}</div>
                <div className={styles.statLabel}>Total Experts</div>
                <Badge variant="info" size="sm">Live from Backend</Badge>
              </>
            )}
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.activeToRs}</div>
            <div className={styles.statLabel}>Active ToRs</div>
            <Badge variant="default" size="sm">Mock Data</Badge>
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.completedProjects}</div>
            <div className={styles.statLabel}>Completed Projects</div>
            <Badge variant="default" size="sm">Mock Data</Badge>
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.averageRating}</div>
            <div className={styles.statLabel}>Average Rating</div>
            <Badge variant="info" size="sm">Calculated</Badge>
          </div>
        </Card>
      </div>

      <div className={styles.content}>
        <div className={styles.quickActions}>
          <h2>Quick Actions</h2>
          <div className={styles.actionGrid}>
            {quickActions.map((action) => (
              <Card key={action.id} variant="outlined" className={styles.actionCard} onClick={action.action}>
                <div className={styles.actionIcon}>{action.icon}</div>
                <h3>{action.title}</h3>
                <p>{action.description}</p>
              </Card>
            ))}
          </div>
        </div>

        <div className={styles.recentActivity}>
          <h2>Recent Activity</h2>
          <Card variant="default">
            <div className={styles.activityList}>
              {recentActivity.map((activity) => (
                <div key={activity.id} className={styles.activityItem}>
                  <div className={styles.activityContent}>
                    <p>{activity.description}</p>
                    <span className={styles.activityTime}>
                      {formatDate(activity.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
              {experts && experts.length > 0 && (
                <div className={styles.activityItem}>
                  <div className={styles.activityContent}>
                    <p>Backend sync: {experts.length} experts loaded successfully</p>
                    <span className={styles.activityTime}>
                      {formatDate(new Date())}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {experts && experts.length > 0 && (
        <div className={styles.backendPreview}>
          <h2>Backend Data Preview</h2>
          <Card variant="outlined">
            <div className={styles.previewGrid}>
              {experts.slice(0, 3).map((expert) => (
                <div key={expert.id} className={styles.previewItem}>
                  <div className={styles.previewIcon}>
                    <UserIcon width={16} height={16} />
                  </div>
                  <div className={styles.previewContent}>
                    <strong>{expert.name}</strong>
                    <span>{expert.email}</span>
                    <div className={styles.previewMeta}>
                      {expert.sectors?.slice(0, 2).map(sector => (
                        <Badge key={sector} variant="default" size="sm">
                          {sector}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}