import { Component, inject, signal } from '@angular/core';
import { UpperCasePipe } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { I18nService } from '../../i18n/i18n.service';
import { TranslatePipe } from '../../i18n/translate.pipe';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, TranslatePipe, UpperCasePipe],
  template: `
    <header class="header" [class.scrolled]="scrolled()">
      <div class="container header-inner">
        <a class="logo" routerLink="/">
          <svg class="logo-icon" width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="24" height="20" rx="4" stroke="currentColor" stroke-width="2"/><polyline points="8,18 12,12 16,15 22,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="22" cy="8" r="2" fill="currentColor"/></svg>
          <span class="logo-text">AdFlow<span class="logo-accent">Pro</span></span>
        </a>

        <nav class="nav" [class.open]="menuOpen()">
          <a href="#hero" (click)="closeMenu()">{{ 'nav.home' | translate }}</a>
          <a href="#services" (click)="closeMenu()">{{ 'nav.services' | translate }}</a>
          <a href="#about" (click)="closeMenu()">{{ 'nav.about' | translate }}</a>
          <a href="#contact" (click)="closeMenu()">{{ 'nav.contact' | translate }}</a>
          <a routerLink="/dashboard" (click)="closeMenu()">{{ 'nav.dashboard' | translate }}</a>

          <div class="lang-switcher">
            @for (lang of i18n.supportedLanguages; track lang.code) {
              <button
                class="lang-btn"
                [class.active]="lang.code === i18n.lang()"
                (click)="switchLang(lang.code)"
              >{{ lang.flag }} {{ lang.code | uppercase }}</button>
            }
          </div>

          <a href="#contact" class="btn btn-accent nav-cta" (click)="closeMenu()">{{ 'nav.getQuote' | translate }}</a>
        </nav>

        <button class="menu-toggle" (click)="toggleMenu()" [attr.aria-label]="'Toggle menu'">
          <span [class.open]="menuOpen()"></span>
        </button>
      </div>
    </header>
  `,
  styles: [`
    .header {
      position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
      background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(99, 102, 241, 0.08);
      transition: var(--transition);
    }
    .header.scrolled { background: rgba(15, 23, 42, 0.95); border-bottom-color: rgba(99, 102, 241, 0.15); box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
    .header-inner {
      display: flex; align-items: center; justify-content: space-between;
      height: 72px;
    }
    .logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.25rem; color: white; }
    .logo-icon { color: #a5b4fc; }
    .logo-accent { color: #06b6d4; }
    .nav {
      display: flex; align-items: center; gap: 28px;
      a { font-weight: 500; font-size: 0.95rem; color: #cbd5e1; transition: var(--transition); &:hover { color: white; } }
    }
    .lang-switcher { display: flex; gap: 4px; }
    .lang-btn {
      background: none; border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 6px;
      padding: 4px 8px; font-size: 0.8rem; cursor: pointer; transition: var(--transition); color: #94a3b8;
      &.active { background: var(--primary); color: white; border-color: var(--primary); }
      &:hover:not(.active) { border-color: #a5b4fc; color: white; }
    }
    .nav-cta { padding: 10px 24px; font-size: 0.9rem; }
    .menu-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
    .menu-toggle span,
    .menu-toggle span::before,
    .menu-toggle span::after {
      display: block; width: 24px; height: 2px; background: white;
      transition: var(--transition); position: relative;
    }
    .menu-toggle span::before, .menu-toggle span::after {
      content: ''; position: absolute; left: 0;
    }
    .menu-toggle span::before { top: -7px; }
    .menu-toggle span::after { top: 7px; }
    .menu-toggle span.open { background: transparent; }
    .menu-toggle span.open::before { top: 0; transform: rotate(45deg); }
    .menu-toggle span.open::after { top: 0; transform: rotate(-45deg); }

    @media (max-width: 768px) {
      .menu-toggle { display: block; }
      .nav {
        position: fixed; top: 72px; left: 0; right: 0; bottom: 0;
        background: #0f172a; flex-direction: column; padding: 32px 24px;
        gap: 24px; transform: translateX(100%); transition: var(--transition);
        &.open { transform: translateX(0); }
        a { font-size: 1.1rem; color: #e2e8f0; }
      }
      .lang-switcher { margin-top: 8px; }
      .nav-cta { width: 100%; text-align: center; }
    }
  `],
})
export class HeaderComponent {
  i18n = inject(I18nService);
  private router = inject(Router);

  scrolled = signal(false);
  menuOpen = signal(false);

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', () => {
        this.scrolled.set(window.scrollY > 20);
      });
    }
  }

  switchLang(code: string): void {
    this.i18n.setLanguage(code);
    this.router.navigate(['/' + code]);
    this.closeMenu();
  }

  toggleMenu(): void {
    this.menuOpen.update(v => !v);
  }

  closeMenu(): void {
    this.menuOpen.set(false);
  }
}
