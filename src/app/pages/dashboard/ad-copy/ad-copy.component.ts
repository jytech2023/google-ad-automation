import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService } from '../ads-data.service';

interface AdSuggestion {
  headline1: string;
  headline2: string;
  headline3: string;
  description1: string;
  description2: string;
  score: number;
}

@Component({
  selector: 'app-ad-copy',
  standalone: true,
  imports: [FormsModule, TranslatePipe],
  templateUrl: './ad-copy.component.html',
  styleUrl: './ad-copy.component.scss',
})
export class AdCopyComponent {
  ads = inject(AdsDataService);

  productInfo = signal('');
  targetAudience = signal('');
  tone = signal<'professional' | 'casual' | 'urgent'>('professional');
  generating = signal(false);

  suggestions = signal<AdSuggestion[]>([
    {
      headline1: 'Premium Wholesale Deals',
      headline2: 'Save Up to 40% Today',
      headline3: 'Fast US Shipping',
      description1: 'Access thousands of wholesale products at unbeatable prices. Trusted by 500+ businesses nationwide.',
      description2: 'Order in bulk and save big. Free shipping on orders over $500. Start your wholesale journey today.',
      score: 92,
    },
    {
      headline1: 'Wholesale Products Online',
      headline2: 'Best Prices Guaranteed',
      headline3: 'Sign Up Free',
      description1: 'Browse our extensive catalog of wholesale goods. From electronics to home goods — we have it all.',
      description2: 'Join thousands of retailers saving money with our platform. No minimum order required.',
      score: 87,
    },
    {
      headline1: 'Bulk Buy & Save More',
      headline2: 'Wholesale Direct Prices',
      headline3: 'Shop Now & Save',
      description1: 'Cut your supply costs by up to 40%. Direct-from-manufacturer pricing with no middleman.',
      description2: 'Reliable wholesale supplier with next-day shipping. Quality products at wholesale prices.',
      score: 84,
    },
  ]);

  generateAds(): void {
    this.generating.set(true);
    // Simulate AI generation
    setTimeout(() => {
      this.generating.set(false);
    }, 2000);
  }
}
