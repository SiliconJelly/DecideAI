'use client';

import { useState } from 'react';
import styles from './Sidebar.module.css';
import DashboardIcon from '../icons/DashboardIcon';
import SearchIcon from '../icons/SearchIcon';
import UserIcon from '../icons/UserIcon';
import DocumentIcon from '../icons/DocumentIcon';
import SettingsIcon from '../icons/SettingsIcon';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function Sidebar({ 
  activeSection, 
  onSectionChange, 
  collapsed = false,
  onToggleCollapse 
}: SidebarProps) {
  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <DashboardIcon width={20} height={20} />,
      description: 'Overview and quick actions'
    },
    {
      id: 'search',
      label: 'Find Experts',
      icon: <SearchIcon width={20} height={20} />,
      description: 'Search and discover experts'
    },
    {
      id: 'experts',
      label: 'Manage Experts',
      icon: <UserIcon width={20} height={20} />,
      description: 'Expert profile management'
    },
    {
      id: 'tor-creator',
      label: 'Create ToR',
      icon: <DocumentIcon width={20} height={20} />,
      description: 'Terms of Reference creator'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <SettingsIcon width={20} height={20} />,
      description: 'Privacy and preferences'
    }
  ];

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🤖</span>
          {!collapsed && (
            <div className={styles.logoText}>
              <h1>DecideAI</h1>
              <p>HR Helper</p>
            </div>
          )}
        </div>
        <button 
          className={styles.collapseButton}
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <nav className={styles.navigation}>
        <ul className={styles.navList}>
          {navigationItems.map(item => (
            <li key={item.id}>
              <button
                className={`${styles.navItem} ${activeSection === item.id ? styles.active : ''}`}
                onClick={() => onSectionChange(item.id)}
                title={collapsed ? item.label : undefined}
              >
                <span className={styles.navIcon}>
                  {item.icon}
                </span>
                {!collapsed && (
                  <div className={styles.navContent}>
                    <span className={styles.navLabel}>{item.label}</span>
                    <span className={styles.navDescription}>{item.description}</span>
                  </div>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className={styles.footer}>
        {!collapsed && (
          <div className={styles.privacyIndicator}>
            <div className={styles.privacyIcon}>🔒</div>
            <div className={styles.privacyText}>
              <span>Privacy First</span>
              <small>All data processed locally</small>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}