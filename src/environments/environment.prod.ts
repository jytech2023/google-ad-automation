export const environment = {
  production: true,
  googleAds: {
    measurementId: '${GOOGLE_ADS_MEASUREMENT_ID}',
    conversionId: '${GOOGLE_ADS_CONVERSION_ID}',
    conversionLabel: '${GOOGLE_ADS_CONVERSION_LABEL}',
  },
  auth0: {
    domain: '${AUTH0_DOMAIN}',
    clientId: '${AUTH0_CLIENT_ID}',
  },
  apiBase: '',
};
