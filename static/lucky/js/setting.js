var addedSegments = 1;

function formValidation() {
    var e = !0;
    $(".frmError").hide();
    var t = $("#txtWheelStrokeWidth").val().trim(), n = $("#txtwheelTextSize").val().trim(),
        a = $("#txtgameOverText").val().trim(), d = $("#txtintroText").val().trim(),
        o = $("#txtOuterRadius").val().trim(), i = $("#txtInnerRadius").val().trim();
    if ("" != t && null != t || (e = !1, $("#spn_WheelStrokeWidth").show()), "" != n && null != n || (e = !1, $("#spn_wheelTextSize").show()), "" != a && null != a || (e = !1, $("#spn_gameOverText").show()), "" != d && null != d || (e = !1, $("#spn_introText").show()), "" != o && null != o || (e = !1, $("#spn_OuterRadius").show()), "" != i && null != i || (e = !1, $("#spn_InnerRadius").show()), $("#tblsegments tr").each(function () {
        var t = $(this).attr("data-count"), n = $("#txtDisplayText" + t).val().trim(),
            a = $("#txtResultText" + t).val().trim();
        "" != n && null != n || (e = !1, $("#spn_DisplayText" + t).show()), "" != a && null != a || (e = !1, $("#spn_ResultText" + t).show())
    }), 1 == e) {
        var l = "";
        return $("#tblsegments tr").each(function () {
            l += $(this).attr("data-count") + ","
        }), $("#hdnSegmentCount").val(l.substring(0, l.length - 1)), !0
    }
    return $("html, body").animate({scrollTop: 0}, "slow"), !1
}

function AddOption() {
    addedSegments++, $("#tblsegments").append('<tr id="dvdelete_' + addedSegments + '"  class="clscombinations" data-count="' + addedSegments + '"><td width="20%"><input type="text" id="txtDisplayText' + addedSegments + '" name="txtDisplayText' + addedSegments + '" class="token_input input_box" placeholder="Enter Segment Name" /><span id="spn_DisplayText" name="spn_DisplayText' + addedSegments + '" class="frmError"> This field is required. </span></td><td width="10%"><input type="text" id="txtBackgroundColor' + addedSegments + '" name="txtBackgroundColor' + addedSegments + '" class="token_input input_box jscolor" placeholder="Select Background Color" /></td><td width="20%"><input type="text" id="txtResultText' + addedSegments + '" name="txtResultText' + addedSegments + '" class="token_input input_box" placeholder="Enter Result Text" /><span id="spn_ResultText' + addedSegments + '" name="spn_ResultText' + addedSegments + '" class="frmError"> This field is required. </span></td><td width="40%"><div  style="text-align: left;"><span style="text-align: left;"> Have a coupon code ? </span></div><div  style="text-align: left;"><input type="radio" name="chkCouponCode' + addedSegments + '" checked="checked" value="Yes" data-id="' + addedSegments + '" class="clsCouponCode"> Yes<input type="radio" name="chkCouponCode' + addedSegments + '" value="No" data-id="' + addedSegments + '" class="clsCouponCode" style="margin-left: 5px;"> No </div><input type="text" id="txtCouponCodeText' + addedSegments + '" name="txtCouponCodeText' + addedSegments + '" class="token_input input_box" placeholder="Enter Coupon Code" value="" /></td><td width="20%"><div class="copon_pr"><select id="ddl_gravity' + addedSegments + '" name="ddl_gravity' + addedSegments + '" class="gravityclass" data-val="true" data-val-number="The field Gravity must be a number." data-val-required="The Gravity field is required." onchange="CalculateGravity(' + addedSegments + ", " + addedSegments + ')"><option value="0">0</option><option value="10">10</option><option value="20">20</option><option value="30">30</option><option value="40">40</option><option value="50">50</option><option value="60">60</option><option value="70">70</option><option value="80">80</option><option value="90">90</option><option value="100">100</option></select><span class="gravityperclass">0%</span><input type="hidden" id="hdnGravityPerc' + addedSegments + '" name="hdnGravityPerc' + addedSegments + '" class="hdnGravity" value="0" /></div></td><td width="5%"><input type="button" value="Delete" id="btndelete_' + addedSegments + '" name="btndelete_' + addedSegments + '" onclick="return DeleteDiv(' + addedSegments + ')" class="clsDeleteDiv del_btn"/></td></tr>'), jscolor.installByClassName("jscolor")
}

function DeleteDiv(e) {
    e = $.trim(e), $("#dvdelete_" + e).remove()
}

function UploadImage(e, t) {
    var n = e.files[0];
    n.size <= 5e5 ? n && ((new Image).src = (window.URL || window.webkitURL).createObjectURL(n), $("#" + t).attr("src", (window.URL || window.webkitURL).createObjectURL(n))) : alert("Image size should be less than 500 kb !")
}


$("#btnRemoveBackgroudImage").click(function () {
    $("#imgBackgroungImage").attr("src", ""), $("#hdnBackgroungImage").val(""), $("#backgroung-image-file").val("")
}), $("#btnRemoveWheelCenterImage").click(function () {
    $("#imgWheelCenterImage").attr("src", "images/no_img.png"), $("#hdnWheelCenterImage").val("")
}), $("#btnRemoveWheelPinImage").click(function () {
    $("#imgWheelPinImage").attr("src", ""), $("#hdnWheelPinImage").val(""), $("#wheelpinimagefile").val("")
}), $(document).on("change", "#ddlBackgroundOption", function () {
    "text" == $("#ddlBackgroundOption option:selected").val() ? ($("#dvBackgroundColor").show(), $("#dvBackgroundImage").hide()) : ($("#dvBackgroundColor").hide(), $("#dvBackgroundImage").show())
}), $(document).on("change", ".clsCouponCode", function () {
    var e = $(this).attr("data-id");
    "Yes" == $(this).val() ? $("#txtCouponCodeText" + e).show() : $("#txtCouponCodeText" + e).hide()
}), $("#enablediscountbar").change(function () {
    this.checked ? ($(".disable-me").css("display", "none"), $("#countdowntime").prop("disabled", !1), $("#position").prop("disabled", !1)) : ($(".disable-me").css("display", "block"), $("#countdowntime").prop("disabled", !0), $("#position").prop("disabled", !0))
}), $("#showdesktop").change(function () {
    $("#dvdesktop").toggleClass("disabled")
}), $("#showmobile").change(function () {
    $("#dvmobile").toggleClass("disabled")
}), $("#desktopinterval").change(function () {
    this.checked ? $("#DesktopIntervaltext").prop("disabled", !1) : $("#DesktopIntervaltext").prop("disabled", !0)
}), $("#mobileinterval").change(function () {
    this.checked ? $("#MobileIntervaltext").prop("disabled", !1) : $("#MobileIntervaltext").prop("disabled", !0)
}), $(document).on("click", ".resetcookie", function (e) {
    1 == confirm("Are you sure want to reset cookies for all users ?") && alert("Cookies are reset.")
});