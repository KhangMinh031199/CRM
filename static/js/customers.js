$(document).ready(function () {

    var shop_id_select = $("#shop_id_select").val();
    var merchant_id = $("#merchant_id").val();
    $('#customers_load').hide();


    $("#customer_input").keypress(function (event) {
        var keycode = event.keyCode || event.which;
        if (keycode == '13') {
            if ($("#customer_input").val().length >= 2) {
                var data = {'text_query': $("#customer_input").val()};
                $('#list_data').hide();
                $('#customers_load').show();
                $.ajax({
                    url: "/search_customers",
                    type: 'POST',
                    data: data,
                    success: function (data) {
                        $("#list_data").empty();
                        $("#list_data").append(data);
                        $('#customers_load').hide();
                        $('#list_data').show();
                    }
                });
                return false;

            } else {
                swal(ngettext("Ban_can_nhap_thong_tin_lon_hon_2_ky_tu"), " ",
                    "info")
            }
            return false;
        }

    });

    $('#locations_selects').select2({
        dropdownAutoWidth: true
    });

    $('textarea').each(function () {
            $(this).val($(this).val().trim());
        }
    );
    $('input').each(function () {
            $(this).val($(this).val().trim());
        }
    );
    if ($("#ex_ranks").length > 0) {
        $("#ranks").val($("#ex_ranks").val());
    }
    if ($("#ex_gender").length > 0) {
        $("#gender").val($("#ex_gender").val());
    }

    if ($("#ex_employee").length > 0) {
        $("#employee_check").val($("#ex_employee").val());
    }

    if ($("#ex_from_date").length > 0 && $("#ex_from_date").val().length > 0 && $("#ex_from_date").val() != 'None') {
        flatpickr("#from_date", {
            enableTime: false,
            defaultDate: $("#ex_from_date").val(),
            dateFormat: "d-m-Y"
        });
    } else {
        flatpickr("#from_date", {
            enableTime: false,
            dateFormat: "d-m-Y"
        });
    }
    if ($("#ex_from_date_bday").length > 0 && $("#ex_from_date_bday").val().length > 0 && $("#ex_from_date_bday").val() != 'None') {
        flatpickr("#bday_from_date", {
            enableTime: false,
            defaultDate: $("#ex_from_date_bday").val(),
            dateFormat: "d-m-Y"
        });
    } else {
        flatpickr("#bday_from_date", {
            enableTime: false,
            dateFormat: "d-m-Y"
        });
    }
    if ($("#ex_to_date").length > 0 && $("#ex_to_date").val().length > 0 && $("#ex_to_date").val() != 'None') {
        flatpickr("#to_date", {
            enableTime: false,
            defaultDate: $("#ex_to_date").val(),
            dateFormat: "d-m-Y"
        });
    } else {
        flatpickr("#to_date", {
            enableTime: false,
            dateFormat: "d-m-Y"
        });
    }
    if ($("#ex_to_date_bday").length > 0 && $("#ex_to_date_bday").val().length > 0 && $("#ex_to_date_bday").val() != 'None') {
        flatpickr("#bday_to_date", {
            enableTime: false,
            defaultDate: $("#ex_to_date_bday").val(),
            dateFormat: "d-m-Y"
        });
    } else {
        flatpickr("#bday_to_date", {
            enableTime: false,
            dateFormat: "d-m-Y"
        });
    }

    $("#export_customers").click(function () {
        var url_export = "/export_customers";
        if (shop_id_select != 'all') {
            url_export = '/export_customers?loc_id=' + shop_id_select;

        }


        $.ajax({
            url: url_export,
            type: 'POST',
            data: $("#form_cus").serialize(),
            success: function (response) {
                swal(ngettext("File_dang_duoc_xu_ly,_vui_long_kiem_tra_email_hoac_truy_cap_quan_ly_File_sau_3-5_phut_nua."), '', 'success');
            },
            error: function (xhr, desc, err) {
                swal(ngettext("Co_loi_xay_ra,_thu_lai_sau"), " ", "error");


            }
        });

    });

    $("#min_visit").keypress(function (e) {
        if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            $("#errmsgn").html(ngettext("Nhap_so")).show().fadeOut("slow");
            return false;
        }
    });
    $("#max_visit").keypress(function (e) {
        if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            $("#errmsgx").html(ngettext("Nhap_so")).show().fadeOut("slow");
            return false;
        }
    });

    $("#lost_day").keypress(function (e) {
        if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            $("#errmsg1").html(ngettext("Chi_duoc_nhap_so")).show().fadeOut("slow");
            return false;
        }
    });

    $("#view_data").click(function (e) {
        e.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        var bday_from_date = $("#bday_from_date").val();
        var bday_to_date = $("#bday_to_date").val();
        var min_visit = $("#min_visit").val();
        var max_visit = $("#max_visit").val();
        var lost_day = $("#lost_day").val();

        if (from_date && from_date.length > 0) {
            if (!to_date || to_date.length == 0) {

                swal('Bạn chưa chọn ngày kết thúc', '', "error");
                return false;
            }
            var from_date_obj = moment(from_date, "DD-MM-YYYY").valueOf();
            var to_date_obj = moment(to_date, "DD-MM-YYYY").valueOf();
            if (to_date_obj < from_date_obj) {
                swal('Ngày bắt đầu phải nhỏ hơn ngày kết thúc', '', "error");
                return false;
            }

        }
        if (to_date && to_date.length > 0) {
            if (!from_date || from_date.length == 0) {

                swal('Bạn chưa chọn ngày bắt đầu', '', "error");
                return false;
            }
            var from_date_obj = moment(from_date, "DD-MM-YYYY").valueOf();
            var to_date_obj = moment(to_date, "DD-MM-YYYY").valueOf();
            if (to_date_obj < from_date_obj) {
                swal('Ngày bắt đầu phải nhỏ hơn ngày kết thúc', '', "error");
                return false;
            }

        }
        if (bday_from_date && bday_from_date.length > 0) {
            if (!bday_to_date || bday_to_date.length == 0) {

                swal('Bạn chưa chọn khoảng ngày có sinh nhật', '', "error");
                return false;
            }
            var bday_from_date_obj = moment(bday_from_date, "DD-MM-YYYY").valueOf();
            var bday_to_date_obj = moment(bday_to_date, "DD-MM-YYYY").valueOf();
            if (bday_to_date_obj < bday_from_date_obj) {
                swal('Ngày bắt đầu phải nhỏ hơn ngày kết thúc', '', "error");
                return false;
            }

        }
        if (bday_to_date && bday_to_date.length > 0) {
            if (!bday_from_date || bday_from_date.length == 0) {

                swal('Bạn chưa chọn khoảng ngày có sinh nhật', '', "error");
                return false;
            }
            var bday_from_date_obj = moment(bday_from_date, "DD-MM-YYYY").valueOf();
            var bday_to_date_obj = moment(bday_to_date, "DD-MM-YYYY").valueOf();
            if (bday_to_date_obj < bday_from_date_obj) {
                swal('Ngày bắt đầu phải nhỏ hơn ngày kết thúc', '', "error");
                return false;
            }

        }

        if (min_visit && min_visit.length > 0) {
            var min_visit_obj = min_visit.trim();
            console.log("what the hell");
            console.log(parseInt(min_visit_obj));
            if (!parseInt(min_visit_obj)) {
                if (parseInt(min_visit_obj) <= 0) {

                    swal('Lượt đến phải lớn hơn 0', '', "error");
                } else {
                    swal('Lượt đến phải dạng số', '', "error");
                }
                return false;
            }

        }
        if (max_visit && max_visit.length > 0) {
            var max_visit_obj = max_visit.trim();
            if (!parseInt(max_visit_obj)) {
                if (parseInt(max_visit_obj) <= 0) {

                    swal('Lượt đến phải lớn hơn 0', '', "error");
                } else {
                    swal('Lượt đến phải dạng số', '', "error");
                }
                return false;
            }

        }
        if (lost_day && lost_day.length > 0) {
            var lost_day_obj = lost_day.trim();
            if (!parseInt(lost_day_obj)) {
                if (parseInt(lost_day_obj) <= 0) {

                    swal('Ngày chưa quay lại phải lớn hơn 0', '', "error");
                } else {
                    swal('Ngày chưa quay lại phải dạng số', '', "error");
                }
                return false;
            }

        }


        var form = $("#form_cus");
        var url = form.attr('action');
        $("#customers_loading_view").show();
        $("#list_data").empty();
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            success: function (data) {
                $("#customers_loading_view").hide();

                $("#list_data").html(data);
            }
        });


    });
    $("#reset_filter").click(function () {

        $('form[id="form_cus"]')
            .find(':radio, :checkbox').removeAttr('checked').end()
            .find('textarea, :text, select').val('');
        $("#tags_selects").val('');
        $('#tags_selects').trigger('change');
        var form = $("#form_cus");
        var url = form.attr('action');
        $("#customers_loading_view").show();
        $("#list_data").empty();
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            success: function (data) {
                $("#customers_loading_view").hide();

                $("#list_data").html(data);
            }
        });
        return false;
    });
    $('#tags_selects').select2({
        dropdownAutoWidth: true
    });

    $('#tags_selects').on("change", function (e) {
        if ($('#tags_selects').val()) {
            $('#select_tags_filter').val($('#tags_selects').val().toString());
        } else {
            $('#select_tags_filter').val("");
        }
    });
    $('#shop_in_mer').select2();
    $('#cus_in_mer').select2({
        dropdownParent: $("#new_customers_modal")
    });
    $('#shop_in_mer').val(shop_id_select).trigger('change');
    $('#shop_in_mer').on("change", function (e) {
        var shop_id = $('#shop_in_mer').val();
        var url = "/customers?loc_id=" + shop_id;
        $(location).attr('href', url);
    });

    var source_tags = $("#source_tags_filter").val();
    if (source_tags && source_tags.length > 0 && source_tags.toString() != 'None') {
        source_tags = source_tags.replace(/u'/g, '"')
        var data_soure_tags = JSON.parse(source_tags.replace(/\'/g, '"'));
        $("#tags_selects").val(data_soure_tags);
        $('#tags_selects').trigger('change');
        $('#select_tags_filter').val($('#tags_selects').val().toString());
    }


    flatpickr("#birthday", {
        enableTime: false,
        dateFormat: "d-m"
    });

    $('#new_tags_selects').select2({
        dropdownAutoWidth: true,
        dropdownParent: $("#new_customers_modal")
    });
    $('#new_tags_selects').on("change", function (e) {
        if ($('#new_tags_selects').val()) {
            $('#new_select_tags_filter').val($('#new_tags_selects').val());
        } else {
            $('#new_select_tags_filter').val("");
        }
    });
    $("#new_customer").click(function () {
        var name = $("#firstName").val();
        var phone = $("#new_phone").val();
        var email = $("#new_email").val();
        var birthday = $("#birthday").val();
        if (name.length == 0) {
            swal(ngettext("Ten_khach_hang_khong_duoc_de_trong"), " ", "error");
            return false;
        }
        if (phone.length == 0 && email.length == 0) {
            swal(ngettext("So_dien_thoai_hoac_Email_khong_duoc_de_trong"), " ", "error");
            return false;
        }

        if ($('#new_tags_selects').val()) {
            $('#new_select_tags_filter').val($('#new_tags_selects').val());
        } else {
            $('#new_select_tags_filter').val("");
        }
        $.ajax({
            url: $("#new_customer_fr").attr("action"),
            type: $("#new_customer_fr").attr("method"),
            data: $("#new_customer_fr").serialize(),
            success: function (response) {
                var returnedData = JSON.parse(response);
                if ('error' in returnedData) {
                    swal(returnedData['error'], " ", "error");
                } else {
                    swal(ngettext("Them_khach_hang_thanh_cong"), '', 'success');
                    location.reload();
                }

            },
            error: function (xhr, desc, err) {
                swal(ngettext("Co_loi_xay_ra,_thu_lai_sau"), " ", "error");


            }
        });

        return false;


    });

    $(document).on("click", '.detail_customer', function(event) {
        var cus_id = $(this).attr('user_id');
        $('.modal_loading').show();
        $('#customer_details').modal('toggle');
        $('#customer_details_body').empty();
        $.ajax({
            type: 'GET',
            url: '/' + merchant_id + '/customers/' + cus_id,
            success: function (response) {
                $('.modal_loading').hide();
                $('#customer_details_body').html(response);
            }
        })


    });

    $(document).on("click", '.visit_log', function(event) {

        var cus_id = $(this).attr('user_id');
        $('.modal_loading').show();
        $('#visits_details').modal('toggle');
        $('#visits_details_body').empty();
        $.ajax({
            type: 'GET',
            url: '/' + merchant_id + '/visit_log/' + cus_id,
            success: function (response) {
                $('.modal_loading').hide();
                $('#visits_details_body').html(response);
            }
        })


    });
    $(document).on("click", '.remove_customer', function(event) {
        var cus_id = $(this).attr('user_id')
        Swal.fire({
            title: ngettext("Ban_co_chac_chan_muon_xoa_khach_hang?"),

            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
focusCancel: true,
            cancelButtonColor: '#d33',
            confirmButtonText: 'Có!',
            cancelButtonText: ngettext("Khong!")
        }).then((result) => {
            if (result.value) {
                if (shop_id_select != 'all') {
                    var url_submit = '/user/' + cus_id + '/unsubscribe?loc_id=' + shop_id_select;
                    $.ajax({
                        url: url_submit,
                        type: 'GET',

                        success: function (data) {
                            swal(ngettext("Xoa_khach_hang_thanh_cong"), '', 'success');
                            location.reload();
                        }
                    });
                } else {
                    var url_submit = '/user/' + cus_id + '/unsubscribe';
                    $.ajax({
                        url: url_submit,
                        type: 'GET',

                        success: function (data) {
                            swal(ngettext("Xoa_khach_hang_thanh_cong"), '', 'success');
                            location.reload();
                        }
                    });

                }
            }

            return false;

        });
    });

    $(".edit_customer").click(function () {
        var cus_id = $(this).attr('user_id')
        var name = $("#firstName_" + cus_id).val();
        var phone = $("#new_phone_" + cus_id).val();
        var email = $("#new_email_" + cus_id).val();
        var birthday = $("#birthday_" + cus_id).val();
        var year = $("#year_birth_" + cus_id).val();
        var real_tags_filter = $("#new_select_tags_filter_" + cus_id).val();
        var company_role = $("#company_role_" + cus_id).val();
        var company = $("#company_" + cus_id).val();
        var location_id = $("#companyName_" + cus_id).val();
        var gender = $("#gender_" + cus_id).val();
        var is_employee = $("#is_employee_" + cus_id).is(":checked");
        var note = $("#bio_" + cus_id).val();
        var address = $("#companyName_" + cus_id).val();
        var facebook = $("#facebook_" + cus_id).val();
        var twitter = $("#socialProfile_" + cus_id).val();

        if (name.length == 0) {
            swal(ngettext("Ten_khach_hang_khong_duoc_de_trong"), " ", "error");
            return false;

        }
        if (phone.length == 0 && email.length == 0) {
            swal(ngettext("So_dien_thoai_hoac_Email_khong_duoc_de_trong"), " ", "error");
            return false;
        }
        var data = {
            'name': name,
            'phone': phone,
            'email': email,
            'birthday': birthday,
            'year_birth': year,
            'real_tags_filter': real_tags_filter,
            'location_id': location_id,
            'gender': gender,
            'is_employee': is_employee,
            'note': note,
            'address': address,
            'facebook': facebook,
            'twitter': twitter,
            'company_role': company_role,
            'company': company
        };
        $.ajax({
            url: $("#new_customer_fr_" + cus_id).attr("action"),
            type: $("#new_customer_fr_" + cus_id).attr("method"),
            data: data,

            success: function (response) {
                var returnedData = JSON.parse(response);
                if ('error' in returnedData) {

                    swal(returnedData['error'], " ", "error");
                } else {
                    swal(ngettext("Cap_nhat_khach_hang_thanh_cong"), '', 'success');
                    location.reload();
                }

            },
            error: function (xhr, desc, err) {
                swal(ngettext("Co_loi_xay_ra,_thu_lai_sau"), " ", "error");


            }
        });
        return false;

    });


   

});