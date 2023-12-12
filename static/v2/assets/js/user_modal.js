$(document).ready(function () {

    if ($("#ex_birthday").length > 0) {
        var from_date_arr = $("#ex_birthday").val();
        flatpickr("#birthday", {
            enableTime: false,
            defaultDate: from_date_arr,
            dateFormat: "d-m"
        });
    } else {
        flatpickr("#birthday", {
            enableTime: false,
            dateFormat: "d-m"
        });
    }
    if ($("#curr_gender").length > 0) {
        $("#gender").val($("#curr_gender").val());
    }

    $('#tags_input').select2({
        dropdownParent: $("#modal-content-user")
    });
    $('#tags_input').on("change", function (e) {
        if ($('#tags_input').val()) {
            $('#select_tags').val($('#tags_input').val().toString());
        } else {
            $('#select_tags').val("");
        }
    });

    var source_tags = $("#source_tags").val();
    if(source_tags && source_tags.length>0 && source_tags.toString() !='None') {
        var data_soure_tags = JSON.parse(source_tags.replace(/\'/g, '"'));

        $("#tags_input").val(data_soure_tags);
        $('#tags_input').trigger('change');
    }
});
