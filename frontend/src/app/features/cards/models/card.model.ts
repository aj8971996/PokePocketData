// src/app/features/cards/models/card.model.ts
export interface Card {
    card_id: string;
    name: string;
    set_name: string;
    pack_name: string;
    collection_number: string;
    rarity: string;
    image_url?: string;
  }
  
  export interface PokemonCard extends Card {
    hp: number;
    type: string;
    stage: string;
    evolves_from?: string;
    abilities: PokemonAbility[];
    weakness: string;
    retreat_cost: number;
  }
  
  export interface PokemonAbility {
    ability_ref: string;
    energy_cost: Record<string, number>;
    ability_effect: string;
    damage?: number;
  }