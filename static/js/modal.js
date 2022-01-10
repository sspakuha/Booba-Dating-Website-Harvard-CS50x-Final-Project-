$(document).ready(function () {
  cursor = null;
  $('.content__image').click(function()
  {
    cursor = $(this);
    $('body').addClass("lock");

    $('#image').attr("src", "");

    image = $(this).find('img').attr('src');
    $('#image').attr("src", image);

    $('#picid').val($(this).find('img').attr('alt'));
    $('#picidavatar').val($(this).find('img').attr('alt'));

    $('.modal').fadeIn(200);
  });

  $('.modal__darken').click(function()
  {
    $('body').removeClass("lock");
    $('.modal').hide();
  })

  $('.modal__arrow-l').click(function()
  {
    if (cursor.prev().hasClass("small__plus") || cursor.prev().length <= 0)
    {
      cursor = cursor.parent().find(".content__image").last();
    }
    else
    {
      if (cursor.prev().length > 0)
        cursor = cursor.prev();
      else
        cursor = $('.content').find(">:last-child");
    }

    image = cursor.find('img').attr('src');

    $('#picid').val(cursor.find('img').attr('alt'));
    $('#picidavatar').val(cursor.find('img').attr('alt'));

    $('#image').attr("src", image);
  });

  $('.modal__arrow-r').click(function()
  {
    if (cursor.next().hasClass("small__plus") || cursor.next().length <= 0)
    {
      cursor = cursor.parent().find(".content__image").first();
    }
    else
    {
      if (cursor.next().length > 0)
        cursor = cursor.next();
      else
        cursor = $('.content').find(">:first-child");
    }

    image = cursor.find('img').attr('src');

    $('#picid').val(cursor.find('img').attr('alt'));
    $('#picidavatar').val(cursor.find('img').attr('alt'));

    $('#image').attr("src", image);
  });
});
