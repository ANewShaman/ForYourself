// bridge.js
// Receives emotional data from Python WebSocket bridge

window.latestEmotion = null;

let socket;

function startBridge() {
  socket = new WebSocket("ws://localhost:8765");

  socket.onopen = () => {
    console.log("[BRIDGE] Connected to Python WebSocket");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      data._t = performance.now();
      window.latestEmotion = data;
      // console.log("Emotion →", data);
    } catch (e) {
      console.error("Bad JSON:", e);
    }
  };

  socket.onerror = (err) => {
    console.error("WebSocket error", err);
  };

  socket.onclose = () => {
    console.warn("[BRIDGE] Lost connection. Retrying in 2s...");
    setTimeout(startBridge, 2000);
  };
}

startBridge();
