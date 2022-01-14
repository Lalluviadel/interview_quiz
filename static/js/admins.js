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

});
