$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active");
	$('#manage_explore').addClass("active");
	$('#page_id').val(2);

    $.post("/MDI/plotMultiTrace", function(data) {
        $("#multiTrace").html(data);
    })
    .error(function() {alert("error128"); });
});