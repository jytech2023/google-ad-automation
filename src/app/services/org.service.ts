import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '@auth0/auth0-angular';
import { filter, switchMap, take } from 'rxjs/operators';

export interface Org {
  id: number;
  name: string;
  domain: string | null;
  plan: string;
  role: string;
}

@Injectable({ providedIn: 'root' })
export class OrgService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);

  orgs = signal<Org[]>([]);
  activeOrg = signal<Org | null>(null);
  loading = signal(false);

  loadOrgs(): void {
    this.loading.set(true);
    this.auth.user$.pipe(
      filter((u) => !!u),
      take(1),
    ).subscribe((user) => {
      if (!user?.sub) return;
      this.http.get<{ orgs: Org[] }>(`/api/orgs?auth0Id=${encodeURIComponent(user.sub)}`).subscribe({
        next: (res) => {
          this.orgs.set(res.orgs);
          this.loading.set(false);
          // Restore from localStorage or pick first
          const savedId = typeof localStorage !== 'undefined' ? localStorage.getItem('activeOrgId') : null;
          const saved = savedId ? res.orgs.find(o => o.id === +savedId) : null;
          this.activeOrg.set(saved || res.orgs[0] || null);
        },
        error: () => this.loading.set(false),
      });
    });
  }

  switchOrg(org: Org): void {
    this.activeOrg.set(org);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('activeOrgId', String(org.id));
    }
  }
}
