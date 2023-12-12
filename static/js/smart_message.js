$(document).ready(function () {
    var shop_id = $('#shop_in_mer').val();
    $('textarea').each(function () {
        $(this).val($(this).val().trim());
    }
    );
    $('input').each(function () {
        $(this).val($(this).val().trim());
    }
    );
    var shop_id_select = $('#shop_id_select').val();
    $('#shop_in_mer').select2();
    $('#shop_in_mer').val(shop_id_select).trigger('change');
    $('#shop_in_mer').on("change", function (e) {
        var shop_id = $('#shop_in_mer').val();
        var url = "/marketing_automation/" + shop_id;
        $(location).attr('href', url);
    });

    $('#thankyou_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/thank_you/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });
    $('#anoun_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/anoun/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });
    $('#birthday_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/happy_birthday/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });


    $('#lost_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/lost/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });


    $('#loyal_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/loyal/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });


    $('#return_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/return/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });


    $('#welcome_active').change(function () {
        var checked = $(this).is(":checked");
        $.get("/marketing_automation/" + shop_id + "/config/welcome/" + checked);
        swal(ngettext("Thanh_cong"), '', 'success');
    });
    sortable('#sort_channel');

    sortable('.sortable')[0].addEventListener('sortupdate', function (e) {
        var des = e.detail.origin.items;
        var new_sort = "";
        for (i = 0; i < des.length; i++) {
            new_sort = new_sort + des[i].innerText.trim();
            if (i < des.length - 1) {
                new_sort = new_sort + ',';
            }

        }
        $('#channel_list').val(new_sort);

    });

    $('#save_channel_list').click(function () {
        var data = {
           'channel_list':  $('#channel_list').val(),
           'all_channel':  $('#all_channel').is(':checked')
        }
        $.ajax({
            headers: { "X-CSRFToken": '{{ csrf_token() }}' },
            url: "/marketing_automation/" + shop_id_select + "/channels",
            type: 'POST',
            data: data,
            success: function () {
                swal(ngettext("Thanh_cong"), '', 'success');
            }
        });


    });


});