import { Injectable, signal, computed } from '@angular/core';
import { TRANSLATIONS, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, Translations } from './translations';

@Injectable({ providedIn: 'root' })
export class I18nService {
  readonly supportedLanguages = SUPPORTED_LANGUAGES;
  private currentLang = signal<string>(DEFAULT_LANGUAGE);

  readonly lang = this.currentLang.asReadonly();
  readonly currentLanguage = computed(() =>
    SUPPORTED_LANGUAGES.find(l => l.code === this.currentLang()) ?? SUPPORTED_LANGUAGES[0]
  );

  private get translations(): Translations {
    return TRANSLATIONS[this.currentLang()] ?? TRANSLATIONS[DEFAULT_LANGUAGE];
  }

  t(key: string): string {
    return this.translations[key] ?? key;
  }

  setLanguage(lang: string): void {
    if (TRANSLATIONS[lang]) {
      this.currentLang.set(lang);
      document.documentElement.lang = lang;
    }
  }

  initFromUrl(langParam: string | null): void {
    if (langParam && TRANSLATIONS[langParam]) {
      this.setLanguage(langParam);
    }
  }
}
