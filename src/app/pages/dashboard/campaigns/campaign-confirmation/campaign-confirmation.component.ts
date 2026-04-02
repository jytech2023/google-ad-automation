import { Component, input, output } from '@angular/core';
import { CurrencyPipe } from '@angular/common';

export interface CreatedCampaign {
  campaignName: string;
  resourceName: string;
  status: string;
  dailyBudget: number;
  channel: string;
  createdAt: string;
  created?: { budget: string; campaign: string; adGroup: string; ad: string; keywords: number };
  errors?: any[];
}

@Component({
  selector: 'app-campaign-confirmation',
  standalone: true,
  imports: [CurrencyPipe],
  templateUrl: './campaign-confirmation.component.html',
  styleUrl: './campaign-confirmation.component.scss',
})
export class CampaignConfirmationComponent {
  campaigns = input.required<CreatedCampaign[]>();
  dismiss = output<void>();

  googleAdsUrl(): string {
    return 'https://ads.google.com/aw/campaigns';
  }
}
