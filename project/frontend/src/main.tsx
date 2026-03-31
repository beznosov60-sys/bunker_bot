import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const tg = (window as Window & { Telegram?: { WebApp?: { ready: () => void } } }).Telegram;
tg?.WebApp?.ready?.();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
