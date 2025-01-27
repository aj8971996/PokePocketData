// src/environments/environment.ts
export const environment = {
    production: false,
    apiUrl: 'http://localhost:8000/api/v1',
    apiEndpoints: {
      auth: {
        google: '/auth/google/callback'
      },
      cards: '/cards',
      decks: '/decks',
      games: '/games'
    }
  };