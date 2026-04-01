/**
 * Build-time script: injects env vars into environment.prod.ts
 * Runs before `ng build` via the build command.
 */
const fs = require('fs');
const path = require('path');

const envFile = path.resolve(__dirname, '../src/environments/environment.prod.ts');
let content = fs.readFileSync(envFile, 'utf-8');

const replacements = {
  '${GOOGLE_ADS_MEASUREMENT_ID}': process.env.GOOGLE_ADS_MEASUREMENT_ID || 'GA_MEASUREMENT_ID',
  '${GOOGLE_ADS_CONVERSION_ID}': process.env.GOOGLE_ADS_CONVERSION_ID || 'AW-XXXXXXXXX',
  '${GOOGLE_ADS_CONVERSION_LABEL}': process.env.GOOGLE_ADS_CONVERSION_LABEL || 'YOUR_CONVERSION_LABEL',
};

for (const [placeholder, value] of Object.entries(replacements)) {
  content = content.replace(placeholder, value);
}

fs.writeFileSync(envFile, content, 'utf-8');
console.log('[set-env] Environment variables injected into environment.prod.ts');
