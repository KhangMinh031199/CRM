$(document).ready(function() {
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

    $("#export_data_fb").click(function() {
        var url_export = "/export_customers";
        $.ajax({
            url: url_export,
            data: $("#form_cus").serialize(),
            success: function(data) {
                alert('File đang được xử lý, vui lòng kiểm tra email để nhận file sau 3-5 phút nữa.');
            }
        });
    });

       $(".user-detail").click(function() {
                $('#customers').click();

        var phone = $(this).attr('phone');
        $("#content_modal").empty();
        var url_user = '/user/modal/' + phone;

        	$('#content_modal').load(url_user,function(result){
	                $('#user_detail').modal({show:true});
	        });


    });

    $("#view_data").click(function() {
        $("#form_cus").attr('action', '/customers');
        $("#form_cus").submit();
    });



        $('#select_tags_input').select2({
          dropdownParent: $("#customers_fb_filter"),
            width: '100%'
        });
        $('#select_tags_input').on("change", function (e) {
            if($('#select_tags_input').val()){
              $('#select_tags_filter').val($('#select_tags_input').val().toString());
            }else{
              $('#select_tags_filter').val("");
            }
      });

        $('#locations_selects').on("change", function(e) {
            if($('#locations_selects').val()){
              $('#locations').val($('#locations_selects').val().toString());
            }else{
              $('#locations').val("");
            }
      });


        var source_tags = $("#source_tags_filter").val();
        if(source_tags && source_tags.length>0 && source_tags.toString() !='None'){
            var data_soure_tags = JSON.parse(source_tags.replace(/\'/g, '"'));
            $("#select_tags_input").val(data_soure_tags);
            $('#select_tags_input').trigger('change');
        }
          $('#customers').click();
});
