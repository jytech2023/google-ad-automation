import { bootstrapApplication } from '@angular/platform-browser';
import { inject as injectAnalytics } from '@vercel/analytics';
import { injectSpeedInsights } from '@vercel/speed-insights';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { GtagService } from './app/services/gtag.service';
import { environment } from './environments/environment';

// Initialize Vercel Analytics & Speed Insights
injectAnalytics({
  mode: environment.production ? 'production' : 'development',
  debug: !environment.production,
});
injectSpeedInsights();

bootstrapApplication(AppComponent, appConfig)
  .then((appRef) => {
    // Initialize Google Ads tracking from environment config
    const gtag = appRef.injector.get(GtagService);
    gtag.init();
  })
  .catch((err) => console.error(err));
