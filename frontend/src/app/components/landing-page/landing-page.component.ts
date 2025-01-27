// landing-page.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';

interface NavigationItem {
  title: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatSidenavModule,
    MatIconModule,
    MatButtonModule,
    MatListModule
]
})
export class LandingPageComponent {
  isMenuOpen = false;
  currentPage = 'Home';

  navigationItems: NavigationItem[] = [
    { title: 'Create Deck List', icon: 'edit', route: '/create-deck' },
    { title: 'Search Saved Decks', icon: 'search', route: '/search-decks' },
    { title: 'View Stats', icon: 'bar_chart', route: '/statistics' },
    { title: 'Save Game Record', icon: 'save', route: '/game-record' }
  ];

  constructor(private router: Router) {}

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  navigate(route: string, title: string): void {
    this.currentPage = title;
    this.router.navigate([route]);
    this.isMenuOpen = false;
  }
}