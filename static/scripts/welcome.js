 $(document).ready(function() {
     $("#myCarousel").on("slide.bs.carousel", function(ev) {
         var lazy;
         lazy = $(ev.relatedTarget).find("img[data-src]");
         lazy.attr("src", lazy.data('src'));
         lazy.removeAttr("data-src");
     });

     $("#myCarousel").swiperight(function() {
         $(this).carousel('prev');
     });
     $("#myCarousel").swipeleft(function() {
         $(this).carousel('next');
     });
     var redirect_page = $('#redirect_page').val();
     if (redirect_page && redirect_page.length > 0) {
         window.open(redirect_page, '_blank');
     }


 });