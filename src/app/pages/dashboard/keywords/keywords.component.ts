import { Component, inject, signal } from '@angular/core';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService } from '../ads-data.service';

interface Keyword {
  keyword: string;
  campaign: string;
  matchType: 'Exact' | 'Phrase' | 'Broad';
  impressions: number;
  clicks: number;
  ctr: number;
  cpc: number;
  conversions: number;
  qualityScore: number;
}

@Component({
  selector: 'app-keywords',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe],
  templateUrl: './keywords.component.html',
  styleUrl: './keywords.component.scss',
})
export class KeywordsComponent {
  ads = inject(AdsDataService);
  searchQuery = signal('');

  // Demo keywords derived from campaign names
  keywords = signal<Keyword[]>([
    { keyword: 'wholesale distributor', campaign: 'DK Wholesale', matchType: 'Broad', impressions: 4200, clicks: 320, ctr: 7.62, cpc: 1.85, conversions: 28, qualityScore: 7 },
    { keyword: 'bulk buy products', campaign: 'DK Wholesale', matchType: 'Phrase', impressions: 3100, clicks: 245, ctr: 7.90, cpc: 2.10, conversions: 18, qualityScore: 6 },
    { keyword: 'wholesale supplier usa', campaign: 'DK Wholesale', matchType: 'Exact', impressions: 1800, clicks: 168, ctr: 9.33, cpc: 1.65, conversions: 22, qualityScore: 8 },
    { keyword: 'electric bike shop', campaign: 'funplus-bike', matchType: 'Broad', impressions: 5600, clicks: 420, ctr: 7.50, cpc: 2.40, conversions: 15, qualityScore: 5 },
    { keyword: 'e-bike sale', campaign: 'funplus-bike', matchType: 'Phrase', impressions: 3800, clicks: 310, ctr: 8.16, cpc: 1.90, conversions: 12, qualityScore: 7 },
    { keyword: 'electric bicycle', campaign: 'funplus-bike', matchType: 'Exact', impressions: 2900, clicks: 195, ctr: 6.72, cpc: 3.20, conversions: 8, qualityScore: 4 },
    { keyword: 'bay area news chinese', campaign: 'cnBayarea.com', matchType: 'Broad', impressions: 2100, clicks: 180, ctr: 8.57, cpc: 0.95, conversions: 5, qualityScore: 6 },
    { keyword: 'semiconductor products', campaign: '菲科半导体系列产品', matchType: 'Phrase', impressions: 1500, clicks: 98, ctr: 6.53, cpc: 4.50, conversions: 3, qualityScore: 5 },
  ]);

  get filteredKeywords(): Keyword[] {
    const q = this.searchQuery().toLowerCase();
    if (!q) return this.keywords();
    return this.keywords().filter(k =>
      k.keyword.toLowerCase().includes(q) || k.campaign.toLowerCase().includes(q)
    );
  }
}
