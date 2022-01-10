let sex = ""
let lookingfor = ""
var good_color = "#66cc66";
var bad_color  = "#ff6666";

$(document).ready(function () {
	$('.right__body-1').hide(0);
	$('.right__option').click(function () {
		let i = $(this).data("answ1");
		parr = $(this).parents('.right__body')

		if (sex == "")
    {
			if (i == 1)
				sex = "Male";
			else if (i == 2)
				sex = "Female";
			else
				sex = "error"
		}

		else if (lookingfor == "")
    {
			if (i == 1)
				lookingfor = "Male";
			else if (i == 2)
				lookingfor = "Female";
			else
				lookingfor = "error"
			$('.right__body').not(parr).replaceWith($(`<div class="right__body"><form class="regform" action="/registration" method="POST"><input type="hidden" name="sex" value="${sex}"><input type="hidden" name="lookingfor" value="${lookingfor}"><label for="username">Username</label><input required id="username" onKeyup="check()" type="text" class="regform__input _req" name="username" autocomplete="off" placeholder="Username"><label for="email">Email</label><input type="email" name="email" id="email" onKeyup="check()" placeholder="Email" class="regform__input"><label for="password">Password</label><input required id="password" type="password" class="regform__input" name="password"	placeholder="Password" onKeyup="check()"><label for="rpass">Repeat password</label><input required id="rpass" type="password" onKeyup="check()" class="regform__input" name="password-repeat"	placeholder="Repeat Password"><label for="age">Age</label><input required id="age" type="number" class="regform__input" name="age" onKeyup="check()" placeholder="Age" onchange="check()" min="0"	max="123"><input type="submit" id="submitbtn" disabled value="Sign Up" class="right__option disabled"></form></div>`))
			$('.right__body').not(parr).hide()
		}
		$('.right__body').fadeOut(50);
		setTimeout(function () {
			$('.right__body').not(parr).fadeIn(500);
		}, 51);
	})
});


function turn(state){
  if (state == "off")
  {
    document.getElementById('submitbtn').disabled = true;
     document.getElementById('submitbtn').classList.add("disabled");
  }
  else
  {
    document.getElementById('submitbtn').disabled = false;
    document.getElementById('submitbtn').classList.remove("disabled");
  }
}


function validateEmail(email) {
  const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}


function error(text){
  var error = $('.right__body').find('.errorz')
  if (error.length==0)
  {
    $(".right__body").prepend("<div class=\"error errorz\">"+ text + "</div>")
  }
  else
  {
    error.text(text)
  }
}


function check_pass(){
  var password = $('#password');
  var confirm  = $('#rpass');
  if(password.val().length < 6)
  {
    password.css('border-color', bad_color);
    error("Password gotta be at least 6 characters long.");
    return false;
  }
  else
  {
    password.css('border-color', good_color);
    if(password.val() == confirm.val() && password.val() != "")
    {
      confirm.css('border-color', good_color);
      error("");
      return true;
    }
    else
    {
      confirm.css('border-color', bad_color);
      error("Passwords do not match.")
      return false;
    }
  }
};


function check_email(){
  var email = $('#email');
  if (validateEmail(email.val()))
  {
    email.css('border-color', good_color);
    error("");
    return true;
  }
  else
  {
    email.css('border-color', bad_color);
    error("Please enter a valid email");
    return false;
  }
}


function check_uname(){
  var uname = $('#username');
  if (uname.val().length > 5)
  {
    uname.css('border-color', good_color);
    error("");
    return true;
  }
  else
  {
    uname.css('border-color', bad_color);
    error("Username gotta be at least 6 character long.");
    return false;
  }
}


function check_age(){
  var age = $('#age');
  if (parseInt(age.val()) > 17)
  {
    age.css('border-color', good_color);
    error("");
    return true;
  }
  else
  {
    age.css('border-color', bad_color);
    error("You gotta be at least 18 year old to enter the website. Sorry.");
    return false;
  }
}

function check(){
  if (check_uname() && check_email() && check_pass() && check_age())
  {
    turn("on");
  }
  else{
    turn("off");
  }
}