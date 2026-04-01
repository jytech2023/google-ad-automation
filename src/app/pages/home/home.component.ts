import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { HeaderComponent } from '../../components/header/header.component';
import { FooterComponent } from '../../components/footer/footer.component';
import { I18nService } from '../../i18n/i18n.service';
import { TranslatePipe } from '../../i18n/translate.pipe';

declare function gtag(...args: unknown[]): void;

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FormsModule, HeaderComponent, FooterComponent, TranslatePipe],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  i18n = inject(I18nService);
  private route = inject(ActivatedRoute);
  private http = inject(HttpClient);

  contactForm = { name: '', email: '', company: '', message: '' };
  formStatus: 'idle' | 'sending' | 'success' | 'error' = 'idle';

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.i18n.initFromUrl(params.get('lang'));
    });
  }

  submitContact(): void {
    if (!this.contactForm.name || !this.contactForm.email || !this.contactForm.message) return;

    this.formStatus = 'sending';
    this.http.post('/api/contact', this.contactForm).subscribe({
      next: () => {
        this.formStatus = 'success';
        this.contactForm = { name: '', email: '', company: '', message: '' };
        // Fire Google Ads conversion
        if (typeof gtag !== 'undefined') {
          gtag('event', 'conversion', {
            send_to: 'AW-XXXXXXXXX/CONVERSION_LABEL',
            value: 1.0,
            currency: 'USD',
          });
        }
      },
      error: () => {
        this.formStatus = 'error';
      },
    });
  }
}
