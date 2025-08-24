'use client';

import { useState } from 'react';
import styles from './DecideAI.module.css';
import Sidebar from '../components/Navigation/Sidebar';
import DashboardIntegrated from '../components/Dashboard/DashboardIntegrated';
import ExpertSearchIntegrated from '../components/ExpertSearch/ExpertSearchIntegrated';
import { mockRootProps } from '../data/decideaiMockData';

export default function DecideAIApp() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
  };

  const handleToggleCollapse = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardIntegrated onNavigate={handleSectionChange} />;
      case 'search':
        return <ExpertSearchIntegrated />;
      case 'experts':
        return (
          <div className={styles.placeholder}>
            <h1>Expert Management</h1>
            <p>Comprehensive expert profile management interface coming soon.</p>
          </div>
        );
      case 'tor-creator':
        return (
          <div className={styles.placeholder}>
            <h1>Terms of Reference Creator</h1>
            <p>Step-by-step ToR creation wizard coming soon.</p>
          </div>
        );
      case 'settings':
        return (
          <div className={styles.placeholder}>
            <h1>Settings & Privacy</h1>
            <p>GDPR-compliant privacy controls and user preferences coming soon.</p>
            <div className={styles.apiInfo}>
              <h3>Backend Integration Status</h3>
              <ul>
                <li>✅ Expert Search - Connected to FastAPI backend</li>
                <li>✅ Dashboard Stats - Real-time data from backend</li>
                <li>✅ Health Check - Backend connectivity monitoring</li>
                <li>🔄 Authentication - Ready for implementation</li>
                <li>🔄 ToR Management - API endpoints available</li>
              </ul>
            </div>
          </div>
        );
      default:
        return <DashboardIntegrated onNavigate={handleSectionChange} />;
    }
  };

  return (
    <div className={styles.app}>
      <Sidebar
        activeSection={activeSection}
        onSectionChange={handleSectionChange}
        collapsed={sidebarCollapsed}
        onToggleCollapse={handleToggleCollapse}
      />
      
      <main className={`${styles.main} ${sidebarCollapsed ? styles.collapsed : ''}`}>
        <div className={styles.content}>
          {renderContent()}
        </div>
      </main>
    </div>
  );
}