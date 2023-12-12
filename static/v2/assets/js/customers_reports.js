$(document).ready(function () {
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

    var deferred = $.Deferred();

    function genDashboard(min_date, max_date) {
        $.ajax({
            url: '/get_top_customers',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#top_customers').empty();
                $('#top_customers').append(result);
            }
        });
        $.ajax({
            url: '/get_devices_report',
            type: 'GET',
            success: function (result) {
                $('#devices').empty();
                $('#devices').append(result);
            }
        });
        $.ajax({
            url: '/get_gender_report',
            type: 'GET',
            success: function (result) {
                $('#gender_reports').empty();
                $('#gender_reports').append(result);
            }
        });
        $.ajax({
            url: '/get_location_report',
            type: 'GET',
            success: function (result) {
                $('#locations_report').empty();
                $('#locations_report').append(result);

            }
        });


    }

    var start = moment().subtract(7, 'days').format('DD-MM-YYYY');
    var end = moment().format('DD-MM-YYYY');
    $("#minDate").val(start);
    $("#maxDate").val(end);
    genDashboard($("#minDate").val(), $("#maxDate").val());

    function numeroAdosCaracteres(fecha) {
        if (fecha > 9) {
            return "" + fecha;
        } else {
            return "0" + fecha;
        }
    }

    flatpickr("#reportrange", {
        enableTime: false,
        dateFormat: "d-m-Y",
        mode: "range",
        defaultDate: [start, end],
        onChange: function (selectedDates, dateStr, instance) {
            var from = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
            var to = numeroAdosCaracteres(selectedDates[1].getDate()) + "-" + numeroAdosCaracteres(selectedDates[1].getMonth() + 1) + "-" + selectedDates[1].getFullYear();
            $("#minDate").val(from);
            $("#maxDate").val(to);
        }
    });

    $("#view_data").click(function () {
        genDashboard($("#minDate").val(), $("#maxDate").val());
    });




});
