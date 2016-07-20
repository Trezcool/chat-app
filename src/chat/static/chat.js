$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        console.log(data);
        var chat = $("#chat");
        var ele = $('<tr></tr>');

        ele.append($("<td></td>").text(data.sender));
        ele.append($("<td></td>").text(data.message));
        ele.append($("<td></td>").text(data.timestamp));
        
        chat.append(ele)
    };

    $("#chatform").on("submit", function(event) {
        var messageEle = $("#message");
        if (!messageEle.val()) return;
        var message = {message: messageEle.val()};
        chatsock.send(JSON.stringify(message));
        messageEle.val('').focus();
        return false
    });
});