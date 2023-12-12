/**
 * Created by macbook on 11/28/16.
 */

$(document).ready(function () {
    $('#sms_connect').on('click', function () {
        $(location).attr('href', '/register');
    });

    $('#facebook_connect').on('click', function () {
        FB.login(function (response) {
            if (response.authResponse) {
                FB.api('/me?fields=email,birthday,age_range,name,hometown,relationship_status,gender', function (response) {
                    var email = response.email;
                    var birthday = response.birthday;
                    var age_range = response.age_range;
                    var age_user = {};
                    var name = response.name;
                    var hometown = response.hometown.name;
                    var relationship_status = response.relationship_status;
                    age_user["min"] = age_range.min;
                    age_user["max"] = age_range.max;
                    var fb_id = response.id;
                    var gender = response.gender;
                    $("#email").val(email);
                    $("#birthday").val(birthday);
                    $("#age_range").val(JSON.stringify(age_user));
                    $("#name").val(name);
                    $("#home_town").val(hometown);
                    $("#relationship_status").val(relationship_status);
                    $("#gender").val(gender);
                    $("#fb_id").val(fb_id);
                    $("#facebook_form").submit();
                });
            } else {
                console.log('User cancelled login or did not fully authorize.');
            }
        }, {scope: 'email,user_birthday,user_hometown,user_relationships', return_scopes: true});

    });

});

