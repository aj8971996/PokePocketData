// src/app/features/decks/components/deck-detail.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-deck-detail',
  standalone: false,
  template: `
    <div class="container mx-auto p-4">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-3xl font-bold mb-4">Deck Details</h1>
        <!-- Deck detail content will go here -->
      </div>
    </div>
  `
})
export class DeckDetailComponent {}