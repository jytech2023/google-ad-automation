import { bootstrapApplication } from '@angular/platform-browser';
import { inject as injectAnalytics } from '@vercel/analytics';
import { injectSpeedInsights } from '@vercel/speed-insights';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

// Initialize Vercel Analytics & Speed Insights
injectAnalytics();
injectSpeedInsights();

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
