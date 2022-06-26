window.addEventListener('load', (e) => {

    $('#update_cat_catcher').on('click', '#update_cat_btn', (e) => {
        let t_href = e.target;
        let checkBox = document.getElementById("option2");

        let arr = [];
        let elements = document.getElementsByClassName('item-on-page')
        for (let i = 0; i < elements.length; i++) {
            arr[i] = elements[i].attributes['value'].value
        }

        let flag = checkBox.checked;
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            data: {'flag': flag, 'elements': arr},
            url: '/myadmin/categories-delete/' + t_href.name + '/',
            success: (data) => {
                if (data) {
                    $('.table-responsive').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    $('#update_que_catcher').on('click', '#update_que_btn', (e) => {
        let t_href = e.target;
        let checkBox = document.getElementById("option2");

        let arr = [];
        let elements = document.getElementsByClassName('item-on-page')
        for (let i = 0; i < elements.length; i++) {
            arr[i] = elements[i].attributes['value'].value
        }

        let flag = checkBox.checked;
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            data: {
                'flag': flag,
                'elements': arr
            },
            url: '/myadmin/questions-delete/' + t_href.name + '/',
            success: (data) => {
                if (data) {
                    $('.table-responsive').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    $('#update_users_catcher').on('click', '#update_user_btn', (e) => {
        let t_href = e.target;
        let checkBox = document.getElementById("option2");

        let arr = [];
        let elements = document.getElementsByClassName('item-on-page')
        for (let i = 0; i < elements.length; i++) {
            arr[i] = elements[i].attributes['value'].value
        }

        let flag = checkBox.checked;
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            data: {
                'flag': flag,
                'elements': arr
            },
            url: '/myadmin/users-delete/' + t_href.name + '/',
            success: (data) => {
                if (data.result) {
                    $('.table-responsive').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    $('#update_post_catcher').on('click', '#update_post_btn', (e) => {
        let t_href = e.target;
        let checkBox = document.getElementById("option2");

        let arr = [];
        let elements = document.getElementsByClassName('item-on-page')
        for (let i = 0; i < elements.length; i++) {
            arr[i] = elements[i].attributes['value'].value
        }

        let flag = checkBox.checked;
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            data: {
                'flag': flag,
                'elements': arr
            },
            url: '/myadmin/posts-delete/' + t_href.name + '/',
            success: (data) => {
                if (data.result) {
                    $('.table-responsive').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    $('#give_me_a_crown').on('click', '#give_me_a_crown_btn', (e) => {
        let t_href = e.target;

        let arr = [];
        let elements = document.getElementsByClassName('item-on-page')
        for (let i = 0; i < elements.length; i++) {
            arr[i] = elements[i].attributes['value'].value
        }

        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            data: {'elements': arr},
            url: '/myadmin/users-is-staff/' + t_href.name + '/',
            success: (data) => {
                if (data.result) {
                    $('.table-responsive').html(data.result)
                }
            },
        });
        e.preventDefault();
    });
    e.preventDefault();

    $('div.thumbnail').click(function (e) {
        e.preventDefault();
        $('#image-modal .modal-body img').attr('src', $(this).find('img').attr('src'));
        $("#image-modal").modal('show');
    });
    $('#image-modal .modal-body img').on('click', function () {
        $("#image-modal").modal('hide')
    });

    if (typeof user_info !== "undefined") {
        if (user_info === 1) {
            e.preventDefault();
            $("#info-modal").modal('show');
        }
    }
    $('#info-modal #info-close').on('click', function () {
        let checkBox = document.getElementById("no-info");
        let flag = checkBox.checked;
        let element = document.querySelector('.modal-content')

        if (flag === true) {
            $.ajax({
                type: 'POST',
                headers: {'X-CSRF-TOKEN': csrftoken},
                data: {'flag': flag},
                url: '/users/no_info/',
                success: (data) => {
                    if (data.result) {
                        $(element).html(data.result)
                    }
                },
            });
            setTimeout(function () {
                $("#info-modal").modal('hide')
            }, 3000);
        } else {
            $("#info-modal").modal('hide');
        }
        $("#form-start-test").submit();
    });

    $('input.confirm-action').click(function (e) {
        e.preventDefault();
        let data = {};
        $('.user-action').find('input, textarea, select').each(function () {
            data[this.name] = $(this).val();
        });
        url = (location.pathname.includes('posts'))
            ? '/users/posts_create/'
            : '/users/question_create/'
        $.ajax({
            type: 'POST',
            data: data,
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: url,
            success: (data) => {
                if (data.result) {
                    $('.user-activity').html(data.result)
                } else {
                    $("#user-action-modal").modal('show');
                    document.getElementById("user-activity-type").innerHTML = (location.pathname.includes('posts'))
                        ? 'Ваша статья отправлена на премодерацию'
                        : 'Ваш вопрос отправлен на премодерацию'
                }
            }
        });
    });

    $('#user-action-modal').on('click', function () {
        $("#user-action-modal").modal('hide')
        $(".user-action").submit();
    });

    $('input.confirm-action-letter').click(function (e) {
        e.preventDefault();
        $("#user-letter-modal").modal('show');
    });
    $('#user-letter-modal').on('click', function () {
        $("#user-letter-modal").modal('hide')
        $(".user-letter").submit();
    });

    $('#update_profile_catcher').on('click', '#profile_edit', (e) => {
        $.ajax({
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/profile_edit/',
            success: (data) => {
                if (data) {
                    $('#profile_catcher').html(data.result)
                }
            },
        });
        e.preventDefault();
    });
    $('#profile_catcher').on('click', '#profile_submit', (e) => {
        let $data = {};
        $('#profile_form').find('input, textarea, select').each(function () {
            $data[this.name] = $(this).val();
        });
        $.ajax({
            type: 'POST',
            data: $data,
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/profile_edit/',
            success: (data) => {
                if (data) {
                    $('#profile_catcher').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    $('#update_img_catcher').on('click', '#profile_img_edit', (e) => {
        $.ajax({
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/profile_img_edit/',
            success: (data) => {
                if (data) {
                    $('#img_catcher').html(data.result)
                }
            },
        });
        e.preventDefault();
    });
    $('#img_catcher').on('click', '#profile_img_submit', (e) => {
        let img_dict = new FormData();
        img_dict.append("image", document.getElementById('avatar').files[0]);
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/profile_img_edit/',
            data: img_dict,
            processData: false,
            contentType: false,
            dataType: 'JSON',
            success: (data) => {
                if (data) {
                    $('#img_catcher').html(data.result)
                }
            },
        });
        e.preventDefault();
    });

    if (location.pathname === '/users/profile/') {
        let element = document.querySelector('#my_profile')
        $.ajax({
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/profile_buttons/',
            success: (data) => {
                if (data) {
                    $(element).html(data.result)
                }
            },
        });
        e.preventDefault();
    }

    $('#deact_delete').click(function (e) {
        let checkBox = document.getElementById("option2");
        let text = document.getElementById("text");
        if (checkBox.checked === true) {
            text.style.display = "block";
        } else {
            text.style.display = "none";
        }
    })

    if ($("#time_counter").length > 0) {
        time_limit = 15
        setInterval(function () {
            document.getElementById("time_counter").innerHTML = time_limit
            if (time_limit === 0) {
                window.location.href = '/questions/time_is_up/';
            }
            time_limit = time_limit - 1
        }, 1000);
    }

    if (location.pathname === '/') {
        let elem = $('#index-title')
        setTimeout(function () {
            elem.attr('style', 'opacity: 0; transition: opacity 3s;')
        }, 3000);
        setTimeout(function () {
            elem.text('Верь в себя');
            elem.attr('class', 'mt-4 oranged')
        }, 6000);
        setTimeout(function () {
            elem.attr('style', 'opacity: 1; transition: opacity 4s;')
        }, 6500);
        e.preventDefault();
    }

    if ((location.pathname === '/myadmin/posts/') || (location.pathname === '/myadmin/search/post/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск по статьям')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/post/')
    }

    if ((location.pathname === '/myadmin/users/') || (location.pathname === '/myadmin/search/user/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск пользователей')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/user/')
    }

    if ((location.pathname === '/myadmin/categories/') || (location.pathname === '/myadmin/search/cat/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск по категориям')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/cat/')
    }
});
