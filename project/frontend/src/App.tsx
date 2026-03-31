import { useGameStore } from './store';

function App() {
  const { gameId, status } = useGameStore();

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <h1 className="text-3xl font-bold mb-4">Бункер Mini App</h1>
      <p>Игра: {gameId ?? 'не создана'}</p>
      <p>Статус: {status}</p>
    </main>
  );
}

export default App;
