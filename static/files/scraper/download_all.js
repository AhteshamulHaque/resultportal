  function pad_roll(roll, size) {
    var s = roll+"";
    while (s.length < size) s = "0" + s;
    return s;
  }

  $("#all").click(function() {
      $(".specific").click();
      $(this).addClass("disabled");
  });

  $(".specific").click(function() {
    var roll_regex = $(this).attr("branch-to-download");
    var semester = $(this).attr("semester");

    var ignore_rolls = [];
    var conf = {
      previous_miss: undefined,
      total_miss: 0,
      percent: Number( $("div[download-progress='"+roll_regex+semester+"']").attr("data-percent") )
    };
    var downloaded_info = $("div[downloaded-info='"+roll_regex+semester+"']").children();

    for(var i = 0; i < downloaded_info.length; ++i) {
      ignore_rolls.push( downloaded_info[i].getAttribute("roll") );
    }

    //.specific is removed so that when download all is clicked it doesn't get restarted
    $(this).addClass("disabled").removeClass(".specific");

    var roll_number_length = 3;
    
    if(roll_regex.slice(4, 6) == "PG" || roll_regex.slice(0,3) == "TYC") {
      roll_number_length = 2;
    }

    download_recursively(1, ignore_rolls, roll_regex, semester, conf, roll_number_length);
  });

/*********************************************** recursive downloader of the student ********************************************************************/
  function download_recursively(start_roll, ignore_rolls, roll_regex, semester, conf, roll_number_length) {

    //first check for existing data or the roll in downloaded
      var index = ignore_rolls.indexOf( (roll_regex + pad_roll(start_roll, roll_number_length)) );
      if(index == -1) {

        $.ajax({
          url: '/student/'+(roll_regex + pad_roll(start_roll, roll_number_length))+"?save=true&semester="+semester,

          // beforeSend: () => { console.log("Making request for "+ roll_regex + pad_roll(start_roll, roll_number_length) ); },
          //one by one update db and html page
          success: function(result) {

              //update page here
              $("div[downloaded-info='"+roll_regex+semester+"']").append('<div class = "item" roll="'+result['roll']+'"><span class = "ui text small">'+result['name']+' ('+result['roll']+')</span></div>');
              console.log("Got result for "+ roll_regex + pad_roll(start_roll, roll_number_length) + ", Semester: " + semester );
              //update percent and ui list

                if( conf['percent'] < 98)
                  conf['percent'] += 1;

                $("div[download-progress='"+roll_regex+semester+"']").progress({ percent: conf['percent'] });
                $("span[download-count='"+roll_regex+semester+"']").text(conf['percent']);

              download_recursively(start_roll+1, ignore_rolls, roll_regex, semester, conf, roll_number_length);
          },

          error: function(xhr) {
            console.log("Missed for "+roll_regex+pad_roll(start_roll, roll_number_length)+ " " + semester);
            if(xhr.status == "503") { //to not complete download because of network failure 503
              xhr.abort();

            } else if(conf['total_miss'] < 5) {
              // console.log("Missed one");
              // console.log("Previous miss: "+ missing_conf[sem_table_name]['previous_miss']);
              // console.log("Current roll: "+start_roll)

              if(conf['previous_miss'] == undefined || conf['previous_miss']+1 == start_roll) {
                // console.log("Miss count increased by one");
                conf['total_miss'] += 1;
              }
              else {
                // console.log("Previous and current roll do not match");
                // console.log("Miss count reset to 1");
                conf['total_miss'] = 1;
              }
              conf['previous_miss'] = start_roll;

              download_recursively(start_roll+1, ignore_rolls, roll_regex, semester, conf, roll_number_length);

            } else {

                $.ajax({
                  url: '/student/'+(roll_regex + pad_roll(start_roll, roll_number_length))+"?complete=true&semester="+semester,

                  success: function() {
                    console.log("Completed");
                    $("div[download-progress='"+roll_regex+semester+"']").progress({ percent: 100 });
                  }
                });

            }
          },

        });
        //student data is already present in already downloaded data...
      } else {
        console.log("Student "+roll_regex+pad_roll(start_roll, 3) + " is already present");
        download_recursively(start_roll+1, ignore_rolls, roll_regex, semester, conf, roll_number_length);
      }


  }
