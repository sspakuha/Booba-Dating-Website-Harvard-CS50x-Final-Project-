min = $('#lowernum').val();
max = $('#uppernum').val();

if (min == null || min == "")
{
  min = 18;
  max = 101;
}
else
{
  min = parseInt(min);
  max = parseInt(max);
}

var vm = new Vue({
	el: '#slider',
  data: {
		minAngle: min,
		maxAngle: max
	},
	computed: {
		sliderMin: {
			get: function () {
				var val = parseInt(this.minAngle);
				return val;
			},
			set: function (val) {
				val = parseInt(val);
				if (val > this.maxAngle)
        {
					this.maxAngle = val;
				}
				this.minAngle = val;
			}
		},
		sliderMax: {
			get: function () {
				var val = parseInt(this.maxAngle);
				return val;
			},
			set: function (val) {
				val = parseInt(val);
				if (val < this.minAngle)
        {
					this.minAngle = val;
				}
				this.maxAngle = val;
			}
		}
	}
});

function checklen() {
	searchfield = $('#searchfield')
	if (searchfield.val().length > 25) {
		searchfield.val(searchfield.val().substr(0, 25))
		return false;
	}
}

$(document).ready(function () {
  $('#loadmore').click(function () {
    let upperage = $('#uppernum').val();
    let lowerage =  $('#lowernum').val();
    let hasphoto = $('#hasphoto').is(":checked");
    if (hasphoto == true)
    {
        hasphoto = 1;
    }
    else
    {
      hasphoto = null;
    }
    let country = $('#country').val();
    if (!country)
    {
      country = null;
    }
    let city = $('#city').val();
    if (!city)
    {
      city = null;
    }
    let genders = $(".sectionleft__grp-radio");
    let gender;
    for (let i = 0; i < genders.length; i++)
    {
      let status = $(genders[i]).find('#radio').is(":checked");
      if(status)
      {
        gender = $(genders[i]).find('#radio').val();
        break;
      }
    }
    let query = $('#searchfield').val().trim();

    let lastusername = $(".users").find(">:last-child").find('.users__login').text().trim();

    $.ajax( { type: 'POST', data: { upperage: upperage, lowerage: lowerage, hasphoto: hasphoto, country: country, city: city, gender: gender, query: query, lastusername: lastusername }, url : "/getsearch", success: function (data)
    {
      length = data.length;
      if (length < 10)
      {
        $('.users__buttonmore').hide();
      }

      for (let i = 0; i < length; i++)
      {
        uname = data.rs[i].username;
        age = data.rs[i].age;
        gender_id = data.rs[i].gender_id;

        locationz = data.locations[i];
        if (locationz != 'Unset')
        {
          locationz = "Country: " + locationz;
        }
        else
        {
          locationz = "";
        }

        if (gender_id == 1)
        {
          gender_id = "Male"
        }
        else
        {
          gender_id = "Female"
        }

        favorites = data.favorites;

        favtext = "";
        for (let j = 0; j < data.favorites.length ; j++)
        {
          if (data.favorites[j] == data.rs[i].id)
          {
            favtext = `<i class="far fa-star"></i>
            Unfavorite`;
          }
        }

        if (favtext == "")
        {
          favtext = `	<i class="fas fa-star"></i>
				  Favorite`;
        }

        $('.users').append(`
        <div class="users__body">
								<div class="users__left">
									<a class="users__image" href="/${uname}">
										<img src="./${data.images[i]}" alt="">
									</a>
									<div class="users__block">
										<a class="users__login" href="/${uname}">
											${uname}
										</a>
										<a class="users__item">
											Age: ${age}
										</a>
										<a class="users__item">
											Sex: ${gender_id}
										</a>
										<a class="users__item">
                      ${locationz}
										</a>
									</div>
								</div>

								<div class="users__block users__block-f">
									<a class="users__item users__item-h" id="favorite" style="cursor: pointer;">
                      ${favtext}
									</a>
									<a class="users__item users__item-h msg" style="cursor: pointer;">
										<i class="fas fa-envelope"></i>
										Write message
									</a>
                  <form method="POST" action="/messages" style="display: none;">
                  <input type="hidden" name="username" value="${uname}">
                  </form>
								</div>
							</div> `);
      }
    }});
  });


  $('.users').on('click', '.msg', function() {
    $(this).next().submit()
  })

  $('.users').on('click', '#favorite', function() {
    item = $(this).parent().prev().find(".users__login");
    username = $(this).parent().prev().find(".users__login").text().trim();
    let res;

    $.ajax( { type: 'POST', data: { username: username }, url : "/favorite", async : false, success: function (data)
    {
      res = data.text;
    }});
    if (res != -1)
    {
        $(this).html(res);
    }
  });


	sf = $('#searchfield')
	sf.on("keyup", function () {
		checklen();
	})
	sf.on("change", function () {
		checklen();
	})
	sf.on("mouseleave", function () {
		checklen();
	})


	$('#options, .sectionleft__hidden').click(function () {
		window.scrollTo(0, 0);
		$('.sectionleft__body').toggleClass("active")
		$('.sectionleft').toggleClass("active")
		$('body').toggleClass("lock")
	});

  $('.sectionleft__grp-radio').click(function (){
    $(this).find("input").prop("checked", true);
  });
});
