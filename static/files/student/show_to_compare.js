$(document).ready(function() {

  var selected_rolls = [];

  // $(".ui.master").checkbox({
  //   onChecked: function() {

  //     $(this).find("tr").addClass("active");
  //     $(".ui.student").checkbox('check');
      
  //   },

  //   onUnchecked: function() {
  //     $(this).find("tr").removeClass("active");
  //     $(".ui.student").checkbox('uncheck');
  //   }
  // });

  //particular student checkbox
  $(".ui.student").checkbox({
    onChecked: function() {
      selected_rolls.push($(this)[0].value);
      $(this).parent().parent().parent().addClass("active");
    },

    onUnchecked: function() {
      selected_rolls.splice( selected_rolls.indexOf($(this)[0].value), 1);
      $(this).parent().parent().parent().removeClass("active");
    }
  });

  $("#compare-btn").click(function(e) {
      e.preventDefault();

      if(selected_rolls.length != 0) {
        $("form").submit();  
      } else {
        alert("Select rolls to compare");
      }
  });

  $(".ui.dropdown").dropdown({
    onChange: function(value) {
      $("#compare-btn").addClass("disabled");
      location.href = '/compare?semester='+value;
    }
  });

});
