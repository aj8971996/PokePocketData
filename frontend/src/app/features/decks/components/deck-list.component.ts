// src/app/features/decks/components/deck-list.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-deck-list',
  standalone: false,
  template: `
    <div class="container mx-auto p-4">
      <h1 class="text-2xl font-bold mb-4">Decks</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Deck list content will go here -->
      </div>
    </div>
  `
})
export class DeckListComponent {}