import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService, Campaign } from '../ads-data.service';

@Component({
  selector: 'app-campaigns',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe, FormsModule],
  templateUrl: './campaigns.component.html',
  styleUrl: './campaigns.component.scss',
})
export class CampaignsComponent {
  ads = inject(AdsDataService);
  private http = inject(HttpClient);

  filter = signal<'all' | 'active' | 'paused' | 'ended'>('all');
  selectedCampaign = signal<Campaign | null>(null);
  actionLoading = signal<string | null>(null);
  actionResult = signal<{ name: string; success: boolean; message: string } | null>(null);

  showCreateForm = signal(false);
  createLoading = signal(false);
  hasBilling = signal<boolean | null>(null);
  newCampaign = { name: '', dailyBudget: 10, channel: 'SEARCH' };

  constructor() {
    this.checkBilling();
  }

  private checkBilling(): void {
    this.http.get<{ hasBilling: boolean }>('/api/billing-status').subscribe({
      next: (res) => this.hasBilling.set(res.hasBilling),
      error: () => this.hasBilling.set(false),
    });
  }

  get filteredCampaigns(): Campaign[] {
    const f = this.filter();
    if (f === 'all') return this.ads.campaigns();
    return this.ads.campaigns().filter(c => c.status === f);
  }

  setFilter(f: 'all' | 'active' | 'paused' | 'ended'): void {
    this.filter.set(f);
  }

  selectCampaign(c: Campaign): void {
    this.selectedCampaign.set(this.selectedCampaign()?.name === c.name ? null : c);
  }

  countByStatus(status: string): number {
    return this.ads.campaigns().filter(c => c.status === status).length;
  }

  pauseCampaign(c: Campaign, event: Event): void {
    event.stopPropagation();
    this.performAction(c, 'pause');
  }

  enableCampaign(c: Campaign, event: Event): void {
    event.stopPropagation();
    this.performAction(c, 'enable');
  }

  createCampaign(): void {
    if (!this.newCampaign.name || this.newCampaign.dailyBudget <= 0) return;
    this.createLoading.set(true);

    this.http.post<{ success: boolean; error?: string }>('/api/campaign-create', { ...this.newCampaign, status: 'PAUSED' }).subscribe({
      next: (res) => {
        this.createLoading.set(false);
        if (res.success) {
          this.showCreateForm.set(false);
          this.newCampaign = { name: '', dailyBudget: 10, channel: 'SEARCH' };
          this.ads.refresh();
        }
      },
      error: (err) => {
        this.createLoading.set(false);
        this.actionResult.set({ name: 'create', success: false, message: err.error?.error ?? 'Failed to create campaign' });
      },
    });
  }

  private performAction(c: Campaign, action: 'pause' | 'enable'): void {
    this.actionLoading.set(c.name);
    this.actionResult.set(null);

    this.http.post<{ success: boolean; error?: string }>('/api/campaign-action', {
      campaignName: c.name,
      action,
    }).subscribe({
      next: (res) => {
        this.actionLoading.set(null);
        if (res.success) {
          this.actionResult.set({ name: c.name, success: true, message: `Campaign ${action}d successfully` });
          this.ads.refresh();
        } else {
          this.actionResult.set({ name: c.name, success: false, message: res.error ?? 'Action failed' });
        }
      },
      error: (err) => {
        this.actionLoading.set(null);
        const msg = err.error?.error ?? 'Network error';
        this.actionResult.set({ name: c.name, success: false, message: msg });
      },
    });
  }
}
