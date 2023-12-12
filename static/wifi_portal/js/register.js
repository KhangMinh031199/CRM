$(document).ready(function () {

      if ($('#gender_register').length > 0) {
            $('#gender_register input[type="checkbox"]').on('change', function() {
                $('#gender_register input[type="checkbox"]').not(this).prop('checked', false);
            });

        }
        $("#submit_register").click(function() {
            if ($('#birthday_require').length > 0 && $('#birthday').length > 0) {

                if ($("#day_birth").val().length == 0 || $("#month_birth").val().length == 0) {
                    alert('Đừng quên nhập ngày sinh nhật để nhận quà.');
                } else {
                    $("#register_form").submit();
                }

            } else {
                $("#register_form").submit();
            }

        });


});
