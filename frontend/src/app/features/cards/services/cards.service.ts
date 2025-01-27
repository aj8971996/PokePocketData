// src/app/features/cards/services/cards.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Card, PokemonCard } from '../models/card.model';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CardsService {
  private readonly apiUrl = `${environment.apiUrl}/cards`;

  constructor(private http: HttpClient) {}

  getCards(params?: any): Observable<Card[]> {
    return this.http.get<Card[]>(this.apiUrl, { params });
  }

  getCard(id: string): Observable<Card> {
    return this.http.get<Card>(`${this.apiUrl}/${id}`);
  }

  createPokemonCard(card: Omit<PokemonCard, 'card_id'>): Observable<PokemonCard> {
    return this.http.post<PokemonCard>(`${this.apiUrl}/pokemon`, card);
  }
}