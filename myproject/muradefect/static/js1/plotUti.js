function plotUti(id_div, utiData, title) {
// TODO: Integrate into plotHistoChart
    var myChart = echarts.init(document.getElementById(id_div));
    var len = utiData[0].length;
    if (len == 24)
    {
        var maxy = 1;
    }
    else if (len == 12) {
        var maxy = 744;
    }
    else
    {
        var maxy = 24;
    }

    option = {
        backgroundColor: '#ffffff',
        title: {
            text: title,
            left: "left",
            textBaseline: 'top',
            textStyle: { fontWeight: 'normal', fontSize: 14 },
        },
        tooltip : {
            trigger: 'item',
//            axisPointer : {
//                type : 'shadow'
//            }
        },
        legend: {
            data: [
                {name: 'Cutting', icon: "rect"},
                {name: 'Productive', icon: "rect"},
                {name: 'Standstill', icon: "rect"},
                {name: 'Off', icon: "rect"}
            ],
            left:'right',
            itemWidth: 10
        },
        grid: {
            left: 0,
            right: 0,
            bottom: 18,
            top: 24,
            containLabel: false
        },
        yAxis:  {
            type: 'value',
            show: false,
            max: maxy,
            axisTick: {
                show: false
            },
            axisLine: {
                show: false
            }
        },
        xAxis: {
            type: 'category',
            data: utiData[0],
            show: true
        },
        series: [
            {
                name: 'Cutting',
                type: 'bar',
                stack: 'all',
                label: {
                    normal: {
                        show: false,
                        position: 'insideRight'
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#00ba38'
                    }
                },
                data: utiData[1]
            },
            {
                name: 'Productive',
                type: 'bar',
                stack: 'all',
                label: {
                    normal: {
                        show: false,
                        position: 'insideRight'
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#619CFF'
                    }
                },
                data: utiData[2]
            },
            {
                name: 'Standstill',
                type: 'bar',
                stack: 'all',
                label: {
                    normal: {
                        show: false,
                        position: 'insideRight'
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#edc309'
                    }
                },
                data: utiData[3]
            },
            {
                name: 'Off',
                type: 'bar',
                stack: 'all',
                label: {
                    normal: {
                        show: false,
                        position: 'insideRight'
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#adadad',
                    }
                },
                data: utiData[4]
            }
        ]
    };

    myChart.setOption(option);
}