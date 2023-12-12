$(document).ready(function () {
    $('textarea').each(function () {
            $(this).val($(this).val().trim());
        }
    );
    $('input').each(function () {
            $(this).val($(this).val().trim());
        }
    );


    $('#welcome_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#return_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#loyal_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#lost_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#birthday_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#anoun_locations_selects').select2({
        dropdownAutoWidth: true
    });
    $('#thank_you_locations_selects').select2({
        dropdownAutoWidth: true
    });

     $('#locations_selects').on("change", function (e) {
         var shop_id = $('#locations_selects').val();
         var url = '/marketing_automation/' + shop_id;
         $(location).attr('href',url);
    });

    if ($("#ex_welcome_shops").length > 0) {
        $('#welcome_locations_selects').select2().val(JSON.parse($("#ex_welcome_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#welcome_locations').val($('#welcome_locations_selects').val()
            .toString());
    }
    if ($("#ex_thank_you_shops").length > 0) {
        $('#thank_you_locations_selects').select2().val(JSON.parse($("#ex_thank_you_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#thank_you_locations').val($('#thank_you_locations_selects').val()
            .toString());
    }
    $('#welcome_locations_selects').on("change", function (e) {
        if ($('#welcome_locations_selects').val().length > 0) {
            $('#welcome_locations').val($('#welcome_locations_selects').val()
                .toString());
        } else {
            $('#welcome_locations').val("");
        }
    });
    $('#thank_you_locations_selects').on("change", function (e) {
        if ($('#thank_you_locations_selects').val().length > 0) {
            $('#thank_you_locations').val($('#thank_you_locations_selects').val()
                .toString());
        } else {
            $('#thank_you_locations').val("");
        }
    });

    if ($("#ex_return_shops").length > 0) {
        $('#return_locations_selects').select2().val(JSON.parse($("#ex_return_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#return_locations').val($('#return_locations_selects').val()
            .toString());
    }
    $('#return_locations_selects').on("change", function (e) {
        if ($('#return_locations_selects').val().length > 0) {
            $('#return_locations').val($('#return_locations_selects').val()
                .toString());
        } else {
            $('#return_locations').val("");
        }
    });
    if ($("#ex_loyal_shops").length > 0) {
        $('#loyal_locations_selects').select2().val(JSON.parse($("#ex_loyal_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#loyal_locations').val($('#loyal_locations_selects').val()
            .toString());
    }
    $('#loyal_locations_selects').on("change", function (e) {
        if ($('#loyal_locations_selects').val().length > 0) {
            $('#loyal_locations').val($('#loyal_locations_selects').val()
                .toString());
        } else {
            $('#loyal_locations').val("");
        }
    });
    if ($("#ex_lost_shops").length > 0) {
        $('#lost_locations_selects').select2().val(JSON.parse($("#ex_lost_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#lost_locations').val($('#lost_locations_selects').val()
            .toString());
    }

    $('#lost_locations_selects').on("change", function (e) {
        if ($('#lost_locations_selects').val().length > 0) {
            $('#lost_locations').val($('#lost_locations_selects').val()
                .toString());
        } else {
            $('#lost_locations').val("");
        }
    });

    if ($("#ex_birthday_shops").length > 0) {
        $('#birthday_locations_selects').select2().val(JSON.parse($("#ex_birthday_shops").val().replace(/\'/g, '"'))).trigger("change");
        $('#birthday_locations').val($('#birthday_locations_selects').val()
            .toString());
    }
    $('#birthday_locations_selects').on("change", function (e) {
        if ($('#birthday_locations_selects').val().length > 0) {
            $('#birthday_locations').val($('#birthday_locations_selects').val()
                .toString());
        } else {
            $('#birthday_locations').val("");
        }
    });
    if ($("#ex_anoun_shops").length > 0) {
        $('#anoun_locations_selects').select2().val(JSON.parse($("#ex_anoun_shops").val().replace(/\'/g, '"')))
            .trigger("change");
        $('#anoun_locations').val($('#anoun_locations_selects').val()
            .toString());
    }
    $('#anoun_locations_selects').on("change", function (e) {
        if ($('#anoun_locations_selects').val().length > 0) {
            $('#anoun_locations').val($('#anoun_locations_selects').val()
                .toString());
        } else {
            $('#anoun_locations').val("");
        }
    });

      $('#welcome_type_coupon').select2({
        dropdownAutoWidth: true
    });
       $('#thank_you_type_coupon').select2({
        dropdownAutoWidth: true
    });
      $('#returning_type_coupon').select2({
        dropdownAutoWidth: true
    });
       $('#regular_customer_type_coupon').select2({
        dropdownAutoWidth: true
    });
        $('#one_month_type_coupon').select2({
        dropdownAutoWidth: true
    });
         $('#happy_birthday_type_coupon').select2({
        dropdownAutoWidth: true
    });
          $('#announ_type_coupon').select2({
        dropdownAutoWidth: true
    });

    if ($("#ex_welcome_type_coupon").length > 0) {
        $('#welcome_type_coupon').select2().val($("#ex_welcome_type_coupon").val())
            .trigger("change");
        $('#welcome_coupon').val($('#welcome_type_coupon').val().toString());
    }
    if ($("#ex_thank_you_type_coupon").length > 0) {
        $('#thank_you_type_coupon').select2().val($("#ex_thank_you_type_coupon").val())
            .trigger("change");
        $('#thank_you_coupon').val($('#thank_you_type_coupon').val().toString());
    }
    $('#welcome_type_coupon').on("change", function (e) {
        if ($('#welcome_type_coupon').val().length > 0) {
            $('#welcome_coupon').val($('#welcome_type_coupon').val())
                .toString();
        } else {
            $('#welcome_coupon').val("");
        }
    });
        $('#thank_you_type_coupon').on("change", function (e) {
        if ($('#thank_you_type_coupon').val().length > 0) {
            $('#thank_you_coupon').val($('#thank_you_type_coupon').val())
                .toString();
        } else {
            $('#thank_you_coupon').val("");
        }
    });
    if ($("#ex_returning_type_coupon").length > 0) {
        $('#returning_type_coupon').select2().val($("#ex_returning_type_coupon").val())
            .trigger("change");
        $('#return_coupon').val($('#returning_type_coupon').val().toString());
    }
     $('#returning_type_coupon').on("change", function (e) {
        if ($('#returning_type_coupon').val().length > 0) {
            $('#return_coupon').val($('#returning_type_coupon').val())
                .toString();
        } else {
            $('#return_coupon').val("");
        }
    });
    if ($("#ex_regular_customer_type_coupon").length > 0) {
        $('#regular_customer_type_coupon').select2().val($("#ex_regular_customer_type_coupon").val())
            .trigger("change");
        $('#loyal_coupon').val($('#regular_customer_type_coupon').val().toString());
    }
    $('#regular_customer_type_coupon').on("change", function (e) {
        if ($('#regular_customer_type_coupon').val().length > 0) {
            $('#loyal_coupon').val($('#regular_customer_type_coupon').val())
                .toString();
        } else {
            $('#loyal_coupon').val("");
        }
    });
    if ($("#ex_one_month_type_coupon").length > 0) {
        $('#one_month_type_coupon').select2().val($("#ex_one_month_type_coupon").val())
            .trigger("change");
        $('#lost_coupon').val($('#one_month_type_coupon').val().toString());
    }
    $('#one_month_type_coupon').on("change", function (e) {
        if ($('#one_month_type_coupon').val().length > 0) {
            $('#lost_coupon').val($('#one_month_type_coupon').val())
                .toString();
        } else {
            $('#lost_coupon').val("");
        }
    });
    if ($("#ex_happy_birthday_type_coupon").length > 0) {
        $('#happy_birthday_type_coupon').select2().val($("#ex_happy_birthday_type_coupon").val())
            .trigger("change");
        $('#birthday_coupon').val($('#happy_birthday_type_coupon').val().toString());
    }
    $('#happy_birthday_type_coupon').on("change", function (e) {
        if ($('#happy_birthday_type_coupon').val().length > 0) {
            $('#birthday_coupon').val($('#happy_birthday_type_coupon').val())
                .toString();
        } else {
            $('#birthday_coupon').val("");
        }
    });
    if ($("#ex_announ_type_coupon").length > 0) {
        $('#announ_type_coupon').select2().val($("#ex_announ_type_coupon").val())
            .trigger("change");
        $('#announ_coupon').val($('#announ_type_coupon').val().toString());
    }
    $('#announ_type_coupon').on("change", function (e) {
        if ($('#announ_type_coupon').val().length > 0) {
            $('#announ_coupon').val($('#announ_type_coupon').val())
                .toString();
        } else {
            $('#announ_coupon').val("");
        }
    });
    $("#save_welcome").click(function () {
        $("#welcome_form").submit();

    });
       $("#save_thank_you").click(function () {
        $("#thank_you_form").submit();

    });
    $("#save_return").click(function () {
        $("#return_form").submit();
    });
    $("#save_loyal").click(function () {
        $("#loyal_form").submit();
    });
    $("#save_lost").click(function () {
        $("#lost_form").submit();
    });
    $("#save_birthday").click(function () {
        $("#birthday_form").submit();
    });
    $("#save_anoun").click(function () {
        $("#anoun_form").submit();
    });
    $("#save_sms").click(function () {
        $("#sms_form").submit();
    });
    $("#save_email").click(function () {
        $("#email_form").submit();
    });
    if ($("#ex_welcome_gender").length > 0) {
        $("#welcome_gender").val($("#ex_welcome_gender").val());
    }
       if ($("#ex_thank_you_gender").length > 0) {
        $("#thank_you_gender").val($("#ex_thank_you_gender").val());
    }
    if ($("#ex_return_gender").length > 0) {
        $("#return_gender").val($("#ex_return_gender").val());
    }
    if ($("#ex_loyal_gender").length > 0) {
        $("#loyal_gender").val($("#ex_loyal_gender").val());
    }
    if ($("#ex_lost_gender").length > 0) {
        $("#lost_gender").val($("#ex_lost_gender").val());
    }
    if ($("#ex_happy_birthday_gender").length > 0) {
        $("#happy_birthday_gender").val($("#ex_happy_birthday_gender").val());
    }
    if ($("#ex_anoun_gender").length > 0) {
        $("#anoun_gender").val($("#ex_anoun_gender").val());
    }

    if ($("#ex_welcome_ranks").length > 0) {
        $("#welcome_ranks").val($("#ex_welcome_ranks").val());
    }
    if ($("#ex_thank_you_ranks").length > 0) {
        $("#thank_you_ranks").val($("#ex_thank_you_ranks").val());
    }
    if ($("#ex_return_ranks").length > 0) {
        $("#return_ranks").val($("#ex_return_ranks").val());
    }
    if ($("#ex_loyal_ranks").length > 0) {
        $("#loyal_ranks").val($("#ex_loyal_ranks").val());
    }
    if ($("#ex_lost_ranks").length > 0) {
        $("#lost_ranks").val($("#ex_lost_ranks").val());
    }
    if ($("#ex_happy_birthday_ranks").length > 0) {
        $("#happy_birthday_ranks").val($("#ex_happy_birthday_ranks").val());
    }
    if ($("#ex_anoun_ranks").length > 0) {
        $("#anoun_ranks").val($("#ex_anoun_ranks").val());
    }
    $("#switch_sms_welcome").click(function () {
        $("#welcome_form input[name=active_welcome]").prop('checked', $("#quick_active_welcome").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#welcome_form").attr('action'),
            data: $('#welcome_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_thank_you").click(function () {
        $("#thank_you_form input[name=active_thank_you]").prop('checked', $("#quick_active_thank_you").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#thank_you_form").attr('action'),
            data: $('#thank_you_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_return").click(function () {
        $("#return_form input[name=active_returning]").prop('checked', $("#quick_active_return").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#return_form").attr('action'),
            data: $('#return_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_loyal").click(function () {
        $("#loyal_form input[name=active_regular_cus]").prop('checked', $("#quick_active_loyal").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#loyal_form").attr('action'),
            data: $('#loyal_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_lost").click(function () {
        $("#lost_form input[name=active_one_month]").prop('checked', $("#quick_active_lost").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#lost_form").attr('action'),
            data: $('#lost_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_birthday").click(function () {
        $("#birthday_form input[name=active_birthday]").prop
        ('checked', $
        ("#quick_active_birthday").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#birthday_form").attr('action'),
            data: $('#birthday_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_sms_announ").click(function () {
        $("#anoun_form input[name=active_announ]").prop('checked', $("#quick_active_announ").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#anoun_form").attr('action'),
            data: $('#anoun_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });

    $("#switch_enable_welcome").click(function () {
        $("#welcome_form input[name=enable_welcome]").prop('checked', $("#quick_enable_welcome").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#welcome_form").attr('action'),
            data: $('#welcome_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
     $("#switch_enable_thank_you").click(function () {
        $("#thank_you_form input[name=enable_thank_you]").prop('checked', $("#quick_enable_thank_you").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#thank_you_form").attr('action'),
            data: $('#thank_you_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_enable_return").click(function () {
        $("#return_form input[name=enable_return]").prop('checked', $("#quick_enable_return").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#return_form").attr('action'),
            data: $('#return_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_enable_loyal").click(function () {
        $("#loyal_form input[name=enable_loyal]").prop('checked', $("#quick_enable_loyal").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#loyal_form").attr('action'),
            data: $('#loyal_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_enable_lost").click(function () {
        $("#lost_form input[name=enable_lost]").prop('checked', $("#quick_enable_lost").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#lost_form").attr('action'),
            data: $('#lost_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_enable_birthday").click(function () {
        $("#birthday_form input[name=enable_birthday]").prop
        ('checked', $
        ("#quick_enable_birthday").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#birthday_form").attr('action'),
            data: $('#birthday_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_enable_announ").click(function () {
        $("#anoun_form input[name=enable_announ]").prop('checked', $("#quick_enable_announ").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#anoun_form").attr('action'),
            data: $('#anoun_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });

    $("#switch_zalo_welcome").click(function () {
        $("#welcome_form input[name=zalo_welcome]").prop('checked', $("#quick_zalo_welcome").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#welcome_form").attr('action'),
            data: $('#welcome_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_thank_you").click(function () {
        $("#thank_you_form input[name=zalo_thank_you]").prop('checked', $("#quick_zalo_thank_you").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#thank_you_form").attr('action'),
            data: $('#thank_you_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_return").click(function () {
        $("#return_form input[name=zalo_return]").prop('checked', $("#quick_zalo_return").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#return_form").attr('action'),
            data: $('#return_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_loyal").click(function () {
        $("#loyal_form input[name=zalo_loyal]").prop('checked', $("#quick_zalo_loyal").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#loyal_form").attr('action'),
            data: $('#loyal_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_lost").click(function () {
        $("#lost_form input[name=zalo_lost]").prop('checked', $("#quick_zalo_lost").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#lost_form").attr('action'),
            data: $('#lost_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_birthday").click(function () {
        $("#birthday_form input[name=zalo_happy_birthday]").prop
        ('checked', $
        ("#quick_zalo_birthday").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#birthday_form").attr('action'),
            data: $('#birthday_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_zalo_announ").click(function () {
        $("#anoun_form input[name=zalo_announcement]").prop('checked', $("#quick_zalo_announ").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#anoun_form").attr('action'),
            data: $('#anoun_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });

    $("#switch_mail_welcome").click(function () {
        $("#welcome_form input[name=mail_welcome]").prop('checked', $("#quick_mail_welcome").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#welcome_form").attr('action'),
            data: $('#welcome_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
     $("#switch_mail_thank_you").click(function () {
        $("#thank_you_form input[name=mail_thank_you]").prop('checked', $("#quick_mail_thank_you").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#thank_you_form").attr('action'),
            data: $('#thank_you_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_mail_return").click(function () {
        $("#return_form input[name=mail_return]").prop('checked', $("#quick_mail_return").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#return_form").attr('action'),
            data: $('#return_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_mail_loyal").click(function () {
        $("#loyal_form input[name=mail_loyal]").prop('checked', $("#quick_mail_loyal").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#loyal_form").attr('action'),
            data: $('#loyal_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_mail_lost").click(function () {
        $("#lost_form input[name=mail_lost]").prop('checked', $("#quick_mail_lost").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#lost_form").attr('action'),
            data: $('#lost_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_mail_birthday").click(function () {
        $("#birthday_form input[name=mail_happy_birthday]").prop('checked', $("#quick_mail_birthday").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#birthday_form").attr('action'),
            data: $('#birthday_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });
    $("#switch_mail_announ").click(function () {
        $("#anoun_form input[name=mail_announcement]").prop('checked', $("#quick_mail_announ").is(":checked"));
        $.ajax({
            type: 'post',
            url: $("#anoun_form").attr('action'),
            data: $('#anoun_form').serialize(),
            success: function () {
                swal("Cập nhật thành công", " ", "success")

            }
        });
    });

       if($("#ex_sms_provider").length > 0){
                $("#sms_provider").val($("#ex_sms_provider").val());
                $("#sms_provider").trigger('change');
            }

    $("#save_welcome_mail").click(function () {
        $("#welcome_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#welcome_content_mail')).catch(
            error => { console.error( error ); });
     ClassicEditor.create(
        document.querySelector('#thank_you_content_mail')).catch(
            error => { console.error( error ); });
    $("#save_return_mail").click(function () {
        $("#return_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#return_content_mail')).catch(
            error => { console.error( error ); });
    $("#save_loyal_mail").click(function () {
        $("#loyal_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#loyal_content_mail')).catch(
            error => { console.error( error ); });
    $("#save_lost_customers_mail").click(function () {
        $("#lost_customers_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#lost_customers_content_mail')).catch(
            error => { console.error( error ); });
    $("#save_birthday_mail").click(function () {
        $("#birthday_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#birthday_content_mail')).catch(
            error => { console.error( error ); });
    $("#save_anoun_mail").click(function () {
        $("#anoun_form_content_mail").submit();
    });
    ClassicEditor.create(
        document.querySelector('#anoun_content_mail')).catch(
            error => { console.error( error ); });

});
