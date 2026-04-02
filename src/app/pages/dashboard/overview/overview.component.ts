import { Component, inject } from '@angular/core';
import { DecimalPipe, CurrencyPipe } from '@angular/common';
import { TranslatePipe } from '../../../i18n/translate.pipe';
import { AdsDataService } from '../ads-data.service';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [DecimalPipe, CurrencyPipe, TranslatePipe],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.scss',
})
export class OverviewComponent {
  ads = inject(AdsDataService);

  barHeight(value: number, max: number): string {
    return Math.round((value / max) * 100) + '%';
  }
}
