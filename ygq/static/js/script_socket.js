$(document).ready(function () {
    // var socket = io.connect();
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

    $('.messages').scroll(load_messages);


    // 插入新消息
    socket.on('new message', function (data) {
        // message_count++;
        // if (!document.hasFocus()) {
        //     document.title = '(' + message_count + ') ' + 'YouGuoQi';
        // }
        // if (data.user_id !== current_user_id) {
        //     messageNotify(data);
        // }
        $('.messages').append(data.message_html);
        flask_moment_render_all();
        scrollToBottom();
        activateSemantics();
    });

    // // 插入新房间消息
    // socket.on('new room message', function (data) {
    //     $('.messages').append(data.message_html);
    //     flask_moment_render_all();
    //     scrollToBottom();
    //     activateSemantics();
    // });

    // 插入新配送订单
    socket.on('new delivery', function (data) {
        $('.messages').append(data.message_html);
        flask_moment_render_all();
        scrollToBottom();
        activateSemantics();
    });

    // // 打印状态信息
    // socket.on('status', function(data) {
    //     $('.messages').append(data.message_html);
    //     flask_moment_render_all();
    //     alert(data.message_html);
    //     scrollToBottom();
    //     activateSemantics();
    // });




    // // 打印消息
    // socket.on('message', function(data) {
    //     $('#chat').val($('#chat').val() + data.msg + '\n');
    //     $('#chat').scrollTop($('#chat')[0].scrollHeight);
    // });

    // function new_message(e) {
    //     var $textarea = $('#message-textarea');
    //     var message_body = $textarea.val().trim();  // 获取消息正文
    //     if (e.which === ENTER_KEY && !e.shiftKey && message_body) {
    //         e.preventDefault();  // 阻止默认行为，即换行
    //         socket.emit('new message', message_body);
    //         $textarea.val('')
    //     }
    // }

    // submit message
    // $('#message-textarea').on('keydown', new_message.bind(this));

    // 提交新消息
    $('#meg-submit').on('click', function () {
        var $message_textarea = $('#message-textarea');
        var message = $message_textarea.val();
        var dish_id = $('#dish-id').val();
        if (message.trim() !== '') {
            socket.emit('new message', message, dish_id);
            $message_textarea.val('');
            $('#dish-id').val('');
        }
    });


    // 提交新配送订单
    $('#delivery-submit').on('click', function () {
        var order_id = $('#order-id').val();
        var fare = $('#fare').val();
        if (order_id !== '' && fare !== '') {
            socket.emit('new delivery', order_id, fare);
            $('#order-id').val('');
            $('#fare').val('');
        }
    });


    // // 提交新群聊消息
    // $('#group-meg-submit').on('click', function () {
    //     var $message_textarea = $('#message-textarea');
    //     var message = $message_textarea.val();
    //     if (message.trim() !== '') {
    //         socket.emit('room_message', message, room_id);
    //         $message_textarea.val('');
    //     }
    // });


    // 接单
    $('.messages').on('click', '.delete-button',function () {
        var $this = $(this);
        $.ajax({
            type: 'GET',
            url: $this.data('href'),
            success: function () {
                $this.parent().parent().remove();
            },
            error: function () {
                alert('Oops, something was wrong!')
            }
        });
    });


    // $('#send-button').on('click', function () {
    //     var $mobile_textarea = $('#mobile-message-textarea');
    //     var message = $mobile_textarea.val();
    //     if (message.trim() !== '') {
    //         socket.emit('new message', message);
    //         $mobile_textarea.val('')
    //     }
    // });



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

        // $('.pop-card').popup({
        //     inline: true,
        //     on: 'hover',
        //     hoverable: true,
        //     html: popupLoading,
        //     delay: {
        //         show: 200,
        //         hide: 200
        //     },
        //     onShow: function () {
        //         var popup = this;
        //         popup.html(popupLoading);
        //         $.get({
        //             url: $(popup).prev().data('href')
        //         }).done(function (data) {
        //             popup.html(data);
        //         }).fail(function () {
        //             popup.html('Failed to load profile.');
        //         });
        //     }
        // });
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

    // // delete message
    // $('.messages').on('click', '.delete-button', function () {
    //     var $this = $(this);
    //     $.ajax({
    //         type: 'DELETE',
    //         url: $this.data('href'),
    //         success: function () {
    //             $this.parent().parent().parent().remove();
    //         },
    //         error: function () {
    //             alert('Oops, something was wrong!')
    //         }
    //     });
    // });

    // // delete user
    // $(document).on('click', '.delete-user-button', function () {
    //     var $this = $(this);
    //     $.ajax({
    //         type: 'DELETE',
    //         url: $this.data('href'),
    //         success: function () {
    //             alert('Success, this user is gone!')
    //         },
    //         error: function () {
    //             alert('Oops, something was wrong!')
    //         }
    //     });
    // });

    init();

});
