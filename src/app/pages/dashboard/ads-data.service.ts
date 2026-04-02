import { Injectable, inject, signal, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface KpiCard {
  label: string;
  value: string;
  change: number;
}

export interface Campaign {
  name: string;
  status: 'active' | 'paused' | 'ended';
  channel: string;
  mutable: boolean;
  impressions: number;
  clicks: number;
  ctr: number;
  cost: number;
  conversions: number;
  roas: number;
}

export interface DailyMetric {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
}

interface AdsApiResponse {
  source: 'google_ads_api' | 'demo';
  kpis: {
    impressions: number;
    clicks: number;
    ctr: number;
    conversions: number;
    cost: number;
    roas: number;
  };
  campaigns: Array<{
    name: string;
    status: string;
    channel: string;
    mutable: boolean;
    impressions: number;
    clicks: number;
    ctr: number;
    cost: number;
    conversions: number;
    roas: number;
  }>;
  daily: Array<{
    date: string;
    impressions: number;
    clicks: number;
    conversions: number;
    cost: number;
  }>;
}

@Injectable({ providedIn: 'root' })
export class AdsDataService {
  private http = inject(HttpClient);

  dateRange = signal<'7d' | '14d' | '30d'>('7d');
  loading = signal(false);
  dataSource = signal<'google_ads_api' | 'demo' | 'error'>('demo');
  errorMessage = signal('');

  kpis = signal<KpiCard[]>([]);
  campaigns = signal<Campaign[]>([]);
  dailyMetrics = signal<DailyMetric[]>([]);

  maxImpressions = computed(() => Math.max(1, ...this.dailyMetrics().map(d => d.impressions)));
  maxConversions = computed(() => Math.max(1, ...this.dailyMetrics().map(d => d.conversions)));

  constructor() {
    effect(() => {
      this.fetchData(this.dateRange());
    });
  }

  setDateRange(range: '7d' | '14d' | '30d'): void {
    this.dateRange.set(range);
  }

  refresh(): void {
    this.fetchData(this.dateRange());
  }

  private fetchData(range: '7d' | '14d' | '30d'): void {
    const days = range === '30d' ? 30 : range === '14d' ? 14 : 7;
    this.loading.set(true);

    this.http.get<AdsApiResponse>(`/api/ads-data?days=${days}`).subscribe({
      next: (data) => {
        this.dataSource.set(data.source);
        this.errorMessage.set('');
        this.applyData(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.loading.set(false);
        this.dataSource.set('error');
        this.errorMessage.set(err.error?.error ?? 'Failed to connect to Google Ads API');
      },
    });
  }

  private applyData(data: AdsApiResponse): void {
    const k = data.kpis;
    const costDollars = k.cost / 1_000_000;

    this.kpis.set([
      { label: 'dash.impressions', value: this.fmtNum(k.impressions), change: 0 },
      { label: 'dash.clicks', value: this.fmtNum(k.clicks), change: 0 },
      { label: 'dash.ctr', value: k.ctr.toFixed(2) + '%', change: 0 },
      { label: 'dash.conversions', value: this.fmtNum(k.conversions), change: 0 },
      { label: 'dash.cost', value: '$' + this.fmtNum(costDollars), change: 0 },
      { label: 'dash.roas', value: k.roas.toFixed(1) + 'x', change: 0 },
    ]);

    const statusMap: Record<string, 'active' | 'paused' | 'ended'> = {
      ENABLED: 'active', active: 'active',
      PAUSED: 'paused', paused: 'paused',
      REMOVED: 'ended', ended: 'ended',
    };

    this.campaigns.set(data.campaigns.map(c => ({
      name: c.name,
      status: statusMap[c.status] ?? 'ended',
      channel: c.channel ?? 'UNKNOWN',
      mutable: c.mutable ?? false,
      impressions: c.impressions,
      clicks: c.clicks,
      ctr: c.ctr,
      cost: c.cost / 1_000_000,
      conversions: c.conversions,
      roas: c.roas,
    })));

    this.dailyMetrics.set(data.daily.map(d => ({
      date: d.date,
      impressions: d.impressions,
      clicks: d.clicks,
      conversions: d.conversions,
      cost: d.cost / 1_000_000,
    })));
  }

  fmtNum(n: number): string {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
    return Math.round(n).toString();
  }
}
