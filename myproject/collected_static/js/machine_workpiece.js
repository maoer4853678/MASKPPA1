$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active")
	$('#manage_demo').addClass("active")

    var mychart_wp_pi_1 = echarts.init(document.getElementById("plot_wp_pie_1"))
	plotPie(mychart_wp_pi_1, [18, 60, 0, 12], "效率KPI")
	var mychart_wp_st_1 = echarts.init(document.getElementById("plot_wp_status_1"))
	plotStatus(mychart_wp_st_1, 20, "机床状态表") // plot status 1

    var mychart_wp_pi_2 = echarts.init(document.getElementById("plot_wp_pie_2"))
	plotPie(mychart_wp_pi_2, [70, 0, 0, 30], "工艺KPI")
	var myChart_wp_hst_1 = echarts.init(document.getElementById("plot_wp_bar_1"))
	plotBarChart(myChart_wp_hst_1, 'wp_1')

	var mychart_wp_pi_3 = echarts.init(document.getElementById("plot_wp_pie_3"))
	plotPie(mychart_wp_pi_3, 0, "刀具KPI")
	var myChart_wp_hst_2 = echarts.init(document.getElementById("plot_wp_bar_2"))
	plotBarChart(myChart_wp_hst_2, 'wp_2');

	var mychart_wp_pi_4 = echarts.init(document.getElementById("plot_wp_pie_4"))
	plotPie(mychart_wp_pi_4, 0, "调度KPI")
	var mychart_wp_st_2 = echarts.init(document.getElementById("plot_wp_status_2"))
	plotStatus(mychart_wp_st_2, 8, "机床调度表"); // plot status 2

	var myChart_wp_pi_5 = echarts.init(document.getElementById("plot_wp_pie_5"))
	plotPie(myChart_wp_pi_5, 0, "主轴KPI")

    var chart_wp_fft_1 = echarts.init(document.getElementById("plot_wp_fft_1"))
    var chart_wp_fft_2 = echarts.init(document.getElementById("plot_wp_fft_2"))

	$.post("/MDI/queryFFT", function(response){
        plotFFT(chart_wp_fft_1, response)
	})

	$.post("/MDI/queryRMS", function(response) {
	    plotNumeric(chart_wp_fft_2, response, '#ba0000')
	});

    setInterval(function () {
        $.post("/MDI/queryFFT", function(response){
            plotFFT(chart_wp_fft_1, response)
        })

        $.post("/MDI/queryRMS", function(response) {
            plotNumeric(chart_wp_fft_2, response, '#ba0000')
        })
    }, 1000)

	$('#page_id').val(3)
});