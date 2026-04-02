# AdFlow Pro - Marketing Automation Platform

A modern marketing automation platform built with Angular 19, designed to help businesses automate ad campaigns, optimize conversions, and scale their digital marketing efforts.

## Features

- **Google Ads Management** — End-to-end campaign management with keyword research, bid optimization, and performance tracking
- **Multi-Channel Advertising** — Unified management across Google, Meta, LinkedIn, and more
- **Conversion Tracking** — Advanced attribution modeling to measure every touchpoint in the customer journey
- **Marketing Consulting** — Expert guidance on ad strategy, budget allocation, and audience targeting
- **Budget Optimization** — AI-driven budget allocation and ROAS optimization
- **Analytics Dashboard** — Real-time reporting with custom dashboards and actionable insights
- **Internationalization** — Full i18n support (English, Chinese, Spanish) with URL-based language switching
- **Google Ads Integration** — Built-in gtag.js tracking and conversion event reporting
- **Responsive Design** — Mobile-friendly UI across all devices

## Tech Stack

- **Framework**: Angular 19 (standalone components)
- **Styling**: SCSS with CSS custom properties
- **Deployment**: Vercel (with serverless functions)
- **Analytics**: Vercel Analytics + Speed Insights
- **API**: Python serverless functions (contact form, health check)

## Getting Started

### Prerequisites

- Node.js 18+
- Angular CLI (`npm install -g @angular/cli`)

### Development

```bash
npm install
ng serve
```

Open [http://localhost:4200](http://localhost:4200) in your browser.

### Build

```bash
npm run build
```

Build artifacts are stored in the `dist/` directory.

### Deployment

The project is configured for Vercel deployment. Push to the main branch to trigger automatic deployment.

## Project Structure

```text
src/
├── app/
│   ├── components/       # Shared components (header, footer)
│   ├── pages/            # Page components (home)
│   ├── i18n/             # Internationalization (translations, service, pipe)
│   ├── services/         # Google Ads gtag service
│   └── environments/     # Environment configs
api/
├── contact.py            # Contact form serverless function
└── health.py             # Health check endpoint
```

## License

Private - All rights reserved.
