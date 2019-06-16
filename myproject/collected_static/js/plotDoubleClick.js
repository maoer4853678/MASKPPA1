    myChart.on('dblclick', function (params) {
//     TODO: integrate to all plot functions
        if ($('#page_id').val() == 1) {
            $.post("/MDI/plotTraceLine",{
                "dataaxis":params.name,
                "data":params.value,
                "filter": 1,
                'machine': $('#div_machine_list').children().eq(0).val(),
                'main_assem': $('#div_main_assem_list').children().eq(0).val(),
                'sub_assem': $('#div_sub_assem_list').children().eq(0).val(),
                'component': $('#div_component_list').children().eq(0).val()
            },  function(data) {
                $("#TraceLine_Hide").html(data);
            })
            .error(function() {alert("error124"); });
            $('#item_id').val(params.name);
            $('#asdasd').show();
        };
    });