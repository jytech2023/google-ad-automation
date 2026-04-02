import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AsyncPipe, DatePipe } from '@angular/common';
import { AuthService } from '@auth0/auth0-angular';
import { I18nService } from '../../i18n/i18n.service';
import { TranslatePipe } from '../../i18n/translate.pipe';
import { AdsDataService } from './ads-data.service';
import { OrgService, Org } from '../../services/org.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, DatePipe, AsyncPipe, TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private route = inject(ActivatedRoute);
  i18n = inject(I18nService);
  ads = inject(AdsDataService);
  auth = inject(AuthService);
  orgService = inject(OrgService);
  today = new Date();
  orgDropdownOpen = signal(false);

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.i18n.initFromUrl(params.get('lang'));
    });
    this.orgService.loadOrgs();
  }

  switchOrg(org: Org): void {
    this.orgService.switchOrg(org);
    this.orgDropdownOpen.set(false);
  }

  logout(): void {
    this.auth.logout({ logoutParams: { returnTo: window.location.origin } });
  }
}
