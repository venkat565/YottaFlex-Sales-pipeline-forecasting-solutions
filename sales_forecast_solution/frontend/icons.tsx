import React from 'react';

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  size?: number | string;
  stroke?: number | string;
  color?: string;
  className?: string;
}

const defaultProps = {
  size: 22,
  stroke: 1.5,
  color: 'currentColor',
};

// 1. Sparkles / AI Intelligence
export function IconSparkles({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 3l1.912 4.912L18.824 9.824 13.912 11.736 12 16.648l-1.912-4.912L5.176 9.824l4.912-1.912z" />
      <path d="M19 15l.956 2.456L22.412 18.412 19.956 19.368 19 21.824l-.956-2.456-2.456-.956 2.456-.956z" />
      <path d="M5 17l.637 1.637L7.274 19.274 5.637 19.911 5 21.548l-.637-1.637-1.637-.637 1.637-.637z" />
    </svg>
  );
}

// 2. Gauge / Dashboard Forecast
export function IconGauge({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
      <path d="M14 8l-2 4" />
      <path d="M7 12a5 5 0 0 1 5 -5" />
      <path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    </svg>
  );
}

// 3. Chart Dots / Pipeline Analytics
export function IconChartDots({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M3 3v18h18" />
      <circle cx="9" cy="9" r="2" />
      <circle cx="19" cy="7" r="2" />
      <circle cx="14" cy="15" r="2" />
      <path d="M10.1 10.5l2.8 3" />
      <path d="M15.1 13.5l2.8 -5" />
    </svg>
  );
}

// 4. Shield Alert / Data Quality
export function IconShieldAlert({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 3a12 12 0 0 0 8.5 3a12 12 0 0 1 -8.5 15a12 12 0 0 1 -8.5 -15a12 12 0 0 0 8.5 -3" />
      <path d="M12 8v4" />
      <path d="M12 16h.01" />
    </svg>
  );
}

// 5. Database / Warehouse & Kimball Schema
export function IconDatabase({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <ellipse cx="12" cy="6" rx="8" ry="3" />
      <path d="M4 6v6a8 3 0 0 0 16 0v-6" />
      <path d="M4 12v6a8 3 0 0 0 16 0v-6" />
    </svg>
  );
}

// 6. Settings
export function IconSettings({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 0 0-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 0 0-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 0 0-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 0 0 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

// 7. CPU / Machine Learning Engine
export function IconCpu({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="5" y="5" width="14" height="14" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <path d="M9 1v4" />
      <path d="M15 1v4" />
      <path d="M9 19v4" />
      <path d="M15 19v4" />
      <path d="M1 9h4" />
      <path d="M1 15h4" />
      <path d="M19 9h4" />
      <path d="M19 15h4" />
    </svg>
  );
}

// 8. Home2
export function IconHome2({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M5 12l-2 0l9 -9l9 9l-2 0" />
      <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7" />
      <path d="M10 12h4v4h-4z" />
    </svg>
  );
}

// 9. Device Desktop Analytics
export function IconDeviceDesktopAnalytics({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="3" y="4" width="18" height="12" rx="1" />
      <path d="M7 20h10" />
      <path d="M9 16v4" />
      <path d="M15 16v4" />
      <path d="M9 12v-2" />
      <path d="M12 12v-1" />
      <path d="M15 12v-3" />
      <path d="M12 12v.01" />
    </svg>
  );
}

// 10. Calendar Stats
export function IconCalendarStats({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="4" y="5" width="16" height="16" rx="2" />
      <path d="M16 3v4" />
      <path d="M8 3v4" />
      <path d="M4 11h16" />
      <path d="M11 15h1" />
      <path d="M12 15v3" />
    </svg>
  );
}

// 11. User
export function IconUser({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
      <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
    </svg>
  );
}

// 12. Fingerprint
export function IconFingerprint({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M18.9 7a8 8 0 0 0 -13.8 0" />
      <path d="M4 11a12 12 0 0 1 16 0" />
      <path d="M8 15a4 4 0 0 1 8 0" />
      <path d="M12 15v6" />
      <path d="M9 21v-3a3 3 0 0 1 6 0v3" />
    </svg>
  );
}

// 13. Bolt / Power
export function IconBolt({ size = defaultProps.size, stroke = defaultProps.stroke, color = defaultProps.color, ...props }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M13 2L4 14h7l-1 8 9-12h-7z" />
    </svg>
  );
}

// Aliases for convenience
export const IconHome = IconHome2;
export const IconDashboard = IconGauge;
export const IconAnalytics = IconDeviceDesktopAnalytics;
export const IconReleases = IconCalendarStats;
export const IconAccount = IconUser;
export const IconSecurity = IconFingerprint;
export const IconAi = IconSparkles;
export const IconPipeline = IconChartDots;
export const IconRisk = IconShieldAlert;
export const IconWarehouse = IconDatabase;
export const IconModel = IconCpu;
