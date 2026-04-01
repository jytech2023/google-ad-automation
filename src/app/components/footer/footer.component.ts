import { Component, inject } from '@angular/core';
import { TranslatePipe } from '../../i18n/translate.pipe';
import { I18nService } from '../../i18n/i18n.service';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [TranslatePipe],
  template: `
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="logo">
              <span class="logo-icon">&#9830;</span>
              <span>GlobalTrade<span class="accent">Pro</span></span>
            </div>
            <p>{{ 'footer.desc' | translate }}</p>
          </div>

          <div class="footer-links">
            <h4>{{ 'footer.quickLinks' | translate }}</h4>
            <a href="#hero">{{ 'nav.home' | translate }}</a>
            <a href="#services">{{ 'nav.services' | translate }}</a>
            <a href="#about">{{ 'nav.about' | translate }}</a>
            <a href="#contact">{{ 'nav.contact' | translate }}</a>
          </div>

          <div class="footer-links">
            <h4>{{ 'footer.services' | translate }}</h4>
            <a>{{ 'services.import.title' | translate }}</a>
            <a>{{ 'services.sourcing.title' | translate }}</a>
            <a>{{ 'services.logistics.title' | translate }}</a>
            <a>{{ 'services.consulting.title' | translate }}</a>
          </div>

          <div class="footer-links">
            <h4>{{ 'footer.legal' | translate }}</h4>
            <a>{{ 'footer.privacy' | translate }}</a>
            <a>{{ 'footer.terms' | translate }}</a>
            <a>{{ 'footer.cookie' | translate }}</a>
          </div>
        </div>

        <div class="footer-bottom">
          <p>{{ 'footer.copyright' | translate }}</p>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      background: var(--bg-dark); color: #d1d5db; padding: 64px 0 0;
    }
    .footer-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      gap: 48px;
    }
    .footer-brand {
      .logo {
        display: flex; align-items: center; gap: 8px;
        font-weight: 800; font-size: 1.25rem; color: white; margin-bottom: 16px;
        .logo-icon { color: var(--accent); }
        .accent { color: var(--accent); }
      }
      p { font-size: 0.95rem; line-height: 1.7; }
    }
    .footer-links {
      display: flex; flex-direction: column; gap: 12px;
      h4 { color: white; font-size: 1rem; margin-bottom: 4px; }
      a { font-size: 0.9rem; transition: var(--transition); cursor: pointer;
        &:hover { color: white; }
      }
    }
    .footer-bottom {
      border-top: 1px solid #374151; margin-top: 48px; padding: 24px 0;
      text-align: center; font-size: 0.85rem;
    }
    @media (max-width: 768px) {
      .footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
      .footer-brand { grid-column: 1 / -1; }
    }
    @media (max-width: 480px) {
      .footer-grid { grid-template-columns: 1fr; }
    }
  `],
})
export class FooterComponent {}
