// src/app/features/cards/components/card-detail/card-detail.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, switchMap } from 'rxjs';
import { CardsService } from '../services/cards.service';
import { Card } from '../models/card.model';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card-detail',
  standalone: false,
  template: `
    <div class="container mx-auto p-4" *ngIf="card$ | async as card">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-3xl font-bold mb-4">{{card.name}}</h1>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-gray-600"><span class="font-semibold">Set:</span> {{card.set_name}}</p>
            <p class="text-gray-600"><span class="font-semibold">Pack:</span> {{card.pack_name}}</p>
            <p class="text-gray-600"><span class="font-semibold">Number:</span> {{card.collection_number}}</p>
            <p class="text-gray-600"><span class="font-semibold">Rarity:</span> {{card.rarity}}</p>
          </div>
        </div>
      </div>
    </div>
  `
})
export class CardDetailComponent implements OnInit {
  card$: Observable<Card>;

  constructor(
    private route: ActivatedRoute,
    private cardsService: CardsService
  ) {
    this.card$ = this.route.params.pipe(
      switchMap(params => this.cardsService.getCard(params['id']))
    );
  }

  ngOnInit(): void {}
}