import { Component, inject, signal, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService } from '../ads-data.service';

interface BillingSummary {
  totalCost: number;
  totalImpressions: number;
  totalClicks: number;
  totalConversions: number;
  avgCpc: number;
  avgCostPerConversion: number;
}

interface CampaignCost {
  name: string;
  status: string;
  cost: number;
  clicks: number;
  conversions: number;
  cpc: number;
  costPerConv: number;
}

interface DailyCost {
  date: string;
  cost: number;
}

@Component({
  selector: 'app-billing',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe],
  templateUrl: './billing.component.html',
  styleUrl: './billing.component.scss',
})
export class BillingComponent {
  private http = inject(HttpClient);
  ads = inject(AdsDataService);

  loading = signal(true);
  summary = signal<BillingSummary | null>(null);
  byCampaign = signal<CampaignCost[]>([]);
  dailyCost = signal<DailyCost[]>([]);
  maxDailyCost = signal(0);
  source = signal('');

  constructor() {
    effect(() => {
      const range = this.ads.dateRange();
      const days = range === '30d' ? 30 : range === '14d' ? 14 : 7;
      this.fetchBilling(days);
    });
  }

  private fetchBilling(days: number): void {
    this.loading.set(true);
    this.http.get<{
      source: string;
      summary: BillingSummary;
      byCampaign: CampaignCost[];
      dailyCost: DailyCost[];
    }>(`/api/billing?days=${days}`).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.source.set(res.source);
        this.summary.set(res.summary);
        this.byCampaign.set(res.byCampaign);
        this.dailyCost.set(res.dailyCost);
        this.maxDailyCost.set(Math.max(...res.dailyCost.map(d => d.cost), 1));
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  costBarHeight(cost: number): string {
    return `${(cost / this.maxDailyCost()) * 100}%`;
  }

  costPercentage(cost: number): number {
    const total = this.summary()?.totalCost || 1;
    return Math.round((cost / total) * 100);
  }
}
