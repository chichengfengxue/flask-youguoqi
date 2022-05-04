$(document).ready(function () {
    socket = io('/group');
    var popupLoading = '<i class="notched circle loading icon green"></i> Loading...';
    var message_count = 0;
    var ENTER_KEY = 13;

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    function scrollToBottom() {
        var $messages = $('.messages');
        $messages.scrollTop($messages[0].scrollHeight);
    }

    var page = 1;

    function load_messages() {
        var $messages = $('.messages');
        var position = $messages.scrollTop();
        if (position === 0) {
            page++;
            $('.ui.loader').toggleClass('active');
            $.ajax({
                url: messages_url,
                type: 'GET',
                data: {page: page},
                success: function (data) {
                    var before_height = $messages[0].scrollHeight;
                    // $(data).prependTo('.messages').hide().fadeIn(800);
                    $('.messages').prepend(data).hide().fadeIn(800);
                    var after_height = $messages[0].scrollHeight;
                    flask_moment_render_all();
                    $messages.scrollTop(after_height - before_height);
                    $('.ui.loader').toggleClass('active');
                    activateSemantics();
                },
                error: function () {
                    alert('No more messages.');
                    $('.ui.loader').toggleClass('active');
                }
            });
        }
    }

    // 加入房间
    socket.on('connect', function() {
        socket.emit('join');
    });

    // 退出房间
    socket.on('disconnect', function() {
        socket.emit('leave');
    });

    $('.messages').scroll(load_messages);

    // 插入新房间消息
    socket.on('new room message', function (data) {
        $('.messages').append(data.message_html);
        flask_moment_render_all();
        scrollToBottom();
        activateSemantics();
    });


    // 打印状态信息
    socket.on('status', function(data) {
        $('.messages').append(data.message_html);
        flask_moment_render_all();
        alert(data.message_html);
        scrollToBottom();
        activateSemantics();
    });


    // 提交新群聊消息
    $('#group-meg-submit').on('click', function () {
        var $message_textarea = $('#message-textarea');
        var message = $message_textarea.val();
        if (message.trim() !== '') {
            socket.emit('room_message', message, room_id);
            $message_textarea.val('');
        }
    });





    function messageNotify(data) {
        if (Notification.permission !== "granted")
            Notification.requestPermission();
        else {
            var notification = new Notification("Message from " + data.nickname, {
                icon: data.gravatar,
                body: data.message_body.replace(/(<([^>]+)>)/ig, "")
            });

            notification.onclick = function () {
                window.open(root_url);
            };
            setTimeout(function () {
                notification.close()
            }, 4000);
        }
    }

    function activateSemantics() {
        $('.ui.dropdown').dropdown();
        $('.ui.checkbox').checkbox();

        $('.message .close').on('click', function () {
            $(this).closest('.message').transition('fade');
        });

        $('#toggle-sidebar').on('click', function () {
            $('.menu.sidebar').sidebar('setting', 'transition', 'overlay').sidebar('toggle');
        });

        $('#show-help-modal').on('click', function () {
            $('.ui.modal.help').modal({blurring: true}).modal('show');
        });

        $('#show-snippet-modal').on('click', function () {
            $('.ui.modal.snippet').modal({blurring: true}).modal('show');
        });
    }

    function init() {
        // desktop notification
        document.addEventListener('DOMContentLoaded', function () {
            if (!Notification) {
                alert('Desktop notifications not available in your browser.');
                return;
            }

            if (Notification.permission !== "granted")
                Notification.requestPermission();
        });

        $(window).focus(function () {
            message_count = 0;
            document.title = 'YouGuoQi';
        });

        activateSemantics();
        scrollToBottom();
    }

    init();

});
