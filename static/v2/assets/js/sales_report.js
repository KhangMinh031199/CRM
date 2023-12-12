$(document).ready(function () {
    $("#dashboards").click();
    var start = moment().subtract(7, 'days').format('DD-MM-YYYY');
    var end = moment().format('DD-MM-YYYY');
    $("#minDate").val(start);
    $("#maxDate").val(end);

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
            onChange: function(selectedDates, dateStr, instance){
                var from = numeroAdosCaracteres(selectedDates[0].getDate()) + "-" + numeroAdosCaracteres(selectedDates[0].getMonth() + 1) + "-" + selectedDates[0].getFullYear();
                $("#minDate").val(from);
            }
        });

    flatpickr("#to_date", {
        enableTime: false,
        dateFormat: "d-m-Y",
        defaultDate: end,
        onChange: function(selectedDates, dateStr, instance){
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
    //          genDashboard($("#minDate").val(), $("#maxDate").val());
    //     }
    // });

    function genDashboard(min_date, max_date) {
        $.ajax({
            url: '/get_booking_table_report',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#booking_table').empty();
                $('#booking_table').append(result);
            }
        });

          $.ajax({
            url: '/get_booking_table_source_report',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#source_booking_table').empty();
                $('#source_booking_table').append(result);
            }
        });

            $.ajax({
            url: '/get_booking_table_location_report',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#location_booking_table').empty();
                $('#location_booking_table').append(result);
            }
        });

        $.ajax({
            url: '/get_status_booking_table_report',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#status_booking_table').empty();
                $('#status_booking_table').append(result);
            }
        });
        $.ajax({
            url: '/get_loyal_wallet_report',
            data: {
                'min_date': min_date,
                'max_date': max_date
            },
            type: 'GET',
            success: function (result) {
                $('#loyal_wallet').empty();
                $('#loyal_wallet').append(result);
            }
        });
    }

    genDashboard($("#minDate").val(), $("#maxDate").val());
});
