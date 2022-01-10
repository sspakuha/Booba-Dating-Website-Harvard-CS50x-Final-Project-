$(document).ready(function ()
{
  datahtml = "";
  gotgift = false;

  $('.msg').click(function()
  {
    $(this).next().submit();
  });

  $("#like").click(function ()
  {
    $('.modal-conf').show();
    $('body').addClass("_lock");
  });

  $(".modal-conf__darken, #cancel-modal").click(function ()
  {
    $('body').removeClass("_lock");
    $('.modal-conf').hide();
  });


	$('.profiledata__title-f .profiledata__text').click(function ()
  {
		$('.profiledata__title-f .profiledata__text').removeClass("active");
		$(this).addClass("active");
	});

	$('.rewards .profiledata__title-p').click(function ()
  {
    if (gotgift)
    {
      alert("You can only get one gift daily.");
      return;
    }

    inp = $(this).siblings();
    curr = $(this);

    let access = true;
    let giftamount = 0;

    $.ajax( { url : "/getgift", async : false, success: function (gift)
    {
      if (gift.amount != -1)
      {
        giftamount=gift.amount;
        inp.html(`${giftamount}<i class="fas fa-coins"></i>`);
        inp.css("color", "lightgreen");
      }
      else
      {
        access = false;
      }
    }});
    if (access == false)
    {
      return;
    }
		$(this).fadeOut(200, function ()
    {
			inp.fadeIn(300);
		});

    balance = $('#balance').text();
    $('#balance, #balance1').text(parseInt(balance)+parseInt(giftamount));
    gotgift = true;
  })

  $('#maindata').click(function ()
  {
    if ($(this).find(".fa-pencil-alt").is(":hidden"))
    {
      $(this).find(".fa-times").hide(100);
      $(this).find(".fa-pencil-alt").show(200);
      $('#maincontenthide').hide(200);
      $('#maincontentshow').show(200);
    }
    else
    {
      $('.maindata_txtar').val($('#maincontentshow').find('pre').text());
      $(this).find(".fa-pencil-alt").hide(100);
	  	$(this).find(".fa-times").show(200);

      $('#maincontentshow').hide(200);
      $('#maincontenthide').show(200);
    }
	});

  $('#leftdata').click(function ()
  {
    if ($(this).find(".fa-pencil-alt").is(":hidden"))
    {
      $(this).find(".fa-times").hide(100);
      $(this).find(".fa-pencil-alt").show(200);

      $("#contenthide").hide(200);
      $("#contentshow").show(200);

    }
    else
    {
      $(this).find(".fa-pencil-alt").hide(100);
		  $(this).find(".fa-times").show(200);

      $("#contentshow").hide(200);
      $("#contenthide").show(200);
  };
})

function checkgift()
{
  $.get("/checkgift", function (gift)
  {
    if (gift.amount == -1)
    {
      $('.rewards__darken').show(100);
      if (gift.hour == 0 && gift.minute == 0)
      {
        $('.rewards__timeout p').text(`Wait 24 hours and 0 minutes more.`);
      }
      else
      {
      $('.rewards__timeout p').text(`Wait ${gift.hour} hour(s) and ${gift.minute} minute  (s) more.`);
      }
    }
    else{
      $('.rewards__darken').hide(100);
    }
  });

  };
  checkgift();
  setInterval(checkgift, 5000);

  function checkonline()
  {
    username = window.location.pathname.substr(1);
    $.ajax( { type: 'POST', data: { username: username }, url : "/checkonline", success: function (time)
    {
      if (time == 0)
      {
        return;
      }
      else if (time == 1)
      {
        $('.online-indicator').css("display", "inline");
        $('#lastseen').text("Currently online");
      }
      else
      {
        $('.online-indicator').css("display", "none");
        $('#lastseen').text(`Last seen: ${pad(time.day)}/${pad(time.month)} ${pad(time.hour)}:${pad(time.minute)}`);
      }
    }});

  }
  checkonline();
  setInterval(checkonline, 5000);

  function checklen()
  {
	  searchfield = $('#age')
	  if (parseInt(searchfield.val()) > 123 )
    {
		  searchfield.val(123);
		  return false;
	  }
    else if(parseInt(searchfield.val()) < 18 )
    {
      searchfield.val(18);
		  return false;
    }
  }

	sf = $('#age')

	sf.on("change", function () {
		checklen();
	})
	sf.on("mouseleave", function () {
		checklen();
	})

  $('#favorite').click(function ()
  {
    username=window.location.pathname.slice(1)
    $.ajax( { type: 'POST', data: { username: username }, url : "/favorite", async : false, success: function (data)
    {
      res = data.text;
    }});
    if (res != -1)
    {
        $(this).html(res);
    }
  })

  $('#confirm-like').click(function ()
  {
    $('#cancel-modal').click();
    let res;
    username=window.location.pathname.slice(1);
    $.ajax( { type: 'POST', data: { username: username }, url : "/like", async : false, success: function (data)
    {
      res = data.text;
    }});
    if (res != -1)
    {
      $("#like").html(res);
      if (res == '<i class="far fa-heart"></i> Unlike')
      {
        balance = $('#balance').text()
        $('#balance, #balance1').text(parseInt(balance)-parseInt(75))

        $('.modal-conf__text').html('<p>You already liked this person. Unliking will not return any coins. </p> <p>Are you sure?</p>')
      }
      else
      {
        balance = $('#balance').text();
        $('.modal-conf__text').html(`									<p>Like costs 75 coins. Do you want to proceed?</p><p>Your balance is: ${balance} <i class="fas fa-money-bill-alt"></i></p>`)
      }
    }
    else
    {
      $('._container').prepend(`<div class="flash" style="text-align: center; color: white; margin-bottom: 30px; padding: 15px 0px; font-family: Arial; font-size: 20px; background-color: rgba(115, 95, 95, 0.5); border-radius: 5px; display: none;">
					You don't have enough money.
				  </div>`)
        $('.flash').show(200);
    }
  });


  $('.profiledata__title-f').on("click", '#tabtrigger', function ()
  {
    target = parseInt($(this).data('target'));
    if (target == 1)
    {
      if ($('#favorites').is(":hidden"))
      {
        $('.tab').each(function()
        {
          $(this).hide(100);
        })
        $('#favorites').show(100);
      }
    }
    else if (target == 2)
    {
      if ($('#visitors').is(":hidden"))
      {
        $('.tab').each(function()
        {
          $(this).hide(100);
        })
        $('#visitors').show(100);
      }
    }
    else if (target == 3)
    {
      if ($('#likes').is(":hidden"))
      {
        $('.tab').each(function()
        {
          $(this).hide(100);
        });
        $('#likes').show(100);
      }
    }
  });


  $('.tab').on('click', '#unfavorite', function()
  {
    item = $(this).parents('.tab__itemflex');
    username = $(this).parent().prev().text().trim();

    $.ajax( { type: 'POST', data: { username: username }, url : "/favorite"})

    item.fadeOut(200, function()
    {
      item.remove();
      any = $('#favorites').find(".tab__itemflex");
      if (!any[0])
      {
      $('#favorites').html(`<p style="padding: 10px;">You don't have any profiles in your favorites.</p>`);
      }
    });
  });
});


function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}
