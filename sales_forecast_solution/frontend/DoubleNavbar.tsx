import React, { useState } from 'react';
import {
  IconSparkles,
  IconGauge,
  IconChartDots,
  IconShieldAlert,
  IconDatabase,
  IconSettings,
  IconCpu,
  IconHome2,
  IconDeviceDesktopAnalytics,
  IconCalendarStats,
  IconUser,
  IconFingerprint,
} from '@tabler/icons-react';
import { Title, Tooltip, UnstyledButton, Badge, Group, Text } from '@mantine/core';
import classes from './DoubleNavbar.module.css';

export interface NavItem {
  icon: React.ComponentType<{ size?: number; stroke?: number }>;
  label: string;
  badge?: string;
  count?: number;
}

export interface SubNavItem {
  label: string;
  tag?: string;
  id?: string;
}

const mainLinksData: NavItem[] = [
  { icon: IconSparkles, label: 'AI Intelligence', badge: 'NEW' },
  { icon: IconGauge, label: 'Forecast & Scenarios' },
  { icon: IconChartDots, label: 'Pipeline Deals' },
  { icon: IconShieldAlert, label: 'Risk & Anomalies', count: 5 },
  { icon: IconDatabase, label: 'Data Warehouse' },
  { icon: IconSettings, label: 'Model Config' },
];

const subLinksMap: Record<string, SubNavItem[]> = {
  'AI Intelligence': [
    { label: 'Deal Win Probability Scorer', tag: 'ML', id: 'scorer' },
    { label: 'Slippage Risk Prediction', id: 'slippage' },
    { label: 'Autonomous Quarantining', id: 'quarantine' },
    { label: 'Calibration Curve (Brier: 0.166)', id: 'calibration' },
    { label: 'Feature Importance & SHAP', id: 'shap' },
  ],
  'Forecast & Scenarios': [
    { label: 'Quarterly Bookings Projection', id: 'projection' },
    { label: 'Base vs Best (+20%) vs Worst (-20%)', id: 'scenarios' },
    { label: 'Point-in-Time Snapshot History', id: 'snapshots' },
    { label: 'Rep Quota Attainment', id: 'quotas' },
  ],
  'Pipeline Deals': [
    { label: 'All Opportunities (fct_opportunities)', id: 'opportunities' },
    { label: 'Enterprise Segment Deals', id: 'enterprise' },
    { label: 'Mid-Market & SMB', id: 'mid_smb' },
    { label: 'Stage Conversion Funnel', id: 'funnel' },
    { label: 'Rep Touchpoint Activities', id: 'activities' },
  ],
  'Risk & Anomalies': [
    { label: 'Quarantined Exceptions Queue', tag: '5 Alerts', id: 'exceptions' },
    { label: 'Stale Deals (>120 Days Inactive)', id: 'stale' },
    { label: 'Invalid Close Dates', id: 'invalid_dates' },
    { label: 'Duplicate Pipeline Records', id: 'duplicates' },
  ],
  'Data Warehouse': [
    { label: 'dim_territories', id: 'dim_territories' },
    { label: 'dim_sales_reps', id: 'dim_sales_reps' },
    { label: 'dim_accounts', id: 'dim_accounts' },
    { label: 'dim_stages', id: 'dim_stages' },
    { label: 'fct_forecast_snapshots', id: 'fct_forecast_snapshots' },
    { label: 'SQLite DB Explorer', id: 'sqlite' },
  ],
  'Model Config': [
    { label: 'HistGradientBoosting Parameters', id: 'hyperparams' },
    { label: 'Snapshot Schedule (AS_OF_DATES)', id: 'dates' },
    { label: 'Currency Conversion Rates', id: 'currencies' },
    { label: 'API & Webhooks', id: 'webhooks' },
  ],
};

interface DoubleNavbarProps {
  activeMain?: string;
  activeSub?: string;
  onSelectMain?: (main: string) => void;
  onSelectSub?: (sub: string, id?: string) => void;
}

export function DoubleNavbar({
  activeMain: propActiveMain,
  activeSub: propActiveSub,
  onSelectMain,
  onSelectSub,
}: DoubleNavbarProps) {
  const [internalMain, setInternalMain] = useState('AI Intelligence');
  const [internalSub, setInternalSub] = useState('Deal Win Probability Scorer');

  const activeMain = propActiveMain || internalMain;
  const activeSub = propActiveSub || internalSub;

  const currentSubLinks = subLinksMap[activeMain] || [];

  const handleMainClick = (label: string) => {
    setInternalMain(label);
    onSelectMain?.(label);
    const firstSub = subLinksMap[label]?.[0];
    if (firstSub) {
      setInternalSub(firstSub.label);
      onSelectSub?.(firstSub.label, firstSub.id);
    }
  };

  const handleSubClick = (sub: SubNavItem) => {
    setInternalSub(sub.label);
    onSelectSub?.(sub.label, sub.id);
  };

  const mainLinks = mainLinksData.map((link) => {
    const isActive = activeMain === link.label;
    return (
      <Tooltip
        label={link.label}
        position="right"
        withArrow
        transitionProps={{ duration: 150 }}
        key={link.label}
      >
        <UnstyledButton
          onClick={() => handleMainClick(link.label)}
          className={classes.mainLink}
          data-active={isActive || undefined}
          aria-label={link.label}
        >
          <link.icon size={22} stroke={1.7} />
          {link.count && <span className={classes.railBadge}>{link.count}</span>}
        </UnstyledButton>
      </Tooltip>
    );
  });

  const subLinks = currentSubLinks.map((item) => {
    const isActive = activeSub === item.label;
    return (
      <a
        className={classes.link}
        data-active={isActive || undefined}
        href="#"
        onClick={(event) => {
          event.preventDefault();
          handleSubClick(item);
        }}
        key={item.label}
      >
        <span className={classes.linkText}>{item.label}</span>
        {item.tag && (
          <Badge
            size="xs"
            variant="filled"
            className={item.tag.includes('Alert') ? classes.tagAlert : classes.tagAi}
          >
            {item.tag}
          </Badge>
        )}
      </a>
    );
  });

  return (
    <nav className={classes.navbar}>
      <div className={classes.wrapper}>
        <aside className={classes.aside}>
          <div className={classes.logo}>
            <div className={classes.aiLogoGlow}>
              <IconCpu size={24} color="#60a5fa" />
            </div>
          </div>
          <div className={classes.mainLinksContainer}>{mainLinks}</div>
        </aside>

        <main className={classes.main}>
          <header className={classes.header}>
            <Group justify="space-between" align="center">
              <Title order={4} className={classes.title}>
                {activeMain}
              </Title>
              <Badge variant="dot" color="teal" size="sm">
                Live
              </Badge>
            </Group>
          </header>

          <div className={classes.linksList}>{subLinks}</div>

          <footer className={classes.aiStatusCard}>
            <div className={classes.pulseDot} />
            <div>
              <Text size="xs" fw={700} c="blue.2">
                Predictive Engine
              </Text>
              <Text size="10px" c="dimmed">
                HistGradientBoosting • v2.4
              </Text>
            </div>
          </footer>
        </main>
      </div>
    </nav>
  );
}
