$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active");
	$('#machine_data_analysis').addClass("active");
	$('#page_id').val(4);

	var day_now = "2017-03-15 00:00:00"
	var month_now = day_now
	var year_now = day_now
	var myChart_fc_pi_1 = echarts.init(document.getElementById("pieplot_day1"))
	var myChart_fc_pi_2 = echarts.init(document.getElementById("pieplot_day2"))
	var myChart_fc_pi_3 = echarts.init(document.getElementById("pieplot_day3"))
	var myChart_fc_pi_4 = echarts.init(document.getElementById("pieplot_day4"))
	var myChart_fc_pi_5 = echarts.init(document.getElementById("pieplot_day5"))
	var myChart_fc_pi_6 = echarts.init(document.getElementById("pieplot_day6"))
	// plot utility of day =================================================================================================
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
		plotPie(myChart_fc_pi_1); plotPie(myChart_fc_pi_2); plotPie(myChart_fc_pi_3)
		plotPie(myChart_fc_pi_4); plotPie(myChart_fc_pi_5); plotPie(myChart_fc_pi_6)
	})
	.error(function() { alert("day utility failed"); });
// plot utility of month ===============================================================================================
    var rtrn_month = [1,1]// timeAnchor(month_now, 'month')
    $.post("/MDI/machine_utility_month", {"st": rtrn_month[0], "et": rtrn_month[1]}, function(response){
		plotUti("histoplot_month", response, response[5]);
	})
	.error(function() { alert("Month utility failed"); });
// plot utility of year ================================================================================================
    var rtrn_year = [1,1]// timeAnchor(month_now, 'year')
	$.post("/MDI/machine_utility_year", {"st": rtrn_year[0], "et": rtrn_year[1]}, function(response){
		plotUti("histoplot_year", response, "Year: 2017");
	})
	.error(function() { alert("Year utility failed"); });
//======================================================================================================================
    myChart_st_fc_1 = echarts.init(document.getElementById("plot_line_status1"))
    myChart_st_fc_2 = echarts.init(document.getElementById("plot_line_status2"))
    myChart_st_fc_3 = echarts.init(document.getElementById("plot_line_status3"))
    myChart_st_fc_4 = echarts.init(document.getElementById("plot_line_status4"))
    myChart_st_fc_5 = echarts.init(document.getElementById("plot_line_status5"))
    myChart_st_fc_6 = echarts.init(document.getElementById("plot_line_status6"))

	plotStatus(myChart_st_fc_1, 1, 0)
	plotStatus(myChart_st_fc_2, 1, 0)
	plotStatus(myChart_st_fc_3, 1, 0)
	plotStatus(myChart_st_fc_4, 1, 0)
	plotStatus(myChart_st_fc_5, 1, 0)
	plotStatus(myChart_st_fc_6, 1, 0)
//======================================================================================================================
    var chartHisto01 = echarts.init(document.getElementById("chartHisto-01"))
    var chartHisto02 = echarts.init(document.getElementById("histoplot_year1"))
    var chartHisto03 = echarts.init(document.getElementById("histoplot_year2"))
    var chartHisto04 = echarts.init(document.getElementById("histoplot_year3"))
    var chartHisto05 = echarts.init(document.getElementById("histoplot_year4"))
    var chartHisto06 = echarts.init(document.getElementById("histoplot_year5"))
    var chartHisto07 = echarts.init(document.getElementById("histoplot_year6"))

    plotHistoChart(chartHisto01, 1, 3)
//    plotStackChart(chartHisto01)
    plotHistoChart(chartHisto02, 0, 0)
    plotHistoChart(chartHisto03, 0, 0)
    plotHistoChart(chartHisto04, 0, 0)
    plotHistoChart(chartHisto05, 0, 1)
    plotHistoChart(chartHisto06, 0, 1)
    plotHistoChart(chartHisto07, 0, 1)

    $( function() {
        var $winHeight = $( window ).height()
        $( '.container' ).height( $winHeight );
    });
});






