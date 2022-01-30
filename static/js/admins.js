window.addEventListener('load', (e) => {
    $('#update_cat_catcher').on('click', '#update_cat_btn', (e) => {
        let t_href = e.target;
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
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
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
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
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
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
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
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
        $.ajax({
            type: 'POST',
            headers: {'X-CSRF-TOKEN': csrftoken},
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
            url: '/questions/profile_buttons/',
            success: (data) => {
                if (data) {
                    $(element).html(data.result)
                }
            },
        });
        e.preventDefault();

    }
});
