$(document).ready(function() {

	function update_graph() {
		// console.log('in update_graph');
		var new_html = '';
		$.ajax({
			url: '/update_graph',
			asnyc: false,
			dataType: 'html',
			success: function(html) {
				// console.log(html);
				$("#GraphContent").html(html);
			}

		});

		// document.body.innerHTML = new_html;
		// return new_html;

		setTimeout(function(){
			console.log('REDRAW');
			update_graph();
		}, 1000);
		
		
	}

	// Initial call to update_graph()
	console.log('here');
	update_graph();

});
