function ChatSession(user, isGroupChat) {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        var chat = $("#chat");

        var cardEle;
        if (data.sender == user) {
            cardEle = $("<div class='card clearfix pull-right user-message'></div>")
        } else {
            cardEle = $("<div class='card clearfix'></div>")
        }
        var cardBlockEle = $("<div class='card-block'></div>");
        var messageEle = $("<p></p>").text(data.message);
        var timestampEle = $("<p></p>").append($("<small class='text-muted'></small>").text(data.timestamp));
        if (isGroupChat && data.sender != user) {
            var senderEle = $("<p class='card-title' style='color: #308430'></p>")
                .append($("<b></b>").text(s.titleize(data.sender)));
            cardBlockEle.append(senderEle);
        }
        cardBlockEle.append(messageEle).append(timestampEle);
        cardEle.append(cardBlockEle);
        chat.append(cardEle)
    };

    $("#chatform").on("submit", function(event) {
        var messageEle = $("#message");
        if (!messageEle.val()) return;
        var message = {message: messageEle.val()};
        chatsock.send(JSON.stringify(message));
        messageEle.val('').focus();
        return false
    });
}