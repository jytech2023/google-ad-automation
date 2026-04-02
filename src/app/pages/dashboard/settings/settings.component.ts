import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { I18nService } from '../../../i18n/i18n.service';
import { AdsDataService } from '../ads-data.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [FormsModule, TranslatePipe],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent {
  i18n = inject(I18nService);
  ads = inject(AdsDataService);

  saved = signal(false);
  apiStatus = signal<'connected' | 'demo'>('demo');

  settings = {
    companyName: 'JY Tech LLC',
    email: '',
    customerId: '298-211-3538',
    timezone: 'America/Los_Angeles',
    currency: 'USD',
    notifications: true,
    weeklyReport: true,
    budgetAlerts: true,
  };

  constructor() {
    this.apiStatus.set(this.ads.dataSource() === 'google_ads_api' ? 'connected' : 'demo');
  }

  save(): void {
    this.saved.set(true);
    setTimeout(() => this.saved.set(false), 3000);
  }

  testConnection(): void {
    this.ads.refresh();
  }
}
