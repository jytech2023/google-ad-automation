import { Component, inject, computed } from '@angular/core';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService } from '../ads-data.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss',
})
export class ReportsComponent {
  ads = inject(AdsDataService);

  maxCost = computed(() => Math.max(1, ...this.ads.dailyMetrics().map(d => d.cost)));
  maxClicks = computed(() => Math.max(1, ...this.ads.dailyMetrics().map(d => d.clicks)));

  totalCost = computed(() => this.ads.dailyMetrics().reduce((sum, d) => sum + d.cost, 0));
  totalClicks = computed(() => this.ads.dailyMetrics().reduce((sum, d) => sum + d.clicks, 0));
  totalImpressions = computed(() => this.ads.dailyMetrics().reduce((sum, d) => sum + d.impressions, 0));
  totalConversions = computed(() => this.ads.dailyMetrics().reduce((sum, d) => sum + d.conversions, 0));
  avgCpc = computed(() => this.totalClicks() > 0 ? this.totalCost() / this.totalClicks() : 0);

  barHeight(value: number, max: number): string {
    return Math.round((value / max) * 100) + '%';
  }
}
