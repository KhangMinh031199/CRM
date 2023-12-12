function customers_report(shop_id_select, range_time) {
    $("#customers_loading").show();
    $("#customers_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/customers',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#customers_loading").hide();
            $("#customers_content").show();
            $("#customers_content").empty();
            $("#customers_content").html(data);
        }
    });

}

function visits_report(shop_id_select, range_time) {
    $("#visits_loading").show();
    $("#visits_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/visits',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#visits_loading").hide();
            $("#visits_content").show();
            $("#visits_content").empty();
            $("#visits_content").html(data);
        }
    });

}

function new_customers_report(shop_id_select, range_time) {
    $("#new_customers_loading").show();
    $("#new_customers_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/new_customers',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#new_customers_loading").hide();
            $("#new_customers_content").show();
            $("#new_customers_content").empty();
            $("#new_customers_content").html(data);
        }
    });

}

function return_customers_report(shop_id_select, range_time) {
    $("#return_customers_loading").show();
    $("#return_customers_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/return_customers',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#return_customers_loading").hide();
            $("#return_customers_content").show();
            $("#return_customers_content").empty();
            $("#return_customers_content").html(data);
        }
    });

}


function smart_message_report(shop_id_select, range_time) {
    $("#smart_message_loading").show();
    $("#smart_message_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/smart_message',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#smart_message_loading").hide();
            $("#smart_message_content").show();
            $("#smart_message_content").empty();
            $("#smart_message_content").html(data);
        }
    });

}

function walkthrough_report(shop_id_select, range_time) {
    $("#walkthrough_loading").show();
    $("#walkthrough_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/walkthrough',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#walkthrough_loading").hide();
            $("#walkthrough_content").show();
            $("#walkthrough_content").empty();
            $("#walkthrough_content").html(data);
        }
    });

}


function location_report(shop_id_select, range_time) {
    $("#location_loading").show();
    $("#location_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/locations',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#location_loading").hide();
            $("#location_content").show();
            $("#location_content").empty();
            $("#location_content").html(data);
        }
    });

}

function device_report(shop_id_select, range_time) {
    $("#device_loading").show();
    $("#device_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/devices',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#device_loading").hide();
            $("#device_content").show();
            $("#device_content").empty();
            $("#device_content").html(data);
        }
    });
}

function visit_report(shop_id_select, range_time) {
    $("#visit_loading").show();
    $("#visit_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/user_visits',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#visit_loading").hide();
            $("#visit_content").show();
            $("#visit_content").empty();
            $("#visit_content").html(data);
        }
    });

}

function hours_report(shop_id_select, range_time) {
    $("#hours_loading").show();
    $("#hours_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/user_hours',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#hours_loading").hide();
            $("#hours_content").show();
            $("#hours_content").empty();
            $("#hours_content").html(data);
        }
    });

}



function days_report(shop_id_select, range_time) {
    $("#days_loading").show();
    $("#days_content").hide();
    $.ajax({
        type: 'GET',
        url: '/merchant_reports/user_days',
        data: { 'shop_id_select': shop_id_select, 'range_time': range_time },
        success: function (data) {
            $("#days_loading").hide();
            $("#days_content").show();
            $("#days_content").empty();
            $("#days_content").html(data);
        }
    });

}

function gen_reports(shop_id_select, range_time){

    customers_report(shop_id_select, range_time);
    visits_report(shop_id_select, range_time);
    new_customers_report(shop_id_select, range_time);
    return_customers_report(shop_id_select, range_time);
    smart_message_report(shop_id_select, range_time);
    walkthrough_report(shop_id_select, range_time);
    location_report(shop_id_select, range_time);
    device_report(shop_id_select, range_time);
    visit_report(shop_id_select, range_time);
    hours_report(shop_id_select, range_time);
    days_report(shop_id_select, range_time);
}

$(document).ready(function () {
    var shop_id_select = $("#shop_in_mer").val();
    var range_time = $("#range_time").val();

    gen_reports(shop_id_select, range_time);
    
    $('#range_time').on('change', function() {
        var shop_id_select = $("#shop_in_mer").val();
        var range_time = $("#range_time").val();
        gen_reports(shop_id_select, range_time);
    })
    $('#shop_in_mer').on('change', function() {
        var shop_id_select = $("#shop_in_mer").val();
        var range_time = $("#range_time").val();
        gen_reports(shop_id_select, range_time);
    })
})