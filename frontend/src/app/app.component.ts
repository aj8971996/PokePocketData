import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgIf, NgFor, NgSwitch } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NgIf, NgFor, NgSwitch],
  template: `
    <router-outlet></router-outlet>
  `
})
export class AppComponent {
  title = 'pokepocketdata';
}