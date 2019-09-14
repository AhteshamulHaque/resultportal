
$(document).ready(function() {

  if(sessionStorage.getItem("not_logged_in") == "true") {
    sessionStorage.removeItem("not_logged_in");
    alert("Please enter your Registration Number first");
  }



  $("#form").submit(function(e) {
      e.preventDefault();
      console.log("Default prevented");

      if($("input[name='roll']").val().trim() != '') {
        $("#load").modal({
          blurring: true,
          closable: false,
          duration: 100,
        }).modal('show');

        validate_and_login_user($("input[name='roll']").val());
      }
  });

  function validate_and_login_user(roll) {

    //make request for a new login
    student_request = $.ajax({

        url: '/',
        type: 'POST',
        data: { roll: roll },

        success: function(student) {
            //insert into recent files
            console.log("Success: ", student);
            if(localStorage.getItem('recent_login') == null || localStorage.getItem('recent_login') == undefined || localStorage.getItem('recent_login') == '')
              localStorage.setItem('recent_login', JSON.stringify(Array(student)));

            else {
              var previous_login = JSON.parse(localStorage.getItem('recent_login'));

              var found = 0;
              previous_login.forEach((value) =>  {
                if(value['roll'] == student['roll']) {
                  found = 1;
                }
              });


              if(found == 0) {
                  previous_login.unshift(student);
                  if(previous_login.length > 3)
                    previous_login.pop();
              }

                localStorage.setItem('recent_login', JSON.stringify(previous_login));
              }

            // $(".load.modal").modal("hide").modal("hide all"); //hiding modal if success because if you come back by clicking back button the modal still loads
            var urlParams = new URLSearchParams(location.search)

            if (urlParams.has('next') && urlParams.get('next').trim() != '') {

              location.href = urlParams.get('next');

            } else {
              location.href = "/profile";
            }

          },

        error: function(xhr, status, error) {

            //show error message and let user login again
            $("#load").modal("hide").modal("hide all");

            if(status != "abort") {
              console.log("Abort not executed");
              $("#error").modal({
                blurring: true,
                duration: 100
              }).modal("show");

            }
        },
        dataType: "JSON"
    });
  }

  function show_recent_logins() {
    var logins = JSON.parse(localStorage.getItem('recent_login'));

    if(localStorage.getItem('recent_login') != null && localStorage.getItem('recent_login') != undefined && localStorage.getItem('recent_login') != '') {

      var recent_html = '<div id = "recent" style = "text-align: left;"><h3 class="ui top attached header">Recent Login</h3><div class="ui attached segment"><div class="ui middle huge aligned relaxed divided list">';

      for(var i = 0; i < logins.length; ++i) {
        recent_html += '<div class = "recent-login-item item"><img class="ui tiny image" src = "/static/images/placeholder.png" style = "max-height: 40px; max-width: 50px" data-src="/static/images/'+logins[i]['image_id']+'"><div class="content"><a style = "font-size: .61em; padding: .5em 0" class="header" data = "'+logins[i]['roll']+'">'+logins[i]['name']+" [ "+logins[i]['roll'] + ' ]</a></div></div>';
      }
      recent_html += '</div></div></div>';

      $(recent_html).insertAfter("#form");
    }

    $(".recent-login-item").click(function(e) {

    $("#load").modal({
      blurring: true,
      closable: false,
      duration: 100
    }).modal('show');

    validate_and_login_user($(this).find("a").attr("data"));

  });

  }

  show_recent_logins();

  $('img')
  .visibility({
    type       : 'image',
    transition : 'fade in',
    duration   : 0
  });

  var urlParams = new URLSearchParams(location.search);

  if(urlParams.has('next') && urlParams.get('next').trim() != '') {

    $('body')
    .toast({
      displayTime: 0,
      class: 'warning inverted',
      showIcon: 'info',
      message: 'You need to submit your registration number to continue'
    });

  }
});
