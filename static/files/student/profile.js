$(document).ready(function() {

    //get the failed sems from the page using javascript and request for them again

  $("#refresh_result").click(function() {

        var sems_failed = [];

        $(".result_status").each(function(val) {

            if ( $(this).text() == "FAIL" )
                sems_failed.push(  { roll: $(this).attr("roll"), semester: $(this).attr("semester") } );

        });


        //show loading modal before requesting
        $("#load").modal({
                    blurring: true,
                    closable: false,
                    onHide: () => { $("#sem_list").empty(); $("#update-sem-message").empty(); $("#load-approve").addClass("disabled"); }
        }).modal("show");

        $("#sems_list").empty();
        $("#update-sem-message").empty();
        $("#load-approve").addClass("disabled");

        //update loading semseter
        for(var i = sems_failed.length-1; i >= 0; --i) {
            $("#sems_list").append('<li class = "item"><i id = "updating-sem-loader-'+sems_failed[i]['semester']+'" class="notched black circle loading icon"></i> Semester '+sems_failed[i]['semester']+"</li>");
        }

        var all_sem_passed = true;
        update_recursively(sems_failed, all_sem_passed);

    });

    function update_recursively(sems_failed, all_sem_passed) {

        if(sems_failed.length == 0) {


            if(all_sem_passed) {

                $("#sems_list").append('<li class = "item"><i id = "updating-ranklist" class="notched black circle loading icon"></i> Updating rank list</li>');

                $.ajax({
                    url: 'https://nilekrator.pythonanywhere.com/updaterank',

                    success: function(result) {

                        //finally clear and show success messages
                        $("#updating-ranklist").removeClass("notched black circle loading").addClass("green check");
                        $("#update-sem-message").html("<span class = 'ui green text'>Congrats! You have cleared all your semesters. Refresh the page to see the effects.</span>");
                    },

                    error: function() {
                        $("#sems_list").empty();
                        $("#sems_list").html("<li class = 'item'><span class = 'ui red text'><i class = 'exclamation icon'></i> There was a problem. Try again Later.</span></li>");
                        $("load-approve").removeClass("disabled");
                    },

                    timeout: 15000,

                    dataType: 'JSON'
                });

            } else {

                $("#update-sem-message").html("<span class = 'ui red text'>You have not passed all the semesters. Cannot update rank</span>");
            }

            $("#load-approve").removeClass("disabled");

            return;
        }

        else {
            var sem = sems_failed.pop();

            $.ajax({
                url : 'https://nilekrator.pythonanywhere.com/student/'+sem['roll']+"?save=true&semester="+sem['semester'],

                success: function(result) {

                    if( Number(result['cgpa']) > 0) {

                        $("#updating-sem-loader-"+sem['semester']).removeClass("notched black circle loading").addClass("check green");

                    } else {

                        all_sem_passed = false;
                        $("#updating-sem-loader-"+sem['semester']).removeClass("notched black circle loading").addClass("red close");

                    }

                    update_recursively(sems_failed, all_sem_passed);
                },

                error: function() {
                    $("#sems_list").empty();
                    $("#sems_list").html("<li class = 'item'><span class = 'ui red text'><i class = 'exclamation icon'></i> There was a problem. Try again Later.</span></li>");
                    $("load-approve").removeClass("disabled");
                },

                timeout: 15000,

                dataType: 'JSON'
            });

        }

    }


});
