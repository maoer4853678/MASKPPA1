$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active");
	$('#manage_search').addClass("active");
	$('#page_id').val(1);

    $('#button_select').click(function(){
		$.post("/MDI/plotBarchart", function(data) {
            $("#Tool_Time").html(data);
        })
        .error(function() {alert("error"); });
	});

    function plotTraceLineJS() {
        $.post("/MDI/plotTraceLine",{
		    'filter':0,
            'machine': $('#div_machine_list').children().eq(0).val(),
            'main_assem': $('#div_main_assem_list').children().eq(0).val(),
            'sub_assem': $('#div_sub_assem_list').children().eq(0).val(),
            'component': $('#div_component_list').children().eq(0).val()
		},  function(data) {
            $("#TraceLine_Hide").html(data);
        })
        .error(function() {alert("error127"); });
    };

//    finding submit configuration
	$('#Finding_Submit').click(function(){
        if (confirm("Confirm to submit?")) {
            $('#TraceLine_Hide').html("");
            $('#Tool_Time').html("");
            $('#asdasd').hide();
            $.post("/MDI/submit_finding", {
                "machine": $('#div_machine_list').children().eq(0).val(),
                'main_assem': $('#div_main_assem_list').children().eq(0).val(),
                'sub_assem': $('#div_sub_assem_list').children().eq(0).val(),
                'component': $('#div_component_list').children().eq(0).val(),
                'category': $('#finding_category').val(),
                'sub_category': $('#finding_sub_category').val(),
                'chart': $('#finding_chart').val(),
                'item': $('#item_id').val()
            });
        };
	});
//	submit predict failure time to table in database
    $('#Prediction_Submit').click(function(){
        $.post("/MDI/submit_predict", {
            "machine": $('#div_machine_list').children().eq(0).val(),
            'main_assem': $('#div_main_assem_list').children().eq(0).val(),
            'sub_assem': $('#div_sub_assem_list').children().eq(0).val(),
            'component': $('#div_component_list').children().eq(0).val(),
            'predict_failure': $('#prediction_failure').val()
        }, function(data) {
            $.post("/MDI/plotTraceLine",{
                'filter':0,
                'machine': $('#div_machine_list').children().eq(0).val(),
                'main_assem': $('#div_main_assem_list').children().eq(0).val(),
                'sub_assem': $('#div_sub_assem_list').children().eq(0).val(),
                'component': $('#div_component_list').children().eq(0).val()
            },  function(data) {
                $("#TraceLine_Hide").html(data);
            })
        });
    });
// =====================================================================================================================
//	=========================================== select change ==========================================================
//  ====================================================================================================================
//  machine
    $.post("/MDI/select_machine_events", { "changed": 0 }, function(data){ //
        $("#div_machine_list").html(data);
	});
//  main assem
	$.post("/MDI/select_main_assem_events", { "changed": 0 }, function(data){ //
        $("#div_main_assem_list").html(data);
	});

	$("#div_machine_list").on("change", function() {
	    $.post("/MDI/select_main_assem_events", { "selected_machine": $('#div_machine_list').children().eq(0).val(), "changed": 1 }, function(data){ //
            $("#div_main_assem_list").html(data);
            $.post("/MDI/select_sub_assem_events", { 'selected_main_assem': $('#div_main_assem_list').children().eq(0).val(), 'changed': 1 }, function(data){ //
                $("#div_sub_assem_list").html(data);
                $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list').children().eq(0).val(), 'changed': 1 }, function(data){ //
                    $("#div_component_list").html(data);
                    plotTraceLineJS()
                });
            });
        });
	});
//  sub assem
	$.post("/MDI/select_sub_assem_events", { 'changed': 0 }, function(data){ //
        $("#div_sub_assem_list").html(data);
	});

	$("#div_main_assem_list").on("change", function() {
        $.post("/MDI/select_sub_assem_events", { 'selected_main_assem': $('#div_main_assem_list').children().eq(0).val(), 'changed': 1 }, function(data){ //
            $("#div_sub_assem_list").html(data);
            $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list').children().eq(0).val(), 'changed': 1 }, function(data){ //
                $("#div_component_list").html(data);
                plotTraceLineJS()
            });
        });
	})

//   component
	$.post("/MDI/select_component_events", { 'changed': 0 }, function(data){ //
        $("#div_component_list").html(data);
	});

	$('#div_sub_assem_list').on('change', function() {
	    $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list').children().eq(0).val(), 'changed': 1 }, function(data){ //
            $("#div_component_list").html(data);
            plotTraceLineJS()
        });
	});

//
});

