// src/environments/environment.prod.ts
export const environment = {
    production: true,
    apiUrl: 'https://your-production-api-url/api/v1',  // Update this with your production API URL
    apiEndpoints: {
      auth: {
        google: '/auth/google/callback'
      },
      cards: '/cards',
      decks: '/decks',
      games: '/games'
    }
  };