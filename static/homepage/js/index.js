$(document).foundation();

$(window).scroll(function() {
  var scroll = $(window).scrollTop();
  if (scroll > 0) {
    $("#sticky-header").addClass("active");
  }
  else {
    $("#sticky-header").removeClass("active");
  }
});

function openNav() {
  document.getElementById("navTray").style.height = "100%";
}

function closeNav() {
  document.getElementById("navTray").style.height = "0%";
}


function isEmail(email) {
  var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  return regex.test(email);
}


function toTitleCase(str)
{
  return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

$('.slider').on('moved.zf.slider', function(){
  var people = $(this).children('.slider-handle').attr('aria-valuenow');
  if (people > 0) {
    $('.totalPeople').html(people);
    var cost = calculate(people, plan);
    if (cost === 0) {
      $('.enterpriseNo').hide();
      $('.enterpriseYes').show();
      $('.monthlyCost').hide();
      $('.totalPrice').html('Contact us for enterprise costs.');
      return;
    }
    $('.enterpriseNo').show();
    $('.enterpriseYes').hide();
    $('.monthlyCost').show();
    $('.totalPrice').html(plan.symbol + cost + '.00');
  }
});

$('.engage').on('click', function() {
  var id = $(this).attr("data-plan");
  plan = plans[id];
  $('.planName').html(toTitleCase(id));
  $('.totalPrice').html(plan.symbol + plan.plan_price + '.00');
  $('#engageModal').foundation('open');
});
