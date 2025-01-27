// src/app/app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: false,
  template: `
    <div class="min-h-screen bg-gray-50">
      <header class="bg-white shadow">
        <nav class="container mx-auto px-4 py-4">
          <h1 class="text-xl font-bold text-gray-900">PokéPocketData</h1>
        </nav>
      </header>
      
      <main class="container mx-auto px-4 py-6">
        <router-outlet></router-outlet>
      </main>
      
      <footer class="bg-white shadow mt-8">
        <div class="container mx-auto px-4 py-4 text-center text-gray-600">
          &copy; 2024 PokéPocketData. All rights reserved.
        </div>
      </footer>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class AppComponent {
  title = 'PokéPocketData';
}