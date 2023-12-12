$(document).ready(function () {
    $("#dashboards").click();
    var start = moment().subtract(7, 'days').format('DD-MM-YYYY');
    var end = moment().format('DD-MM-YYYY');
    $("#minDate").val(start);
    $("#maxDate").val(end);
    $("#bday_from_date").val(start);
    $("#bday_to_date").val(end);

    if ($("#loyal_from").length == 0 || $("#loyal_from").val() == '') {
        $("#loyal_from").val('3');
    }

    if ($("#loyal_to").length == 0 || $("#loyal_to").val() == '') {
        $("#loyal_to").val('5');
    }
    if ($("#lost_count").length == 0 || $("#lost_count").val() == '') {
        $("#lost_count").val('31');
    }

    function numeroAdosCaracteres(fecha) {
        if (fecha > 9) {
            return "" + fecha;
        } else {
            return "0" + fecha;
        }
    }

    flatpickr("#from_date", {
        enableTime: false,
        dateFormat: "d-m-Y",
        defaultDate: start,
        onChange: function (selectedDates, dateStr, instance) {
            var from = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
            $("#minDate").val(from);
        }
    });

    flatpickr("#to_date", {
        enableTime: false,
        dateFormat: "d-m-Y",
        defaultDate: end,
        onChange: function (selectedDates, dateStr, instance) {
            var to = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
            $("#maxDate").val(to);
        }
    });
    // flatpickr("#reportrange", {
    //     enableTime: false,
    //     dateFormat: "d-m-Y",
    //     mode: "range",
    //     defaultDate: [start, end],
    //     onChange: function (selectedDates, dateStr, instance) {
    //         var from = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
    //         var to = numeroAdosCaracteres(selectedDates[1].getDate()) + "-" + numeroAdosCaracteres(selectedDates[1].getMonth() + 1) + "-" + selectedDates[1].getFullYear();
    //         $("#minDate").val(from);
    //         $("#maxDate").val(to);
    //          genDashboard($("#minDate").val(), $("#maxDate").val(), $("#current_shops").val());
    //     }
    // });


    flatpickr("#birthdayrange", {
        enableTime: false,
        dateFormat: "d-m-Y",
        mode: "range",
        defaultDate: [start, end],
        onChange: function (selectedDates, dateStr, instance) {
            var from = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
            var to = numeroAdosCaracteres(selectedDates[1].getDate()) + "-" + numeroAdosCaracteres(selectedDates[1].getMonth() + 1) + "-" + selectedDates[1].getFullYear();
            $("#bday_from_date").val(from);
            $("#bday_to_date").val(to);
            $("#view_birthday_data").click();
        }
    });

    var ajaxReqs = 0;
    var ajaxQueue = [];
    var ajaxActive = 0;
    var ajaxMaxConc = 3;

    function addAjax(obj) {
        ajaxReqs++;
        var oldSuccess = obj.success;
        var oldError = obj.error;
        var callback = function () {
            ajaxReqs--;
            if (ajaxActive === ajaxMaxConc) {
                $.ajax(ajaxQueue.shift());
            } else {
                ajaxActive--;
            }
        };
        obj.success = function (resp, xhr, status) {
            callback();
            if (oldSuccess) oldSuccess(resp, xhr, status);
        };
        obj.error = function (xhr, status, error) {
            callback();
            if (oldError) oldError(xhr, status, error);
        };
        if (ajaxActive === ajaxMaxConc) {
            ajaxQueue.push(obj);
        } else {
            ajaxActive++;
            $.ajax(obj);
        }
    }

    $("#view_birthday_data").click(function () {
        var bday_from_date = $("#bday_from_date").val();
        var bday_to_date = $("#bday_to_date").val();
        $.ajax({
            url: '/get_birthday_report',
            data: {
                'min_date': bday_from_date,
                'max_date': bday_to_date
            },
            type: 'GET',
            success: function (result) {
                $('#total_birthday').empty();
                $('#total_birthday').append(result);
            }
        });
    });
    $("#view_data").click(function () {
        genDashboard($("#minDate").val(), $("#maxDate").val(), $("#current_shops").val());
    });


    $("#view_lost_count").click(function () {
        $.ajax({
            url: '/get_lost_customer_report',
            data: {
                'lost_count': $("#lost_count").val()
            },
            type: 'GET',
            success: function (result) {
                $('#total_lost').empty();
                $('#total_lost').append(result);

            }
        });
    });

    $("#view_loyal_data").click(function () {
        $.ajax({
            url: '/get_loyal_customer_report',
            data: {
                'loyal_from': $("#loyal_from").val(),
                'loyal_to': $("#loyal_to").val()
            },
            type: 'GET',
            success: function (result) {
                $('#total_loyal').empty();
                $('#total_loyal').append(result);

            }
        });
    });

    function genDashboard(min_date, max_date, shop) {
        // if (shop == 'all') {
            $.ajax({
                url: '/get_campaign_report',
                data: {
                    'min_date': min_date,
                    'max_date': max_date,
                },
                type: 'GET',
                success: function (result) {
                    $('#campaign').empty();
                    $('#campaign').append(result);
                }
            });
        // } else {
        //     $.ajax({
        //         url: '/get_shop_campaign_report',
        //         data: {
        //             'min_date': min_date,
        //             'max_date': max_date,
        //             'shop_select': shop
        //         },
        //         type: 'GET',
        //         success: function (result) {
        //             $('#shop_campaign').empty();
        //             $('#shop_campaign').append(result);
        //         }
        //     });
        // }


        $.ajax({
            url: '/get_sms_coupons_report',
            data: {
                'min_date': min_date,
                'max_date': max_date,
                'shop_select': shop
            },
            type: 'GET',
            success: function (result) {
                $('#sms_coupons_report').empty();
                $('#sms_coupons_report').append(result);
            }
        });
        var bday_from_date = $("#bday_from_date").val();
        var bday_to_date = $("#bday_to_date").val();
        // if ($("#bday_from_date").length == 0 ){
        //
        // }
        $.ajax({
            url: '/get_birthday_report',
            data: {
                'min_date': bday_from_date,
                'max_date': bday_to_date
            },
            type: 'GET',
            success: function (result) {
                $('#total_birthday').empty();
                $('#total_birthday').append(result);
            }
        });
        $.ajax({
            url: '/get_lost_customer_report',
            data: {
                'lost_count': $("#lost_count").val()
            },
            type: 'GET',
            success: function (result) {
                $('#total_lost').empty();
                $('#total_lost').append(result);

            }
        });
        $.ajax({
            url: '/get_loyal_customer_report',
            data: {
                'loyal_from': $("#loyal_from").val(),
                'loyal_to': $("#loyal_to").val()
            },
            type: 'GET',
            success: function (result) {
                $('#total_loyal').empty();
                $('#total_loyal').append(result);

            }
        });

    }

    genDashboard($("#minDate").val(), $("#maxDate").val(), $("#current_shops").val());

    // var data_soure_shops = $("#current_shops").val();
    // $('#locations_selects').select2().val(data_soure_shops)
    //     .trigger("change");
    // $('#locations_selects').on("change", function (e) {
    //     var url = '/marketing_reports?shop=' + $('#locations_selects').val();
    //     window.location.replace(url);
    // });

});
