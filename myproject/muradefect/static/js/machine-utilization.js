$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active");
	$('#machine_utilization').addClass("active");
	$('#page_id').val(4);
    // plot utility of day =============================================================================================
    rtrn_day = [1,1]// timeAnchor(day_now, "day")
    var mychart_ut_pi_1 = echarts.init(document.getElementById("pieplot_day"))
    var mychart_ut_pi_2 = echarts.init(document.getElementById("pieplot_morning"))
    var mychart_ut_pi_3 = echarts.init(document.getElementById("pieplot_noon"))
    var mychart_ut_pi_4 = echarts.init(document.getElementById("pieplot_evening"))
	$.post("/MDI/machine_utility_day", {"st": rtrn_day[0], "et": rtrn_day[1]}, function(response){
	    plotUti("histoplot_day", response[0], response[2]);
		plotPie(mychart_ut_pi_1, response[1][0],"全天");
		plotPie(mychart_ut_pi_2, response[1][1],"早班");
		plotPie(mychart_ut_pi_3, response[1][2],"午班");
		plotPie(mychart_ut_pi_4, response[1][3],"晚班");
	})
	.error(function() { alert("day utility failed"); });
	// plot status of the machine  =====================================================================================
	myChart_fc_st_1 = echarts.init(document.getElementById("plot_utl_status_1"))
	plotStatus(myChart_fc_st_1, 20, "实施运行数据");

	var myChart2 = echarts.init(document.getElementById("plotNo-02"));
	var myChart4 = echarts.init(document.getElementById("plotNo-04"));
    var i=0;
	$.post("/MDI/machine_numeric_select", {"index": i}, function(response){
		plotNumeric(myChart4, response, '#ba0000');
	})

	$.post("/MDI/queryLinearPosition", function(response) {
	    plotNumeric(myChart2, response, '#4286f4');
    })

	setInterval(function (){
        $.post("/MDI/machine_numeric_select", function(response){
            plotNumeric(myChart4, response, '#ba0000');
        })

        $.post("/MDI/queryLinearPosition", function(response) {
            plotNumeric(myChart2, response, '#4286f4');
        })
    }, 1000);



    var myChart0 = echarts.init(document.getElementById("plotGauge-01"));
	var myChart5 = echarts.init(document.getElementById("plotGauge-02"));
	var myChart6 = echarts.init(document.getElementById("plotGauge-03"));
	var myChart7 = echarts.init(document.getElementById("plotGauge-04"));
	var myChart8 = echarts.init(document.getElementById("plotGauge-05"));
	var myChart9 = echarts.init(document.getElementById("plotGauge-06"));
	plotGauge(myChart0, "主轴状态");
	plotGauge(myChart5, "导轨状态");
	plotGauge(myChart6, "电机状态");
	plotGauge(myChart7, "加工完成度");
	plotGauge(myChart8, "切削稳定性");
	plotGauge(myChart9, "产线负荷");
});

