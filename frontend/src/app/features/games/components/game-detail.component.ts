// src/app/features/games/components/game-detail.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-game-detail',
  standalone: false,
  template: `
    <div class="container mx-auto p-4">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-3xl font-bold mb-4">Game Details</h1>
        <!-- Game detail content will go here -->
      </div>
    </div>
  `
})
export class GameDetailComponent {}