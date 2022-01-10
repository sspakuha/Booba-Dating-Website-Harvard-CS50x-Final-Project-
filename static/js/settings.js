$(document).ready(function () {
  $('#npassword, #npasswordr').keyup(function (){
    if ($('#npassword').val().length < 6)
    {
      $('#npassword').css("border-bottom", "1px solid red");
    }
    else
    {
      $('#npassword').css("border-bottom", "1px solid white");
    }

    if ($('#npassword').val() != $('#npasswordr').val())
    {
      $('#npasswordr').css("border-bottom", "1px solid red");
    }
    else{
      $('#npasswordr').css("border-bottom", "1px solid white");
    }
  })
});