"use strict";
var Navbar = function() {
    var e = $(".navbar-nav, .navbar-nav .nav")
      , t = $(".navbar-nav .collapse");
    t.on({
        "show.bs.collapse": function() {
            var a;
            (a = $(this)).closest(e).find(t).not(a).collapse("hide")
        }
    })
};
