import { Component, inject, signal, output } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CurrencyPipe } from '@angular/common';
import { CreatedCampaign } from '../campaign-confirmation/campaign-confirmation.component';

interface AiCampaignPlan {
  campaigns: Array<{ name: string; dailyBudget: number; channel: string; rationale: string }>;
  keywords: string[];
  adCopy: { headlines: string[]; descriptions: string[] };
  targetAudience: string;
  estimatedMonthlyBudget: number;
  tips: string[];
}

@Component({
  selector: 'app-ai-widget',
  standalone: true,
  imports: [CurrencyPipe],
  templateUrl: './ai-widget.component.html',
  styleUrl: './ai-widget.component.scss',
})
export class AiWidgetComponent {
  private http = inject(HttpClient);

  campaignCreated = output<CreatedCampaign[]>();
  private createdList: CreatedCampaign[] = [];

  aiPrompt = signal('');
  aiLoading = signal(false);
  aiPlan = signal<AiCampaignPlan | null>(null);
  aiError = signal('');
  aiCreating = signal<number | null>(null);
  aiCreated = signal<Set<number>>(new Set());
  crawledSite = signal<{ url: string; title: string; siteName: string } | null>(null);

  generateAiPlan(): void {
    const prompt = this.aiPrompt().trim();
    if (!prompt) return;
    this.aiLoading.set(true);
    this.aiPlan.set(null);
    this.aiError.set('');
    this.aiCreated.set(new Set());

    this.crawledSite.set(null);
    this.http.post<{ success: boolean; plan: AiCampaignPlan; crawledSite?: { url: string; title: string; siteName: string }; error?: string }>('/api/ai-campaign', { prompt }).subscribe({
      next: (res) => {
        this.aiLoading.set(false);
        if (res.success) {
          this.aiPlan.set(res.plan);
          if (res.crawledSite) this.crawledSite.set(res.crawledSite);
        } else {
          this.aiError.set(res.error ?? 'Failed to generate plan');
        }
      },
      error: (err) => {
        this.aiLoading.set(false);
        this.aiError.set(err.error?.error ?? 'Failed to generate campaign plan');
      },
    });
  }

  createAiCampaign(index: number): void {
    const plan = this.aiPlan();
    if (!plan || index >= plan.campaigns.length) return;
    const c = plan.campaigns[index];
    this.aiCreating.set(index);

    const site = this.crawledSite();
    this.http.post<{ success: boolean; campaignName: string; resourceName: string; status: string; dailyBudget: number; created?: any; errors?: any[]; error?: string }>('/api/campaign-create', {
      name: c.name,
      dailyBudget: c.dailyBudget,
      channel: c.channel,
      status: 'PAUSED',
      headlines: plan.adCopy.headlines,
      descriptions: plan.adCopy.descriptions,
      keywords: plan.keywords,
      finalUrl: site?.url || '',
    }).subscribe({
      next: (res) => {
        this.aiCreating.set(null);
        if (res.success) {
          const created = new Set(this.aiCreated());
          created.add(index);
          this.aiCreated.set(created);
          this.createdList.push({
            campaignName: res.campaignName,
            resourceName: res.resourceName,
            status: res.status,
            dailyBudget: res.dailyBudget,
            channel: c.channel,
            createdAt: new Date().toISOString(),
            created: res.created,
            errors: res.errors,
          });
          // If all campaigns created, emit to show confirmation
          if (this.allCreated()) {
            this.campaignCreated.emit([...this.createdList]);
          }
        } else {
          this.aiError.set(res.error ?? 'Failed to create campaign');
        }
      },
      error: (err) => {
        this.aiCreating.set(null);
        this.aiError.set(err.error?.error ?? 'Failed to create campaign');
      },
    });
  }

  createAllAiCampaigns(): void {
    const plan = this.aiPlan();
    if (!plan) return;
    plan.campaigns.forEach((_, i) => {
      if (!this.aiCreated().has(i)) this.createAiCampaign(i);
    });
  }

  viewSummary(): void {
    if (this.createdList.length > 0) {
      this.campaignCreated.emit([...this.createdList]);
    }
  }

  reset(): void {
    this.createdList = [];
    this.aiPrompt.set('');
    this.aiPlan.set(null);
    this.aiError.set('');
    this.aiCreated.set(new Set());
    this.crawledSite.set(null);
  }

  useExample(prompt: string): void {
    this.aiPrompt.set(prompt);
  }

  allCreated(): boolean {
    const plan = this.aiPlan();
    if (!plan) return false;
    return plan.campaigns.every((_, i) => this.aiCreated().has(i));
  }
}
