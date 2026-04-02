import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { DatePipe } from '@angular/common';
import { I18nService } from '../../i18n/i18n.service';
import { TranslatePipe } from '../../i18n/translate.pipe';
import { AdsDataService } from './ads-data.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, DatePipe, TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private route = inject(ActivatedRoute);
  i18n = inject(I18nService);
  ads = inject(AdsDataService);
  today = new Date();

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.i18n.initFromUrl(params.get('lang'));
    });
  }
}
