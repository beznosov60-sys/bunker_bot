from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response

app = FastAPI()

INDEX_HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bunker Bot</title>
</head>
<body>
  <h1>Bunker Bot</h1>
  <p id="state">Подключение...</p>
  <ul id="log"></ul>

  <script>
    const stateEl = document.getElementById('state');
    const logEl = document.getElementById('log');

    function addLog(message) {
      const li = document.createElement('li');
      li.textContent = message;
      logEl.appendChild(li);
    }

    const ws = new WebSocket(`ws://${location.host}/ws`);

    ws.onopen = () => {
      stateEl.textContent = 'WebSocket подключен';
      ws.send(JSON.stringify({ type: 'ping', message: 'hello' }));
    };

    ws.onmessage = (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        // Если сервер прислал обычный текст, не падаем.
        addLog(`Текст: ${event.data}`);
        return;
      }

      if (data.type === 'status') {
        addLog(`Статус: ${data.message}`);
      } else if (data.type === 'echo') {
        addLog(`Эхо: ${data.message}`);
      } else {
        addLog(`Сообщение: ${JSON.stringify(data)}`);
      }
    };

    ws.onerror = () => {
      stateEl.textContent = 'Ошибка WebSocket';
    };

    ws.onclose = () => {
      stateEl.textContent = 'WebSocket отключен';
    };
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.get("/favicon.ico")
async def favicon() -> Response:
    # Заглушка favicon, чтобы не было 404 в браузере.
    return Response(content=b"", media_type="image/x-icon")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "status", "message": "connected"})

    try:
        while True:
            raw_message = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "message": raw_message})
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
