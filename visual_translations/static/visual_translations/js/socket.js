var ws = new WebSocket(VT.webSocketEndpoint);
interval = null;

ws.onopen = function() {
    console.log("websocket connected");
    initial = true;
};
ws.onmessage = function(e) {
    console.log("Received: " + e.data);
    if(initial) {
        initial = false;
        return;
    }
    if(interval === null) {
        interval = setInterval(function() { VT.functions.scrollDocument("top-left") }, 100)
    } else {
        clearInterval(interval);
        interval = null;
    }
};
ws.onerror = function(e) {
    console.error(e);
    clearInterval(interval);
    interval = null;
};
ws.onclose = function(e) {
    console.log("connection closed");
    clearInterval(interval);
    interval = null;
};