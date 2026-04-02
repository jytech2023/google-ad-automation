import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

declare global {
  interface Window { dataLayer: unknown[]; gtag: (...args: unknown[]) => void; }
}

@Injectable({ providedIn: 'root' })
export class GtagService {
  private loaded = false;

  /** Dynamically load gtag.js and configure Google Ads + Analytics measurement */
  init(): void {
    if (this.loaded || typeof document === 'undefined') return;
    const id = environment.googleAds.measurementId;
    if (!id || id === 'GA_MEASUREMENT_ID') return; // skip if not configured

    // dataLayer + gtag function
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id);

    const conversionId = environment.googleAds.conversionId;
    if (conversionId && conversionId !== 'AW-XXXXXXXXX') {
      window.gtag('config', conversionId);
    }

    // Load gtag.js script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${id}`;
    document.head.appendChild(script);

    this.loaded = true;
  }

  /** Fire a Google Ads conversion event */
  trackConversion(value = 1.0, currency = 'USD'): void {
    const { conversionId, conversionLabel } = environment.googleAds;
    if (!window.gtag || !conversionId || conversionId === 'AW-XXXXXXXXX') return;

    const params: Record<string, unknown> = { value, currency };
    if (conversionLabel && conversionLabel !== 'YOUR_CONVERSION_LABEL') {
      params['send_to'] = `${conversionId}/${conversionLabel}`;
    } else {
      params['send_to'] = conversionId;
    }

    window.gtag('event', 'conversion', params);
  }

  /** Track a custom event */
  trackEvent(action: string, params: Record<string, unknown> = {}): void {
    if (!window.gtag) return;
    window.gtag('event', action, params);
  }
}
