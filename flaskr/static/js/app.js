$(document).ready(function() {
	function update_graph() {
		console.log('in update_graph');
		var new_html = '';
		$.ajax({
			url: '/update_graph',
			asnyc: false,
			dataType: 'text',
			success: function(text) {
				new_html = text;
				console.log(new_html);
			}

		});


		setTimeout(function(){
			console.log('REDRAW');
			update_graph();
		}, 500);
		
		document.body.innerHTML = new_html;
		return new_html;
	}

	// Initial call to update_graph()
	console.log('here');
	update_graph();

});
