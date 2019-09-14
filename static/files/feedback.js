$(document).ready(function() {

	$("#feedback-button").click(function() {

		var regno = $("input[name='regno']").val().trim();
		var query = $("textarea[name='query']").val().trim();

		if(regno != '' && query != '') {

			$("#feedback-button").addClass("elastic loading");

			$.ajax({
				url: "/feedback",

				data: {
					regno: regno,
					query: query
				},

				success: function(x,y) {

					$("input[name='regno']").val('');
					$("textarea[name='query']").val('');
					$("#message").modal('hide');

					$('body')
					  .toast({
					  	class: 'success',
					  	displayTime: 10000,
					    message: 'Your problem has been saved. We will try to fix it. Come back in an hour.'
					  });
				},

				error: function(xhr) {
					$("input[name='regno'").val('');
					$("textarea[name='query']").val('');
					$("#message").modal('hide');

					$('body')
					  .toast({
					    class: 'error',
					    displayTime: 10000,
					    message: 'An error occured while saving your feedback. Please try again!'
					  });
				},

				complete: function() {
					$("#feedback-button").removeClass("elastic loading");
				},

				type: 'GET'

			});
		}

	});
});