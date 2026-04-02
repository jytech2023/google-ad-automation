import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '@auth0/auth0-angular';
import { filter, switchMap, take } from 'rxjs/operators';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);

  return auth.isLoading$.pipe(
    filter((loading) => !loading),
    take(1),
    switchMap(() =>
      auth.isAuthenticated$.pipe(
        take(1),
        switchMap((isAuth) => {
          if (isAuth) {
            return [true];
          }
          // Not authenticated — trigger login and wait (never resolves, page will redirect)
          auth.loginWithRedirect();
          return [];
        }),
      ),
    ),
  );
};
