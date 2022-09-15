/**
 * Contains javascript scripts for asynchronous operation of site elements.
 */

window.addEventListener('load', (e) => {

    /**
     * Allows you to make a category available/unavailable at the click of a button
     * without reloading the entire page, while preserving the original pagination.
     * Works in the admin panel on the category list page.
     */
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

    /**
     * Allows you to make a question available/unavailable at the click of a button
     * without reloading the entire page, while preserving the original pagination.
     * Works in the admin panel on the question list page.
     */
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

    /**
     * Allows you to make a user active/inactive at the click of a button
     * without reloading the entire page, while preserving the original pagination.
     * Works in the admin panel on the user list page.
     */
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

    /**
     * Allows you to give the user the rights of a superuser/deprive of these rights
     * at the touch of a button without reloading the entire page, while preserving the original pagination.
     * Works in the admin panel on the user list page.
     */
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

    /**
     * Allows you to make a user active/inactive at the click of a button
     * without reloading the entire page, while preserving the original pagination.
     * Works in the admin panel on the users list page.
     */
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

    /**
     * Works with any pictures except category pictures and pictures on the main
     * page of the site. When you click on the image, it will be opened in
     * a modular window and enlarged for the convenience of the user.
     */
    $('div.thumbnail').click(function (e) {
        e.preventDefault();
        $('#image-modal .modal-body img').attr('src', $(this).find('img').attr('src'));
        let height = (window.innerWidth > 0) ? window.innerHeight : screen.height;
        if (height >= 900) {
            $("#image-modal").modal('show');
        }
    });

    /**
     * Closes the modal window of the image when you click on it.
     * This modal window is used to zoom in (zoom in) the picture of a question or post,
     * so that it is more convenient for the user to view the details.
     */
    $('#image-modal .modal-body img').on('click', function () {
        $("#image-modal").modal('hide')
    });

    /**
     * If the user has not canceled this earlier, he will be shown a modal window
     * with information about the order of testing before starting the test.
     */
    if (typeof user_info !== "undefined") {
        let height = (window.innerWidth > 0) ? window.innerHeight : screen.height;
        if (user_info === 1 && height >= 900) {
            e.preventDefault();
            console.log('1', height)
            $("#info-modal").modal('show');
        }
    }

    /**
     * Closes the modal window with information about the order of passing
     * the test before it starts. If a user checks the checkbox in
     * the information window, this will start the process of changing
     * the record in the database about this user so that the information
     * window no longer appears for him.
     * Then another modal window will appear with a message that the information
     * will no longer be displayed and will automatically close after 3 seconds.
     */
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
                        $(element).html(data.result);
                        setTimeout(function () {
                                $("#info-modal").modal('hide');
                            },
                            3000);
                        setTimeout(function () {
                                $("#form-start-test").submit();
                            },
                            3500);
                    }
                },
            });
        } else {
            $("#info-modal").modal('hide');
            $("#form-start-test").submit();
        }
    });

    /**
     * Works when the user creates his own question or post (universalized).
     * When filling out the form and submitting it, it transmits the form data
     * and uploaded images to the corresponding view. Based on the results of
     * the data received, either a form filled in by the user with an error
     * indication will be displayed, or a modal window will appear with a message
     * about the successful creation of user content.
     */
    $('input.confirm-action').click(function (e) {
        let data = new FormData();
        $('.user-action').find('input, textarea, select').each(function () {
            data.append(this.name, $(this).val());
        });
        if (location.pathname.includes('posts')) {
            url = '/users/posts_create/';
            data.append('image', document.getElementById('post_image').files[0]);
        } else {
            url = '/users/question_create/';
            let images = ['image_01', 'image_02', 'image_03'];
            images.forEach((el, index) => {
                data.append(`${el}`, document.getElementById(`${el}`).files[0]);
            });
        }

        $.ajax({
            type: 'POST',
            data: data,
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: url,
            processData: false,
            contentType: false,
            dataType: 'JSON',
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

    /**
     * Closing the modal window with a message about the
     * successful creation of user content and switching
     * to the user profile.
     */
    $('#user-action-modal').on('click', function () {
        $("#user-action-modal").modal('hide')
        window.location.href = '/users/profile/'
    });

    /**
     * It works when the user creates an email message for the admin.
     * When submitting a form, its data is transmitted to the view via AJAX.
     * Based on the results of the data received, either a form with
     * previously filled in data and an error indication will be loaded,
     * or a modal window will appear with information that the message has been sent.
     */
    $('input.confirm-action-letter').click(function (e) {
        let data = {}
        $('.user-letter').find('input, textarea, select').each(function () {
            data[this.name] = $(this).val();
        });
        $.ajax({
            type: 'POST',
            data: data,
            headers: {'X-CSRF-TOKEN': csrftoken},
            url: '/users/write_to_admin/',
            success: (data) => {
                if (data.result) {
                    $('.user-letter').html(data.result)
                } else {
                    $("#user-letter-modal").modal('show');
                }
            }
        });
    });

    /**
     * Closes the message about the successful sending of the message
     * and goes to the user profile page.
     */
    $('#user-letter-modal').on('click', function () {
        $("#user-letter-modal").modal('hide')
        window.location.href = '/users/profile/'
    });

    /**
     * It works when the user edits his profile data.
     * Loads part of the profile page to display the edit form.
     */
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

    /**
     * Receives data from the user's profile editing form. If the form is valid,
     * the changes will be saved. Loads part of the page with user information.
     */
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

    /**
     * It works when a user edits an avatar on their profile page.
     * Loads part of the page with the avatar editing form.
     */
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

    /**
     * Retrieves data from the avatar editing form and saves a new avatar.
     * If the user tries to save the form without selecting an image,
     * the previous avatar will be left. Loads part of the page with
     * the user's avatar.
     */
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

    /**
     * If the user goes to his profile page, the menu loads the buttons
     * of user actions that are available only on this page.
     */
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

    /**
     * Works in the admin area. Monitors the object deletion mode.
     * When switching from the default "Deactivation" mode to the
     * "Deletion" mode (complete deletion of an object and a record in
     * the database), it displays a warning about this in the deletion panel
     * without reloading the page.
     */
    $('#deact_delete').click(function (e) {
        let checkBox = document.getElementById("option2");
        let text = document.getElementById("text");
        if (checkBox.checked === true) {
            text.style.display = "block";
        } else {
            text.style.display = "none";
        }
    })

    /**
     * It works in the process of testing the user with the selected
     * response time limit mode. Monitors the remaining time, displays
     * it on the page without reloading it. After 15 seconds, it navigates
     * to a page with a message that the time has expired.
     */
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

    /**
     * A small decoration of the main page. Changes the inscription
     * "Check yourself" ("Проверь себя") to "Believe in yourself"
     * ("Верь в себя") after a short period of time.
     */
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

    /**
     * Works in the admin area. Tracks the current page and if it relates
     * to working with posts, then the search bar changes the placeholder
     * and the action when using it to search for posts.
     */
    if ((location.pathname === '/myadmin/posts/') || (location.pathname === '/myadmin/search/post/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск по статьям')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/post/')
    }

    /**
     * Works in the admin area. Tracks the current page and if it relates
     * to working with users, then the search bar changes the placeholder
     * and the action when using it to search for users.
     */
    if ((location.pathname === '/myadmin/users/') || (location.pathname === '/myadmin/search/user/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск пользователей')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/user/')
    }

    /**
     * Works in the admin area. Tracks the current page and if it relates
     * to working with categories, then the search bar changes the placeholder
     * and the action when using it to search for categories.
     */
    if ((location.pathname === '/myadmin/categories/') || (location.pathname === '/myadmin/search/cat/')) {
        $('#admins_search_panel').attr('placeholder', 'Поиск по категориям')
        $('#catcher_admins_search_panel').attr('action', '/myadmin/search/cat/')
    }

});
