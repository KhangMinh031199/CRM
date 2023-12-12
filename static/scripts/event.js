$(document).ready(function() {
    $("#share_link_box").hide();
    $('#content').summernote({
        height: 100,
        minHeight: null,
        maxHeight: null,
    });
    $("#preview_event").on("load", function() {
        var event = $("#event").val();
        if (event === '{}') {
            $("#title").val($("#preview_event").contents().find("#title_product").text());
            $("#content").summernote("code", $("#preview_event").contents().find("#content_product").text());
            $("#preview_event").contents().find("#share_fb").hide();
            $("#preview_event").contents().find("#like_fb").show();
            $("#preview_event").contents().find("#check_in_fb").hide();
            $("#preview_event").contents().find("#connect_fb").hide();
        } else {
            var json_event = {};
            $("#event_value :input").each(function(e) {
                json_event[this.id] = this.value;
            });
            if (json_event["type"] == 'share') {
                $("#share_link_box").show();
                $("#preview_event").contents().find("#share_fb").show();
                $("#preview_event").contents().find("#like_fb").hide();
                $("#preview_event").contents().find("#check_in_fb").hide();
                $("#preview_event").contents().find("#connect_fb").hide();
            } else {
                $("#share_link_box").hide();
                if ($("#social").val() == 'like') {
                    $("#preview_event").contents().find("#share_fb").hide();
                    $("#preview_event").contents().find("#like_fb").show();
                    $("#preview_event").contents().find("#check_in_fb").hide();
                    $("#preview_event").contents().find("#connect_fb").hide();
                } else if ($("#social").val() == 'connect') {
                    $("#preview_event").contents().find("#share_fb").hide();
                    $("#preview_event").contents().find("#like_fb").hide();
                    $("#preview_event").contents().find("#check_in_fb").hide();
                    $("#preview_event").contents().find("#connect_fb").show();
                } else {
                    $("#preview_event").contents().find("#share_fb").hide();
                    $("#preview_event").contents().find("#like_fb").hide();
                    $("#preview_event").contents().find("#check_in_fb").show();
                    $("#preview_event").contents().find("#connect_fb").hide();
                }

            }

        }
    });

    $("#title").keyup(function() {
        $("#preview_event").contents().find("#title_product").text($("#title").val());
    });
    $('#content').on('summernote.keyup', function(we, e) {
        $("#preview_event").contents().find("#content_product").html($("#content").summernote("code"));
    });

    function readURL(input) {

        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function(e) {
                $("#preview_event").contents().find("#background-image").css('background', 'url(' + e.target.result + ') no-repeat bottom center');
            };

            reader.readAsDataURL(input.files[0]);
        }
    }

    $("#photo").change(function() {
        readURL(this);
    });

    $("#social").change(function() {
        $("#preview_event").contents().find("#social").empty();
        if ($("#social").val() == 'share') {
            $("#share_link_box").show();
            $("#preview_event").contents().find("#share_fb").show();
            $("#preview_event").contents().find("#like_fb").hide();
            $("#preview_event").contents().find("#check_in_fb").hide();
            $("#preview_event").contents().find("#connect_fb").hide();
        } else {
            $("#share_link_box").hide();
            if ($("#social").val() == 'like') {
                $("#preview_event").contents().find("#share_fb").hide();
                $("#preview_event").contents().find("#like_fb").show();
                $("#preview_event").contents().find("#check_in_fb").hide();
                $("#preview_event").contents().find("#connect_fb").hide();
            } else if ($("#social").val() == 'connect') {
                $("#preview_event").contents().find("#share_fb").hide();
                $("#preview_event").contents().find("#like_fb").hide();
                $("#preview_event").contents().find("#check_in_fb").hide();
                $("#preview_event").contents().find("#connect_fb").show();
            } else {
                $("#preview_event").contents().find("#share_fb").hide();
                $("#preview_event").contents().find("#like_fb").hide();
                $("#preview_event").contents().find("#check_in_fb").show();
                $("#preview_event").contents().find("#connect_fb").hide();
            }

        }
    });

    if ($("#event_social").length > 0) {
        $("#social").val($("#event_social").val());
    }


});
