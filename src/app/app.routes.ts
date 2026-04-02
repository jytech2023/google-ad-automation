import { Routes } from '@angular/router';
import { SUPPORTED_LANGUAGES } from './i18n/translations';
import { authGuard } from './auth/auth.guard';

const validLangs = SUPPORTED_LANGUAGES.map(l => l.code);

const dashboardChildren: Routes = [
  { path: '', loadComponent: () => import('./pages/dashboard/overview/overview.component').then(m => m.OverviewComponent) },
  { path: 'campaigns', loadComponent: () => import('./pages/dashboard/campaigns/campaigns.component').then(m => m.CampaignsComponent) },
  { path: 'keywords', loadComponent: () => import('./pages/dashboard/keywords/keywords.component').then(m => m.KeywordsComponent) },
  { path: 'ad-copy', loadComponent: () => import('./pages/dashboard/ad-copy/ad-copy.component').then(m => m.AdCopyComponent) },
  { path: 'billing', loadComponent: () => import('./pages/dashboard/billing/billing.component').then(m => m.BillingComponent) },
  { path: 'reports', loadComponent: () => import('./pages/dashboard/reports/reports.component').then(m => m.ReportsComponent) },
  { path: 'settings', loadComponent: () => import('./pages/dashboard/settings/settings.component').then(m => m.SettingsComponent) },
];

export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard],
    children: dashboardChildren,
  },
  {
    path: ':lang/dashboard',
    canMatch: [(_route: any, segments: any) => validLangs.includes(segments[0]?.path)],
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard],
    children: dashboardChildren,
  },
  {
    path: ':lang',
    canMatch: [(_route: any, segments: any) => validLangs.includes(segments[0]?.path)],
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent),
  },
  {
    path: '',
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent),
  },
  { path: '**', redirectTo: '' },
];
