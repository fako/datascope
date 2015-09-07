var ws = new WebSocket(VT.webSocketEndpoint);
ws.onopen = function() {
    console.log("websocket connected");
};
ws.onmessage = function(e) {
    console.log("Received: " + e.data);
};
ws.onerror = function(e) {
    console.error(e);
};
ws.onclose = function(e) {
    console.log("connection closed");
};