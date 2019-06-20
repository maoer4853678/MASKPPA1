$(document).ready(function(){
	$(".nav.navbar-nav > li").removeClass("active");
	$('#machine_global').addClass("active");

	var myChart_wmp_gb_1 = echarts.init(document.getElementById("plot_fc_wmap_1"))
	plotWorldMap(myChart_wmp_gb_1)
	myChart_wmp_gb_1.setOption({title: {text: "全球工厂概况"}})

});

