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
          <span class="logo-icon">&#9830;</span>
          <span class="logo-text">GlobalTrade<span class="logo-accent">Pro</span></span>
        </a>

        <nav class="nav" [class.open]="menuOpen()">
          <a href="#hero" (click)="closeMenu()">{{ 'nav.home' | translate }}</a>
          <a href="#services" (click)="closeMenu()">{{ 'nav.services' | translate }}</a>
          <a href="#about" (click)="closeMenu()">{{ 'nav.about' | translate }}</a>
          <a href="#contact" (click)="closeMenu()">{{ 'nav.contact' | translate }}</a>

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
      background: rgba(255,255,255,0.95); backdrop-filter: blur(12px);
      border-bottom: 1px solid transparent;
      transition: var(--transition);
    }
    .header.scrolled { border-bottom-color: var(--border); box-shadow: var(--shadow); }
    .header-inner {
      display: flex; align-items: center; justify-content: space-between;
      height: 72px;
    }
    .logo { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 1.25rem; }
    .logo-icon { color: var(--primary); font-size: 1.5rem; }
    .logo-accent { color: var(--primary); }
    .nav {
      display: flex; align-items: center; gap: 28px;
      a { font-weight: 500; font-size: 0.95rem; transition: var(--transition); &:hover { color: var(--primary); } }
    }
    .lang-switcher { display: flex; gap: 4px; }
    .lang-btn {
      background: none; border: 1px solid var(--border); border-radius: 6px;
      padding: 4px 8px; font-size: 0.8rem; cursor: pointer; transition: var(--transition);
      &.active { background: var(--primary); color: white; border-color: var(--primary); }
      &:hover:not(.active) { border-color: var(--primary); }
    }
    .nav-cta { padding: 10px 24px; font-size: 0.9rem; }
    .menu-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
    .menu-toggle span,
    .menu-toggle span::before,
    .menu-toggle span::after {
      display: block; width: 24px; height: 2px; background: var(--text);
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
        background: white; flex-direction: column; padding: 32px 24px;
        gap: 24px; transform: translateX(100%); transition: var(--transition);
        &.open { transform: translateX(0); }
        a { font-size: 1.1rem; }
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
