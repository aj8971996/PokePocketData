// src/app/features/cards/cards.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { CardsListComponent } from './components/cards-list.component';
import { CardDetailComponent } from './components/card-detail.component';

const routes: Routes = [
  {
    path: '',
    component: CardsListComponent
  },
  {
    path: ':id',
    component: CardDetailComponent
  }
];

@NgModule({
  declarations: [
    CardsListComponent,
    CardDetailComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    RouterModule.forChild(routes)
  ]
})
export class CardsModule { }