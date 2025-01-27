// src/app/features/decks/decks.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { DeckListComponent } from './components/deck-list.component';
import { DeckDetailComponent } from './components/deck-detail.component';

const routes: Routes = [
  {
    path: '',
    component: DeckListComponent
  },
  {
    path: ':id',
    component: DeckDetailComponent
  }
];

@NgModule({
  declarations: [
    DeckListComponent,
    DeckDetailComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    RouterModule.forChild(routes)
  ]
})
export class DecksModule { }