//var ws = new WebSocket(VT.webSocketEndpoint);
//interval = null;
//
//ws.onopen = function() {
//    console.log("websocket connected");
//    initial = true;
//};
//ws.onmessage = function(e) {
//    console.log("Received: " + e.data);
//    if(e.data == '--heartbeat--') {
//        return;
//    }
//    if(initial) {
//        initial = false;
//        return;
//    }
//    if(interval === null) {
//        interval = setInterval(function() { VT.functions.scrollDocument("top-left") }, 100)
//    } else {
//        clearInterval(interval);
//        interval = null;
//    }
//};
//ws.onerror = function(e) {
//    console.error(e);
//    clearInterval(interval);
//    interval = null;
//};
//ws.onclose = function(e) {
//    console.log("connection closed");
//    clearInterval(interval);
//    interval = null;
//};

window.WSExecute = function(socket, heartbeat, functions) {

    this.ws4redis = WS4Redis({
        uri: socket,
        receive_message: this.execute,
        heartbeat_msg: heartbeat,
        on_open: function() {
            console.log("websocket connected");
        },
        on_error: function(e) {
            console.error(e);
        },
        on_close: function(e) {
            console.log("connection closed");
        }
    });
    this.functions = functions;
    return this;
};

WSExecute.prototype.execute = function(msg) {
    var splitMessage = msg.split(':');
    var fnc = splitMessage[0];
    var args = splitMessage[1].split(',');
    if(wsConnection.functions[fnc]) {
        return wsConnection.functions[fnc].apply(this, args);
    } else {
        $.error('Function ' +  fnc + ' does not exist in functions object.' );
    }
};

WSExecute.prototype.send = function(msg){
    this.ws4redis.send_message(msg);
};

$(function(){
    window.wsConnection = new WSExecute(VT.webSocketEndpoint, VT.webSocketHeartbeat, VT.functions || {});
});