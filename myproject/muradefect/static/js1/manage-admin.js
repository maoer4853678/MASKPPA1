$(document).ready(function(){
    $(".nav.navbar-nav > li").removeClass("active");
	$('#manage_admin').addClass("active");
	$('#page_id').val(0);
    /* engine table*/
	var maint_ID, maint_Machine, maint_Amount, maint_Break_down, selected_row_maint, flag_op_maint;
	var maint_Main_assem, maint_Sub_assem, maint_Component, maint_SparepartNO;
	var maint_Failure_type, maint_Failure_cause, maint_Failure_time, maint_Maint_work;

	$('#button-query-maint').click(function(){
		$.post("/MDI/manage_admin_query_maint", function(data){
			$("#area-maint-table").html(data);
		})
		.error(function() { alert("Error3"); });
	});

	$('#button-add-maint').click(function(){
		$.post("/MDI/manage_admin_add_maint",{
		"Break_down": $("#maint_Break_down").val(),
		"Machine": $('#div_machine_list0').children().eq(0).val(),
		"Amount": $("#maint_Amount").val(),
		"Main_assem": $('#div_main_assem_list0').children().eq(0).val(),
		"Sub_assem": $('#div_sub_assem_list0').children().eq(0).val(),
		"Component": $('#div_component_list0').children().eq(0).val(),
		"SparepartNO": $("#maint_SparepartNO").val(),
		"Failure_type": $("#maint_Failure_type").val(),
		"Failure_cause": $("#maint_Failure_cause").val(),
		"Failure_time": $("#maint_Failure_time").val(),
		"Maint_work": $("#maint_Maint_work").val() },  function(){
			$.post("/MDI/manage_admin_query_maint", function(data){
				$("#area-maint-table").html(data);
			})
			bootbox.alert("Daten wurden erfolgreich hinzugefügt!")
		})
		.error(function() { alert("Error5"); });
	});

	$('#button-delete-maint').click(function(){
	    bootbox.confirm({
	        message: "Ausgewählte Zeile wirklich löschen?",
	        buttons: {
                confirm: {
                    label: 'Ja',
                    className: 'btn-primary'
                },
                cancel: {
                    label: 'Abbrechen',
                },
             },
            callback: function(result) {
                if (result) {
                    $.post("/MDI/manage_admin_delete_maint",{ "id" : maint_ID }, function(){
                        $.post("/MDI/manage_admin_query_maint", function(data){
                            $("#area-maint-table").html(data);
                        })
                    })
                }
			 }
	    })
		.error(function() { alert("error7"); });
	});

	$('#area-maint-table').on('click', 'tr', function(){
		var row = $(this);
		/* Mark as selected if the row is not a detail row */
		if(row.hasClass('isMaintTableRow')) {
			var bk = $(this).css("background-color");
			if(bk == "rgb(249, 251, 162)") {
				$(this).css("background-color", "#FFFFFF");
				$('#button-delete-maint').attr("disabled", true);
			}
			else {
				$(this).css("background-color", "#F9FBA2");
				$(this).siblings().css("background-color", "#FFFFFF");
				$('#button-delete-maint').attr("disabled", false);

				maint_ID = $(this)[0].cells[0].innerText;
				selected_row_maint = row;
			}
		}
	});
// =====================================================================================================================
//	=========================================== select change ==========================================================
//  ====================================================================================================================
//  machine
    $.post("/MDI/select_machine_events", { 'changed': 2 }, function(data){ //
        $("#div_machine_list0").html(data);
	});
	//  main assem
	$.post("/MDI/select_main_assem_events", { "changed": 0 }, function(data){ //
        $("#div_main_assem_list0").html(data);
	});

	$("#div_machine_list0").on("change", function() {
	    $.post("/MDI/select_main_assem_events", { "selected_machine": $('#div_machine_list0').children().eq(0).val(), "changed": 2 }, function(data){ //
            $("#div_main_assem_list0").html(data);
            $.post("/MDI/select_sub_assem_events", { 'selected_main_assem': $('#div_main_assem_list0').children().eq(0).val(), 'changed': 2 }, function(data){ //
                $("#div_sub_assem_list0").html(data);
                $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list0').children().eq(0).val(), 'changed': 2 }, function(data){ //
                    $("#div_component_list0").html(data);
                });
            });
        });
	});
	//  sub assem
	$.post("/MDI/select_sub_assem_events", { 'changed': 0 }, function(data){ //
        $("#div_sub_assem_list0").html(data);
	});

	$("#div_main_assem_list0").on("change", function() {
        $.post("/MDI/select_sub_assem_events", { 'selected_main_assem': $('#div_main_assem_list0').children().eq(0).val(), 'changed': 2 }, function(data){ //
            $("#div_sub_assem_list0").html(data);
            $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list0').children().eq(0).val(), 'changed': 2 }, function(data){ //
                $("#div_component_list0").html(data);
            });
        });
	})

//   component
	$.post("/MDI/select_component_events", { 'changed': 0 }, function(data){ //
        $("#div_component_list0").html(data);
	});

	$('#div_sub_assem_list0').on('change', function() {
	    $.post("/MDI/select_component_events", { 'selected_sub_assem': $('#div_sub_assem_list0').children().eq(0).val(), 'changed': 2 }, function(data){ //
            $("#div_component_list0").html(data);
        });
	});
})