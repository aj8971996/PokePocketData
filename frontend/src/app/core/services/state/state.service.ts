// src/app/core/services/state/state.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StateService<T> {
  private state: BehaviorSubject<T>;
  public state$: Observable<T>;

  constructor() {
    this.state = new BehaviorSubject<T>({} as T);
    this.state$ = this.state.asObservable();
  }

  public initialize(initialState: T): void {
    this.state.next(initialState);
  }

  public getState(): T {
    return this.state.getValue();
  }

  public setState(newState: T): void {
    this.state.next(newState);
  }

  public updateState(partialState: Partial<T>): void {
    this.setState({ ...this.getState(), ...partialState });
  }
}