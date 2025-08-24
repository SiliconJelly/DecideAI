'use client';

import { useState } from 'react';
import styles from './Dashboard.module.css';
import Card from '../ui/Card';
import Button from '../ui/Button';
import DashboardIcon from '../icons/DashboardIcon';
import SearchIcon from '../icons/SearchIcon';
import UserIcon from '../icons/UserIcon';
import DocumentIcon from '../icons/DocumentIcon';
import SettingsIcon from '../icons/SettingsIcon';
import { mockStore, mockQuery } from '../../data/decideaiMockData';
import { formatDate } from '../../utils/formatters';

interface DashboardProps {
  onNavigate?: (section: string) => void;
}

export default function Dashboard({ onNavigate }: DashboardProps) {
  const [activeSection, setActiveSection] = useState('dashboard');
  const { currentUser, recentActivity } = mockStore;
  const { dashboardStats } = mockQuery;

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

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div className={styles.welcome}>
          <h1>Welcome back, {currentUser.name}</h1>
          <p>Here's what's happening with your HR operations today.</p>
        </div>
        <div className={styles.privacyIndicator}>
          <span className={styles.privacyBadge}>🔒 Privacy: All data processed locally</span>
        </div>
      </div>

      <div className={styles.stats}>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.totalExperts}</div>
            <div className={styles.statLabel}>Total Experts</div>
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.activeToRs}</div>
            <div className={styles.statLabel}>Active ToRs</div>
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.completedProjects}</div>
            <div className={styles.statLabel}>Completed Projects</div>
          </div>
        </Card>
        <Card variant="elevated" className={styles.statCard}>
          <div className={styles.statContent}>
            <div className={styles.statNumber}>{dashboardStats.averageRating}</div>
            <div className={styles.statLabel}>Average Rating</div>
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
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}