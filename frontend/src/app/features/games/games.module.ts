// src/app/features/games/games.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { GameListComponent } from './components/game-list.component';
import { GameDetailComponent } from './components/game-detail.component';

const routes: Routes = [
  {
    path: '',
    component: GameListComponent
  },
  {
    path: ':id',
    component: GameDetailComponent
  }
];

@NgModule({
  declarations: [
    GameListComponent,
    GameDetailComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    RouterModule.forChild(routes)
  ]
})
export class GamesModule { }