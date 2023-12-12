
$(document).ready(function () {
    var redirect_page = $('#redirect_page').val();
    var is_mobile_phone = $('#is_mobile_phone').val();
    var strWindowFeatures = "menubar=yes,location=yes,resizable=yes,scrollbars=yes,status=yes";
    if (redirect_page && redirect_page.length > 0) {

        window.open("fb://page/" + $("#facebook_page_id").val(), '_system', 'location=no');
    }
    $('.carousel').bcSwipe({ });

});
