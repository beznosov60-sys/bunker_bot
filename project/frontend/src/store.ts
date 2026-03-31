import { create } from 'zustand';

type GameState = {
  gameId: number | null;
  status: string;
  setGame: (gameId: number, status: string) => void;
};

export const useGameStore = create<GameState>((set) => ({
  gameId: null,
  status: 'lobby',
  setGame: (gameId, status) => set({ gameId, status }),
}));
