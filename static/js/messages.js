$(document).ready(function (){
  let ajaxing = false;
  let gettingolder = false;
  let closed = true;
  let executing = false;

  // If method == "POST" don't save passed data
  window.history.pushState('messages', 'Conversations', '/messages');

  document.querySelector(".messages__right-messages").scrollTo(0, document.querySelector(".messages__right-messages").scrollHeight);

  $('#content').keydown(function (event)
  {
    if (event.key == "Enter")
    {
      $('#send').click()
    }
  })

  $('#search').keyup(function (event)
  {
    let query = $(this).val().replace(/[^a-zA-Z]/g,'');
    query = query.toLowerCase();
    $('.user__card').each(function ()
    {
      username = $(this).find('.user__name').text().trim();
      if (username.toLowerCase().includes(query))
      {
        $(this).show();
      }
      else{
        $(this).hide();
      }
    });
  });

  $('.user').on("click", '.user__card', function ()
  {
    closed = false;
    touch = $(this)
    let isnew = false;

    username = touch.find(".user__name").text().trim();
    avatar = touch.find('.user__image').html();

    src = touch.find('.user__image img').attr('src');

    $('.username').html(`<a href="${username}" style="color: inherit;">${username}</a>`);

    if ($('.userpicture img').length > 0)
    {
      if ($('.userpicture img').attr('src').trim() != src.trim())
      {
        $('.userpicture').html(avatar)
      }
    }
    else
    {
      $('.userpicture').html(avatar)
    }

    if (!touch.hasClass('active'))
    {
      gettingolder = false;
      ajaxing = false;
      isnew = true;
      $('.messages__container').empty();
      $('.messages__right').removeClass('active');
      $('#lastseen').text('').hide();
      $('#content').focus();
      $('#content').select();
    }

    if (ajaxing)
    {
      return false;
    }
    ajaxing = true;

    $('.user__card').removeClass("active");
    touch.addClass("active");
    touch.removeClass("new");

    $.ajax( { type: 'POST', data: { username: username }, url : "/getmessages", success: function (res)
    {
    if (closed)
    {
      return;
    }
    $('.close').show();
    $('.messages__right-send').show();

    if (res[0] == -1)
    {
      ajaxing = false;
      return false;
    }
    if (res[0] == 0)
    {
      $('.messages__container').html(`<p style="font-size: 16px; color: white; margin-top: 20px; font-family: Roboto;">You don't have any message history with ${username}. Why don't you start now?</p>`);
      $('.messages__left').addClass("active");
	    $('.messages__right').addClass('active');
      ajaxing = false;
      return false;
    }
    else if (isnew)
    {
      html = ''
      for (let id = 0; id < res.length; id++)
      {
        if (res[id].status == 0)
        {
          newstatus = '<i class="fas fa-check"></i>'
        }
        else if(res[id].status == 1)
        {
          newstatus = '<i class="fas fa-check-double"></i>'
        }
        html += `<div class="messages__message message" id="msg${res[id].id}">
							    <div class="message__img">
							      <img src="/${res[id].authorimg}" alt="">
							    </div>
							    <div class="message__block">
							      <div class="message_top">
							        <div class="message__name">
                        <a href="/${res[id].author}">${res[id].author}</a>
                      </div>
							      	</div>
							      	<div class="message__text">
							      		${res[id].content}
							      	</div>
							        </div>
                      <div class="message__time">
									      <div>${res[id].time}</div>
									    <div class="message__status">${newstatus}</div>
								    </div>
							      </div>`;
      }
      $('.messages__container').empty();
      $('.messages__container').html(html);
      document.querySelector(".messages__right-messages").scrollTo(0,   document.querySelector(".messages__right-messages").scrollHeight);
    }
    else
    {
      if ($('.messages__container').find('p').length > 0)
      {
        $('.messages__container').find('p').remove();
      }

      let upperbound = res.length-1;
      let lowerbound = 0;
      if ($('.messages__container').children().last().length > 0)
      {
        for (let i = res.length-1; i >= 0; i--)
        {
          let newmsg = res[i].content.trim();
          let newstatus;
          if (res[i].status == 0)
          {
            newstatus = '<i class="fas fa-check"></i>'
          }
          else if(res[i].status == 1)
          {
            newstatus = '<i class="fas fa-check-double"></i>'
          }
          let oldmsg = $('.messages__container').children().last().find('.message__text').text().replace(/^\s+|\s+$/gm,'');

          let oldstatus = $('.messages__container').children().last().find('.message__status').html();

          if (oldmsg == newmsg && newstatus == oldstatus)
          {
            if (i == res.length-1)
            {
              ajaxing = false;
              return false;
            }
            break;
          }
          else
          {
            lowerbound = i;
          }
        }
      }
      html = ''
      let status;
      for (let id = lowerbound; id <= upperbound; id++)
      {
          if (res[id].status == 0)
          {
            status = '<i class="fas fa-check"></i>';
          }
          else if(res[id].status == 1)
          {
            status = '<i class="fas fa-check-double"></i>';
          }
          if ($(`#msg${res[id].id}`).length > 0)
          {
            if ($(`#msg${res[id].id}`).find('.message__status').html() != status)
            {
              $(`#msg${res[id].id}`).find('.message__status').html(status);
            }
            continue;
          }

          if (res[id].status == 0)
          {
            status = '<i class="fas fa-check"></i>';
          }
          else if(res[id].status == 1)
          {
            status = '<i class="fas fa-check-double"></i>';
          }
          html = `<div class="messages__message message" id="msg${res[id].id}">
							      <div class="message__img">
							      	<img src="/${res[id].authorimg}" alt="">
							      </div>
							      <div class="message__block">
							      	<div class="message_top">
							      		<div class="message__name">
                        <a href="/${res[id].author}">${res[id].author}</a>

                        </div>
							      	</div>
							      	<div class="message__text">
							      		${res[id].content}
							      	</div>
							      </div>
                    <div class="message__time">
									    <div>${res[id].time}</div>
									  <div class="message__status">${status}</div>
								</div>
							  </div>`;

            $('.messages__container').append(html);
            document.querySelector(".messages__right-messages").scrollTo(0,   document.querySelector(".messages__right-messages").scrollHeight);
      }
    }
    $('.messages__left').addClass("active");
	  $('.messages__right').addClass('active');
    touch.removeClass("new");
    ajaxing = false;
    isnew = false;
    }});
  });


  function getolder()
  {
    if (($('.messages__right-messages').scrollTop() <= (document.querySelector(".messages__right-messages").scrollHeight / 12)) && ($('.messages__container .message').length >= 40))
    {
      if (gettingolder)
      {
        return false;
      }
      gettingolder = true;
      lastmsgid = $('.messages__container').find(">:first-child").attr('id').substr(3)
        $.ajax( { type: 'POST', data: { lastmsgid: lastmsgid, username: username }, url : "/getmessages", success: function (res)
        {
          if (res[0] == -1)
          {
            gettingolder = false;
            return false;
          }
          else if (res[0] == 0)
          {
            gettingolder = true;
            return false;
          }
          else
          {
            html = ''
            let status;
            oldmsgamount = res.length;
            for (let id = oldmsgamount-1; id >= 0; id--)
            {
              if (res[id].status == 0)
              {
              status = '<i class="fas fa-check"></i>';
              }
              else if(res[id].status == 1)
              {
                status = '<i class="fas fa-check-double"></i>';
              }
              if (res[id].status == 0)
              {
                status = '<i class="fas fa-check"></i>';
              }
              else if(res[id].status == 1)
              {
                status = '<i class="fas fa-check-double"></i>';
              }
              image = $(this).find('.user__image img').attr('src');

              html = `<div class="messages__message message" id="msg${res[id].id}">
							      <div class="message__img">
							      	<img src="/${res[id].authorimg}" alt="">
							      </div>
							      <div class="message__block">
							      	<div class="message_top">
							      		<div class="message__name">
                        <a href="/${res[id].author}">${res[id].author}</a>

                        </div>
							      	</div>
							      	<div class="message__text">
							      		${res[id].content}
							      	</div>
							      </div>
                    <div class="message__time">
									    <div>${res[id].time}</div>
									  <div class="message__status">${status}</div>
								</div>
							  </div>`;
              $('.messages__container').prepend(html)
            }
            document.querySelector(".messages__right-messages").scrollTo(0, document.querySelector("#msg"+lastmsgid).offsetTop-200);
          }
          gettingolder = false;
        }
      });
    }
  }

  $('.close').click(function ()
  {
    $('#lastseen').text("").hide();
    closed = true;
    gettingolder = false;
    ajaxing = false;
    $('.messages__container').html(`              <div style="font-size: 30px; color: white; text-align: center; font-family: Roboto; display: flex; align-items: center; height: 100%;"><i class="fas fa-hand-point-left" style="font-size: 100px; margin-right: 10px;"></i>Click on a dialog</div> `);

	  $('.messages__left').removeClass("active");
	  $('.messages__right').removeClass('active');
    $('.userpicture').html("");
    $('.username').html("");
    $('.messages__right-send').hide();
    $('.user__card.active').removeClass("active");
    $(this).hide()
  });


  $("#send").click(function()
  {
    if ($('.messages__container').find('p').length > 0)
    {
      $('.messages__container').find('p').remove()
    }
    content = $("#content").val();
    username = $('.user__card.active').find(".user__name").text().trim();
    $.ajax( { type: 'POST', data: { username: username, content: content}, url : "/sendmessage", success: function ()
    {
      $('.user__card.active').click();
    }});
    $("#content").val("");
    $('.user__card.active').click();
    });

   $('.messages__right').on("click", '.userpicture', function ()
   {
     src = $(this).parent().find('.username a').attr('href')
     window.location.href = src;
   });

   function getconvs() {
    $.ajax( { type: 'POST', url : "/getconversations", success: function (res)
    {
      if (res[0] == 0 || res == "")
      {
        return false;
      }

      for (let id in res)
      {
        status = res[id].status;
        if (status == 1)
        {
          status = '<i class="fas fa-check-double"></i>';
        }
        else
        {
          status = '<i class="fas fa-check"></i>';
        }
        if ($('#'+res[id].userid).length > 0)
        {
          oldmessage = $('#'+res[id].userid).find('.user__message-msg').text().trim();
          oldmessage = oldmessage.substring(0, oldmessage.length-3);
          oldstatus = $('#'+res[id].userid).find('.user__message-status').html().trim();
          if (oldmessage != res[id].lastmsg)
          {
            if (res[id].userid == res[id].sentby)
            {
              $('.user__message-you').css("display", "none");
            }
            else
            {
              $('.user__message-you').css("display", "inline");
            }

            $('#'+res[id].userid).find('.user__message-msg').text(res[id].lastmsg+"...");

            if ($('#'+res[id].userid).hasClass('active') == false && res[id].sentby == res[id].userid)
            {
              $('#'+res[id].userid).addClass('new');
            }

            firstcard_uname = $('#'+res[id].userid).find(">:first-child").find('.user__name').text().trim();

            if (firstcard_uname != res[id].username)
            {
              toprepend = $('#'+res[id].userid).prop('outerHTML');
              $('#'+res[id].userid).remove();
              $('.user').prepend(toprepend);
            }
          }
          if (status != oldstatus)
          {
            $('#'+res[id].userid).find('.user__message-status').html(status);
          }

        }
        else
        {
          photo = res[id].photo;
          newcard = `<div class="user__card" id="${res[id].userid}">
						    <div class="user__image">
                  <img src="/${photo}" alt="">
                  <i class="status-indicator"></i>
						  </div>
						  <div class="user__body">
							  <div class="user__name">
								  ${res[id].username}
						  	</div>
                <div class="user__message">
								  <div class="user__message-content">
              	    <div class="user__message-you" style="display: none;">
										  <b>You:</b>
									  </div>
									  <div class="user__message-msg">
										  ${res[id].lastmsgid}...
									  </div>
								  </div>
								  <div class="user__message-status">
                    ${status}
								  </div>
							  </div>
					    </div>
				  	</div>`
            $('.user').prepend(newcard)
        }
      }
    }});
   }

  function checkallonlines()
  {
    if (executing)
    {
      return false
    }
    executing = true;
    $.ajax( { type: 'POST', url : "/checkallonlines", success: function (res)
    {
      if (res == -1 && $('.user').find('.user__card').length <= 0)
      {
        return false;
      }
        $(document.getElementsByClassName("user__card")).each(function ()
        {
        cardname = $(this).find('.user__name').text().trim();
        if (cardname in res)
        {
          if (res == 0)
          {
            return false;
          }
          else if (res[cardname] == 1)
          {
            $(this).find('.user__image').find(`.status-indicator`).show();
            if ($(this).hasClass('active'))
            {
              $('.userpicture').find('.status-indicator').show();
              $('#lastseen').text("").hide();
            }
          }
          else
          {
            if ($(this).hasClass('active'))
            {
              $('.userpicture').find('.status-indicator').hide();
              if (res[cardname].day && !closed)
              {
                $('#lastseen').text(`Seen ${res[cardname].day}/${pad(res[cardname].month)} ${pad(res[cardname].hour)}:${pad(res[cardname].minute)}`).show();
              }
            }
            $(this).find('.user__image').find(`.status-indicator`).hide();
          }
        }
        else
        {
          el = $(this);
          $.ajax( { type: 'POST', url : "/checkonline", data: { username: cardname }, success: function (data)
          {
          if (data == 0)
          {
            return false;
          }
          else if (data == 1)
          {
            el.find('.user__image').find(`.status-indicator`).show();
            if (el.hasClass('active'))
            {
              $('.userpicture').find('.status-indicator').show();
              $('#lastseen').text("").hide();
            }
          }
          else
          {
            if (el.hasClass('active'))
            {
              $('.userpicture').find('.status-indicator').hide();
              $('#lastseen').text(`Seen: ${data.day}/${pad(data.month)} ${pad(data.hour)}:${pad(data.minute)}`).show();
            }
            el.find('.user__image').find(`.status-indicator`).hide();
          }
          }});
        }
      });
    executing = false;
    }});
   }

   checkallonlines();

   setInterval(getconvs, 1000);
   setInterval(function () {
     $('.user__card.active').click();
   }, 1000);
   setInterval(getolder, 1000);
   setInterval(checkallonlines, 2000);
});


function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}