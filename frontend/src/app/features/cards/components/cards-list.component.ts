// src/app/features/cards/components/cards-list/cards-list.component.ts
import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { CardsService } from '../services/cards.service';
import { Card } from '../models/card.model';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cards-list',
  standalone: false,
  template: `
    <div class="container mx-auto p-4">
      <h1 class="text-2xl font-bold mb-4">Cards</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ng-container *ngIf="cards$ | async as cards">
          <div *ngFor="let card of cards" 
               class="border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
            <h2 class="text-lg font-semibold">{{card.name}}</h2>
            <p class="text-gray-600">{{card.set_name}}</p>
            <p class="text-sm text-gray-500">{{card.collection_number}}</p>
          </div>
        </ng-container>
      </div>
    </div>
  `
})
export class CardsListComponent implements OnInit {
  cards$: Observable<Card[]>;

  constructor(private cardsService: CardsService) {
    this.cards$ = this.cardsService.getCards();
  }

  ngOnInit(): void {}
}