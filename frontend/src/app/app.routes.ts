// app.routes.ts
import { Routes } from '@angular/router';
import { LandingPageComponent } from './components/landing-page/landing-page.component';

export const routes: Routes = [
  { path: '', component: LandingPageComponent },
  { path: 'create-deck', component: LandingPageComponent },
  { path: 'search-decks', component: LandingPageComponent },
  { path: 'statistics', component: LandingPageComponent },
  { path: 'game-record', component: LandingPageComponent },
  // Add a catch-all route for 404
  { path: '**', redirectTo: '' }
];