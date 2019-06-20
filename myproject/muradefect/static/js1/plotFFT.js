function plotFFT(myChart, input_data){
//    myChart = echarts.init(document.getElementById(id_div))
    data = []
    for (i=0; i<256; i++) {
        data.push([i, input_data[i]])
    }
    data.shift();

    option = {
        title: {
            show: false
        },
        tooltip: {
            trigger: 'item',
            formatter: '{c}'
        },
        legend: {
            show: false
        },
        grid: [
            {
                left: '5%',
                right: '5%',
                top: '5%',
                bottom: '0%',
                containLabel: true,
                show: true
            }
        ],
        xAxis: [
            {
                type: 'value',
                boundaryGap: false,
//                nameGap: 36,
                max: 'dataMax',
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                }
            }
        ],
        yAxis: [
            {
                name: '振动响应',
                nameLocation: 'middle',
                nameGap: 30,
                type: 'log',
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                }
            }
        ],
        series: [
            {
                type: 'line',
                symbolSize: 0,
                lineStyle:{
                    normal:{
                        width:1
                    },
                },
                data: data
            }
        ],
        animation: false
    };

    myChart.setOption(option)
}