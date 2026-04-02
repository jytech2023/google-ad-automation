import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService, Campaign } from '../ads-data.service';
import { AiWidgetComponent } from './ai-widget/ai-widget.component';
import { CampaignConfirmationComponent, CreatedCampaign } from './campaign-confirmation/campaign-confirmation.component';

@Component({
  selector: 'app-campaigns',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe, FormsModule, AiWidgetComponent, CampaignConfirmationComponent],
  templateUrl: './campaigns.component.html',
  styleUrl: './campaigns.component.scss',
})
export class CampaignsComponent {
  ads = inject(AdsDataService);
  private http = inject(HttpClient);

  filter = signal<'all' | 'active' | 'paused' | 'ended'>('all');
  selectedCampaign = signal<Campaign | null>(null);

  showCreateForm = signal(false);
  createLoading = signal(false);
  createError = signal('');
  newCampaign = { name: '', dailyBudget: 10, channel: 'SEARCH' };
  showAiWidget = signal(false);
  createdCampaigns = signal<CreatedCampaign[]>([]);

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

  createCampaign(): void {
    if (!this.newCampaign.name || this.newCampaign.dailyBudget <= 0) return;
    this.createLoading.set(true);
    this.createError.set('');

    const payload = { ...this.newCampaign, status: 'PAUSED' };
    this.http.post<{ success: boolean; campaignName: string; resourceName: string; status: string; dailyBudget: number; error?: string }>('/api/campaign-create', payload).subscribe({
      next: (res) => {
        this.createLoading.set(false);
        if (res.success) {
          this.showCreateForm.set(false);
          this.createdCampaigns.set([{
            campaignName: res.campaignName,
            resourceName: res.resourceName,
            status: res.status,
            dailyBudget: res.dailyBudget,
            channel: payload.channel,
            createdAt: new Date().toISOString(),
          }]);
          this.newCampaign = { name: '', dailyBudget: 10, channel: 'SEARCH' };
          this.ads.refresh();
        }
      },
      error: (err) => {
        this.createLoading.set(false);
        this.createError.set(err.error?.error ?? 'Failed to create campaign');
      },
    });
  }

  onAiCampaignCreated(campaigns: CreatedCampaign[]): void {
    this.createdCampaigns.set(campaigns);
    this.showAiWidget.set(false);
    this.ads.refresh();
  }

  dismissConfirmation(): void {
    this.createdCampaigns.set([]);
  }
}
