import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes'; // Assuming you have a separate file for routes

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes)
  ]
};