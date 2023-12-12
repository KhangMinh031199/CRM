function set_current_step() {
    var step_active = $('ul#page_selector').find('li.active').attr('data-value');
    $("#current_step").val(step_active);
}

function display_config() {
    var current_step = $("#current_step").val();
    if (parseInt(current_step) == 4) {
        $("#step_header").text("Kết nối");
        $("#setting_page").hide();
        $("#page_type_list").hide();
        $("#page_type_div").hide();
        $("#page_type_div_survey").hide();
    } else {
        $("#step_header").text("Bước " + $("#current_step").val());
        var current_type_page = $("#page_type_selects").val();
        $("#setting_page_type").val(current_type_page);
        var arrayPage = ['survey', 'spin', 'woay'];

        if ($.inArray(current_type_page, arrayPage) >= 0) {
            if (current_type_page != "spin") {
                $("#setting_page").hide();
                $("#page_type_div_survey").hide();
                $("#page_type_div").show();
            } if (current_type_page != "survey") {
                $("#setting_page").hide();
                $("#page_type_div_survey").show();
                $("#page_type_div").hide();
            } if (current_type_page != "survey") {
                $("#setting_page").hide();
                $("#page_type_div").hide();
                $("#page_type_div_survey").hide();
            }

        } else if (current_type_page != "0") {
            $("#setting_page").show();
            $("#page_type_div").hide();
            $("#page_type_div_survey").hide();
        } else {
            $("#setting_page").hide();
            $("#page_type_div").hide();
            $("#page_type_div_survey").hide();
        }
    }

}

function checkFields(form) {
    var checks_radios = form.find(':checkbox, :radio');
    var checked = checks_radios.filter(':checked');

    if (checked.length === 0) {
        return false;
    }
    return true;

}

function check_input_empty(form) {
    var count = 0;
    $(form).find(':input[name=link_youtube]').each(function () {
        if ($(this).val().length > 0) {
            count = count + 1;
        }

    });
    if (count == 0) {

        return false;
    }
    return true;
}

function check_images_form(form) {
    var has_selected_file = $(form + ' input[type=file]').filter(function () {
        return $.trim(this.value) != ''
    }).length > 0;

    return has_selected_file;
}

function check_list_select(type_page) {
    if (type_page == "spin") {
        var item_select = $('#page_type_list').val();
    }
    if (type_page == "survey") {
        var item_select = $('#page_type_list_survey').val();
    }
    if (!item_select) {
        return false;
    }
    return true;
}

function check_config_page(type_page) {

    if (type_page == 'collect') {
        var oneFilled = checkFields($('#collect_form'));
        if (!oneFilled) {
            return false;
        }
    }

    if (type_page == 'image') {
        var check_file = check_images_form('#image_form');
        if (!check_file) {
            return false;
        }
    }

    if (type_page == 'slides') {
        var check_file = check_images_form('#slide_form');
        if (!check_file) {
            return false;
        }

    }

    if (['survey', 'spin'].includes(type_page)) {
        return check_list_select(type_page);
    }

    if (type_page == "youtube") {
        var check_file = check_input_empty('#youtube_form');
        if (!check_file) {
            return false;
        }
    }
    return true;

}

function save_step(type_page) {
    var current_step = $("#current_step").val();


    if (parseInt(current_step) == 4) {
        $("#input_type_step_4").val('connect');
    } else {
        $("#input_type_step_" + current_step).val(type_page);
    }


}

function input_modal(step) {
    var element = document.getElementById('modal_body_' + step);
    var html = element.outerHTML;
    var data = { html: html };
    return JSON.stringify(data);
}

$(document).ready(function () {
    var list_redirect_type = ['website', 'mobile_app', 'facebook_page', 'zalo_oa', 'instagram', 'facebook_mess'];
    var merchant_id = $("#merchant_id").val()
    var camp_id = $("#camp_id").val()
    $("#setting_page").hide();
    $("#page_type_div").hide();
    $("#page_type_div_survey").hide();
    $("#connect_success").hide();
    $("#modal_form").modal('hide');
    list_redirect_type.forEach(function (i) {
        $("#auto_" + i).hide();
    });
    $("#hotspot_method").on('change', function () {
        var hotspot_method = $("#hotspot_method").val();
        if (hotspot_method == 'profile_code') {
            $("#default_code_div").hide();
        } else {
            $("#default_code_div").show();
        }
    });
    var redirect_type = $("#redirect_type").val();
    list_redirect_type.forEach(function (i) {
            if (i == redirect_type) {
                $("#auto_" + i).show();
            } else {
                $("#auto_" + i).hide();
            }
        })
    // $("#display_coupon").on('change', function () {
    //     if (this.checked == true) {
    //         $("#default_coupon").hide();
    //     } else {
    //         $("#default_coupon").show();
    //     }

    // });
    var ex_redirect_type = $("#ex_redirect_type").val();
    if (ex_redirect_type && ex_redirect_type.length > 0) {
        $("#redirect_type").val(ex_redirect_type);
        $("#auto_" + ex_redirect_type).show();
    }

    $("#redirect_type").on('change', function () {
        var redirect_type = $("#redirect_type").val();

        list_redirect_type.forEach(function (i) {
            if (i == redirect_type) {
                $("#auto_" + i).show();
            } else {
                $("#auto_" + i).hide();
            }
        })
    });
    $("#modal_image").modal('hide');

    $("#modal_slides").modal('hide');

    $("#modal_youtube").modal('hide');

    $("#modal_list").modal('hide');

    $('textarea').each(function () {
        $(this).val($(this).val().trim());
    });
    $('input').each(function () {
        $(this).val($(this).val().trim());
    });
    set_current_step();
    $.ajax({
        url: "/wifi_ads_detail",
        type: 'POST',
        data: {
            'step': $("#current_step").val(),
            'merchant_id': merchant_id,
            'camp_id': camp_id
        },
        success: function (data) {
            $("#select_type_page").empty();
            $("#select_type_page").append(data);
        }
    });

    $("#card_config_camp").hide();
    $("#card_location_distribution").hide();
    $("#card_setting_campaign").hide();
    $("#config_camp").click(function () {
        $("#card_build_page").hide();
        $("#card_location_distribution").hide();
        $("#card_setting_campaign").hide();
        $("#card_config_camp").show();
        $("#build_page").removeClass("active");
        $("#location_distribution").removeClass("active");
        $("#setting_campaign").removeClass("active");
        // switch this tab on
        $(this).addClass("active");
    });
    $("#build_page").click(function () {
        $("#card_config_camp").hide();
        $("#card_location_distribution").hide();
        $("#card_setting_campaign").hide();
        $("#card_build_page").show();
        $("#config_camp").removeClass("active");
        $("#location_distribution").removeClass("active");
        $("#setting_campaign").removeClass("active");
        // switch this tab on
        $(this).addClass("active");
    });

    $("#location_distribution").click(function () {
        $("#card_config_camp").hide();
        $("#card_setting_campaign").hide();
        $("#card_location_distribution").show();
        $("#card_build_page").hide();
        $("#config_camp").removeClass("active");
        $("#build_page").removeClass("active");
        $("#setting_campaign").removeClass("active");
        // switch this tab on
        $(this).addClass("active");
    });

    $("#setting_campaign").click(function () {
        $("#card_config_camp").hide();
        $("#card_setting_campaign").show();
        $("#card_location_distribution").hide();
        $("#card_build_page").hide();
        $("#config_camp").removeClass("active");
        $("#build_page").removeClass("active");
        $("#location_distribution").removeClass("active");
        // switch this tab on
        $(this).addClass("active");
    });

    $('[data-toggle="buttons"] .btn').on('click', function () {
        // toggle style
        $(this).toggleClass('btn-success btn-danger active');

        // toggle checkbox
        var $chk = $(this).find('[type=checkbox]');
        $chk.prop('checked', !$chk.prop('checked'));

        return false;
    });

    flatpickr("#event_start_picker", {
        enableTime: false,
        dateFormat: "d-m-Y"
    });
    flatpickr("#event_end_picker", {
        enableTime: false,
        dateFormat: "d-m-Y"
    });
    var date_type_select = $("#date_type_select").val()
    if (date_type_select == 'week_day') {
        $("#week_day").show();
        $("#month_day").hide();
        $("#event_day").hide();

    }
    if (date_type_select == 'month_day') {
        $("#week_day").hide();
        $("#month_day").show();
        $("#event_day").hide();

    }
    if (date_type_select == 'event_day') {
        $("#week_day").hide();
        $("#month_day").hide();
        $("#event_day").show();

    }

    $('#date_type_select').on('change', function () {
        var item_select = this.value;
        if (item_select == 'week_day') {
            $("#week_day").show();
            $("#month_day").hide();
            $("#event_day").hide();

        }
        if (item_select == 'month_day') {
            $("#week_day").hide();
            $("#month_day").show();
            $("#event_day").hide();

        }
        if (item_select == 'event_day') {
            $("#week_day").hide();
            $("#month_day").hide();
            $("#event_day").show();

        }

    });
    $("#close").click(function () {
        Swal.fire({
            title: ngettext("Ban_co_chac_chan_muon_dong_khong?"),
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
focusCancel: true,
            cancelButtonColor: '#d33',
            confirmButtonText: ngettext("Co!"),
            cancelButtonText: ngettext("Khong!")
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "/close_wifi_ads",
                    type: 'POST',
                    data: {
                        'merchant_id': merchant_id,
                        'camp_id': camp_id
                    },
                    success: function (data) {
                        location.href = '/wifi_ads';
                    }
                });

            }
        })
    });


    function validate(photo) {
        var file_size = $(photo)[0].files[0].size;
        var file = $(photo).val();
        var exts = ['jpg', 'png', 'jpeg'];
        if (file) {
            var get_ext = file.split('.');
            get_ext = get_ext.reverse();
        if ($.inArray ( get_ext[0].toLowerCase(), exts) > -1){
        if(file_size > 3670016){
                return "big_file";
        }else{
            return true;
            }
        }else {
            return false;
            }
        }

    }

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#view_bg_connect')
                    .attr('src', e.target.result);
            };

            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#background_connect").change(function () {
        var validate_photo = validate(this);
        if (validate_photo == true){
        swal(ngettext("Upload_thanh_cong"), '', 'success');
    $('#view_bg_connect').show();
    readURL(this, 'background_connect');
        } else {
            if (validate_photo == "big_file"){
                swal(ngettext("File_co_kich_thuoc_qua_lon!"), '', 'error');
                return false
            };
        swal(ngettext("File_khong_dung_dinh_dang"), '', 'error');
        $('#background_connect').val('');
        $('#view_bg_connect').hide();

                                }})

    $("#save_connect_success").click(function () {
        // luu thong tin connect page
        var current_step = '4';
        var camp_id = $("#camp_id").val();
        var merchant_id = $("#merchant_id").val();
        var modal_connect = document.getElementById('connect_page');
        var form_connect = new FormData(modal_connect);
        var type_page = 'connect_success';
        var connect_success_page = {};
        var form_data = new FormData();
        form_connect.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if (!Reflect.has(connect_success_page, key)) {
                connect_success_page[key] = value;
                return;
            }
            if (!Array.isArray(connect_success_page[key])) {
                connect_success_page[key] = [connect_success_page[key]];
            }
            connect_success_page[key].push(value);
        });
        form_data.append('connect_success_page', JSON.stringify(connect_success_page))
        form_data.append('img_connect', $('input.img-connect[type=file]')[0].files[0]);
        form_data.append('camp_id', camp_id)
        form_data.append('merchant_id', merchant_id)
        form_data.append('current_step', current_step)
        form_data.append('type_page', 'connect_success')
        $.ajax({
            headers: { "X-CSRFToken": '{{ csrf_token() }}' },
            url: "/save_step_wifi_ads_camp/" + merchant_id + "/" + camp_id,
            type: 'POST',
            data: form_data,
            contentType: false,
            processData: false,
            success: function () {
                var url_preiew = '/preview/' + type_page + '/' + merchant_id + '/' + camp_id + '/4';
                $("#preview").empty();
                bioMp(document.getElementById('preview'), {
                    url: url_preiew,
                    view: 'front',
                    image: '/static/images/iphone_simulator/img_preview_mobile.svg',
                    height: 618,
                    width: 308
                });
                swal(ngettext("Thanh_cong"), '', 'success')
            }
        });
    })


    $("#save_campaign").click(function () {
        var name_campaing = $('#name_camp').val();
        var min_visit = $('#min_visit').val();
        var max_visit = $('#max_visit').val();
        if (name_campaing.length == 0) {
            swal('Bạn chưa nhập tên chiến dịch', '', 'error');
            return false
        };

        if (min_visit.length > 0 && max_visit.length > 0 && parseInt(min_visit) > parseInt(max_visit)) {
            swal('Bạn nhập sai lượt đến', '', 'error');
            return false
        }
        if (min_age.length > 0 && max_age.length > 0 && parseInt(min_age) > parseInt(max_age)) {
            swal('Bạn nhập sai độ tuổi', '', 'error');
            return false
        }
        var type_step_1 = $('#input_type_step_1').val();
        var type_step_2 = $('#input_type_step_2').val();
        var type_step_3 = $('#input_type_step_3').val();
        var type_step_4 = $('#input_type_step_4').val();
        var form_data = new FormData();
        // luu thu tu cac buoc
        form_data.append('step_1', $('#input_type_step_1').val())
        form_data.append('step_2', $('#input_type_step_2').val())
        form_data.append('step_3', $('#input_type_step_3').val())

        // sinh nhat va kich hoat, ten chien dich
        var is_birthday = $('#birthday').is(":checked")
        var active = $('#active').is(":checked")
        var type_camp = $('#type_camp').val()
        form_data.append('active', active)
        form_data.append('birthday', is_birthday)
        form_data.append('name_camp', $('#name_camp').val())
        form_data.append('type_camp', $('#type_camp').val())
        var birthday = $('#birthday').val()
        var active = $('#active').val()

        // nhom khach hang
        var modal_group_customer = document.getElementById('group_customer');
        var form_group_customer = new FormData(modal_group_customer);
        var group_customer = {};
        form_group_customer.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if (!Reflect.has(group_customer, key)) {
                group_customer[key] = value;
                return;
            }
            if (!Array.isArray(group_customer[key])) {
                group_customer[key] = [group_customer[key]];
            }
            group_customer[key].push(value);
        });
        // phan phoi dia diem
        var modal_group_distribution = document.getElementById('group_distribution');
        var form_group_distribution = new FormData(modal_group_distribution);
        var group_distribution = {};
        form_group_distribution.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if (!Reflect.has(group_distribution, key)) {
                group_distribution[key] = value;
                return;
            }
            if (!Array.isArray(group_distribution[key])) {
                group_distribution[key] = [group_distribution[key]];
            }
            group_distribution[key].push(value);
        });
        // cau hinh
        var modal_setting_campaign = document.getElementById('group_setting_campaign');
        var form_setting_campaign = new FormData(modal_setting_campaign);
        var setting_campaign = {};
        form_setting_campaign.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if (!Reflect.has(setting_campaign, key)) {
                setting_campaign[key] = value;
                return;
            }
            if (!Array.isArray(setting_campaign[key])) {
                setting_campaign[key] = [setting_campaign[key]];
            }
            setting_campaign[key].push(value);
        });
        form_data.append('group_customer', JSON.stringify(group_customer))
        form_data.append('group_distribution', JSON.stringify(group_distribution))
        form_data.append('setting_campaign', JSON.stringify(setting_campaign))
        form_data.append('weekday_sun_', $('#weekday_sun').hasClass("active"))
        form_data.append('weekday_mon_', $('#weekday_mon').hasClass("active"))
        form_data.append('weekday_tue_', $('#weekday_tue').hasClass("active"))
        form_data.append('weekday_wed_', $('#weekday_wed').hasClass("active"))
        form_data.append('weekday_thu_', $('#weekday_thu').hasClass("active"))
        form_data.append('weekday_fri_', $('#weekday_fri').hasClass("active"))
        form_data.append('weekday_sat_', $('#weekday_sat').hasClass("active"))

        $.ajax({
            url: "/save_wifi_ads/" + merchant_id + "/" + camp_id,
            type: 'POST',
            data: form_data,
            contentType: false,
            processData: false,
            success: function () {
                swal(ngettext("Thanh_cong"), '', 'success')
                location.href = '/wifi_ads';
            }
        });

    });
    var arr = [];
    $("#view").click(function () {
        var type_step_1 = $('#input_type_step_1').val();
        var type_step_2 = $('#input_type_step_2').val();
        var type_step_3 = $('#input_type_step_3').val();
        var type_step_4 = $('#input_type_step_4').val();
        var arr_view = []
        if(type_step_1 != "0"){
            arr_view.push('1')
        }
        if(type_step_2 != "0"){
            arr_view.push('2')
        }
        if(type_step_3 != "0"){
            arr_view.push('3')
        }
        if(type_step_4 != "0"){
            arr_view.push('4')
        }
        arr = arr_view
        var curr_step_view = "1";
        var type_page = $('#input_type_step_1').val();
        var url_pre
        // var url_pre = '/preview_init_camp/' + shop_id_select + '/0';
        if (type_page == "0") {
            curr_step_view = (parseInt(curr_step_view) + 1).toString();
            type_page = $('#input_type_step_' + curr_step_view).val();
        }
        $('#current_step_view').val(curr_step_view);
        if (type_page == "khai_bao_y_te") {
            var url_pre = '/tokhaiyte/' + shop_id_select
        }
        else if (type_page == "woay") {
            var url_pre = 'https://app.woay.vn/w/8b97ab99-9bdc-417f-978d-1edb1c5efaa3/?shop_id=1';
        }
        else if (type_page == "0") {
            next_step_view();
        }
        else {
            var url_pre = '/preview_ads/' + type_page + '/' + merchant_id + '/' + camp_id + '/' + curr_step_view;
        }
        if (type_page != "0"){
            $("#view_modal_body").empty();
            bioMp(document.getElementById('view_modal_body'), {
                url: url_pre,
                view: 'front',
                image: '/static/images/iphone_simulator/img_preview_mobile.svg',
                height: 618,
                width: 308
            });
            
            if(curr_step_view == "1"){
                $('#prev_step_view').attr('disabled', true);
            }
        }
        
    });


    function next_step_view() {
        var before_step_view = parseInt($('#current_step_view').val());
        var curr_step_view = (before_step_view + 1).toString();
        
        var type_page = $('#input_type_step_' + curr_step_view).val();
        if (type_page == "0") {
            curr_step_view = (parseInt(curr_step_view) + 1).toString();
            type_page = $('#input_type_step_' + curr_step_view).val();
        }
        $('#current_step_view').val(curr_step_view);
        if(curr_step_view == "4"){
            $('#next_step_view').attr('disabled', true);
        }
        if(curr_step_view != "1"){
            $('#prev_step_view').removeAttr("disabled");
        }
        
        $('#current_step_view').val(curr_step_view);
        if (type_page == "khai_bao_y_te") {
            var url_pre = '/tokhaiyte/' + shop_id_select
        }
        else if (type_page == "woay") {
            var url_pre = 'https://app.woay.vn/w/8b97ab99-9bdc-417f-978d-1edb1c5efaa3/?shop_id=1';
        }
        else if (type_page == "0") {
            next_step_view();
        }
        else {
            var url_pre = '/preview_ads/' + type_page + '/' + merchant_id + '/' + camp_id + '/' + curr_step_view;
        }
        if (type_page != "0") {
            $("#view_modal_body").empty();
            bioMp(document.getElementById('view_modal_body'), {
                url: url_pre,
                view: 'front',
                image: '/static/images/iphone_simulator/img_preview_mobile.svg',
                height: 618,
                width: 308
            });
        }
        
        
    }

    function prev_step_view() {
        var before_step_view = parseInt($('#current_step_view').val());
        var curr_step_view = (before_step_view - 1).toString();
        var type_page = $('#input_type_step_' + curr_step_view).val();
        if (type_page == "0") {
            curr_step_view = (parseInt(curr_step_view) - 1).toString();
            type_page = $('#input_type_step_' + curr_step_view).val();
        }
        $('#current_step_view').val(curr_step_view);
        if(curr_step_view == "1" || curr_step_view == arr[0]){
            $('#prev_step_view').attr('disabled', true);
        }
        if(curr_step_view != "4"){
            $('#next_step_view').removeAttr("disabled");
        }
        if (type_page == "khai_bao_y_te") {
            var url_pre = '/tokhaiyte/' + shop_id_select
        }
        else if (type_page == "woay") {
            var url_pre = 'https://app.woay.vn/w/8b97ab99-9bdc-417f-978d-1edb1c5efaa3/?shop_id=1';
        }
        else if (type_page == "0") {
            prev_step_view();
        }
        else {
            var url_pre = '/preview_ads/' + type_page + '/' + merchant_id + '/' + camp_id + '/' + curr_step_view;
        }
        
        if (type_page != "0") {
            $("#view_modal_body").empty();
            bioMp(document.getElementById('view_modal_body'), {
                url: url_pre,
                view: 'front',
                image: '/static/images/iphone_simulator/img_preview_mobile.svg',
                height: 618,
                width: 308
            });
        }
        
    }


    $("#next_step_view").click(function () {
        next_step_view();
    });

    $("#prev_step_view").click(function () {
        prev_step_view();
    });
});