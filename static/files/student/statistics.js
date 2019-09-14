(function() {
	var lastly_close_icon_on = undefined;
	var max_semester = 10;
	var last_semester = $("#predictor_container").attr("last-semester");

	var min_slider_value = 4;
	var max_slider_value = 10;
	//last semester is the number of the semester last attended eg: 1.. 2.. 3.. 4.. 5 <- last semester 
	var sgpa_array = [];

	//length - 1 so the sgpa can include the total sum the array will be like [ 0 , 0 , 0, sum, other predicted results ]
	for(var i = 0; i < Number(last_semester) -1; ++i)
	{
		sgpa_array.push(0);
	}

	sgpa_array.push( Number( $("#predicted_cgpa").text() ) * Number( last_semester ) );

	$("#add_predictor").click(function() {
		last_semester = add_predictor();
		//After #last_semester below the cgpa in predictor
		$("#last-semester").text(last_semester);
	});


	function add_predictor() {

		if(max_semester != last_semester) {
			$("i[semester-icon='"+last_semester+"']").remove();
			
			last_semester++;
			var predictor = '<div class = "ui column"><div class = "ui segment container"><div semester-slider = "'+last_semester+'" class = "ui slider" style = "margin: 10px 0 !important"></div><div icon-to-attach = "'+last_semester+'" class="ui top attached label">SEMESTER '+last_semester+'<i semester-icon = "'+last_semester+'" class = "ui text red close icon" style = "float: right"></i></div><div class="ui bottom attached label">SGPA <span semester-sgpa = "'+last_semester+'">0</span></div></div></div>';
			$("#predictor_container").append(predictor);

			lastly_close_icon_on = last_semester;	

			$(".close").click(remove_predictor);

			sgpa_array.push(min_slider_value);

			$("div[semester-slider='"+last_semester+"'").slider({
				min: min_slider_value,
				max: max_slider_value,
				step: 0.1,
				onMove: function(value) {
					//update the value of the sgpa according to slider
					$("span[semester-sgpa='"+$(this).attr("semester-slider")+"'").text(value);
					var index = Number( $(this).attr("semester-slider") );

					sgpa_array[index-1] = Number(value); //index-1 because of usual index starting from 0

					//calculate the cgpa
					var sum = sgpa_array.reduce( function(total, num) {
						return total+num;
					});

					$("#predicted_cgpa").text( ( sum / sgpa_array.length ).toFixed(2) );
					
				}
			});
		}

		return last_semester;
	}

	function remove_predictor() {
		$(this).parent().parent().parent().remove();
		last_semester--;

		$("div[icon-to-attach='"+last_semester+"']").append('<i semester-icon = "'+last_semester+'" class = "ui close icon" style = "float: right"></i>');

		lastly_close_icon_on = last_semester;


		//remove the last predictor sgpa from the array
		sgpa_array.pop();

		//calculate the cgpa
		var sum = sgpa_array.reduce( function(total, num) {
					return total+num;
				});
		$("#predicted_cgpa").text( ( sum / sgpa_array.length ).toFixed(2) );
		$("#last-semester").text(last_semester);

		// ...since I delete the previous close icon(<i> element) and add a new one
		// the event, which was associated with the deleted close icon also doesnot work
		// because it is bind with the previous close icon..hence the new click handler 
		$(".close").click(remove_predictor);	
	}
})();

	// this is the predictor html
	// <div class = "ui column">
	// 	<div class = "ui inverted green tertiary segment container">
	// 	  <div semester-slider = "for selecting this slider" class = "ui slider" style = "margin: 10px 0 !important"></div>
	// 	  <div class="ui top attached black label">SEMESTER last_semester+1<i semester-icon = "last_semester" class = "close icon" style = "float: right"></i></div>

	// 	  <div class="ui bottom attached black label">SGPA <span semester-sgpa = "for selecting this sgpa">0</span></div>
	// 	</div>
	// </div>
