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