(function(){
	var webSocket = undefined;

	var template = function(color) {
		return '<div class="ui message ' + color + '"><div class="comment">' +
		//'<a class="avatar"><img src="/images/avatar/small/matt.jpg"></a>' +
		'<div class="content">' + '<a class="author">Matt</a>' +
		'<div class="text"></div>' +
		'</div></div></div>';
	};

	var comment = function(msg) {
		var elms = $('[data-name="chat"]').find('div')
		while (elms.length >= 100) {
			elms = elms.last().remove();
		}
		var el = $(template(msg.color.replace(/black/, '')));
		el.find('.text').text(msg.text)
		el.find('.author').text(msg.from.replace(/ryo terunuma · /, '💂🏻'))
		$('[data-name="chat"]').prepend( el );
	};

	var onMessage = function(event) {
		if (event && event.data) {
			var data = JSON.parse(event.data)
			//console.log(data.comments);
            //$('#active').text(data.active)
			console.log(data);
			data.comments.forEach(function(c) {
				//console.log(c);
				comment(c);
			});

		}
	};

	var onOpen = function(event) {
		onMessage(event)
	};

	var onErr = function() {
	};

	var onClose = function() {
		webSocket = undefined;
	};

	var requestData = function() {
		var c = $('#comment').val();
		if (c.length == 0) {
			$('#comment').val('🙈🙈🙈');
		}
		var f = $('#from').val();
		if (f.length == 0) {
			f = 'うぇぶからです代理';
		}

		var d = {
			from: f,
			text: c,
			color: $('#color').val()
		};

		//console.log(d);

		$('#comment').val('');
		return JSON.stringify(d);
	};

	var init = function() {
		var uri = "ws://" + location.host + "/chat";
		webSocket = new WebSocket(uri);
		webSocket.onopen = onOpen;
		webSocket.onmessage = onMessage;
		webSocket.onerror = onErr;
		webSocket.onclose = onClose;

		var send = function(event) {
			if (event && event.which == 13) {
				webSocket.send(requestData());
			}
		};

		var submit = function() {
			webSocket.send(requestData());
		};

		$("#comment").keyup(send);
		$("button").click(submit);
	};

	$(init);
})()
