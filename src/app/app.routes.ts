import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: ':lang',
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent),
  },
  {
    path: '',
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent),
  },
  { path: '**', redirectTo: '' },
];
