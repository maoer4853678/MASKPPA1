function plotBubble(input_1, input_2, input_3, name,  id_div) {
    var myChart = echarts.init(document.getElementById(id_div));
    var a1 = input_1;
    var a2 = input_2;
    if (input_3 == 1) {
        a3 = [['2017-05-08 13:12', 0]]
    } else if (input_3 == 2){
        a3 = [
            ['2017-05-08 13:12', 0],
            ['2017-06-08 13:12', 0],
            ['2017-08-08 13:12', 0]
        ]
    }else {
        a3 = input_3
    };


    option = {
        title:{text: 'Failure Component&Machine Data',x: 'left'},
        grid: [
            {x: '7%', y: '13%', width: '89%', height: '75%'}
        ],
//        tooltip: {
//            trigger: 'axis',
//            position: function (pt) {
//                return [pt[0], '0%'];
//            }
//        },
        legend: {
            right: 10,
            data: ['Failure', 'Run_Time', 'Predict_failure']
        },
        xAxis: {
            type: 'time',
            splitLine: false
        },
        yAxis: {
            type: 'value',
            show: false,
            min: -5,
            max: 15
        },
        dataZoom: [
            {
                type: 'inside'
            }
        ],
        series: [{
            name: 'Run_Time',
            data: a2,
            type: 'scatter',
            symbolSize: 35,
            label: {
                emphasis: {
                    show: true,
                    formatter: function (param) {
    //                    return param.data[1];
                        return 'tool ' + name[1];
                    },
                    position: 'top'
                }
            },
            itemStyle: {
                normal: {
                    color: '#55ced6'
                }
            }
        },
        {
            name: 'Failure',
            data: a1,
            type: 'scatter',
            symbolSize: 40,
            label: {
                emphasis: {
                    show: true,
                    formatter: function (param) {
    //                    return param.data[1];
                        return name[0];

                    },
                    position: 'top'
                }
            },
            itemStyle: {
                normal: {
//                    shadowBlur: 10,
//                    shadowColor: 'rgba(25, 100, 150, 0.5)',
//                    shadowOffsetY: 5,
                    color: '#f47d42'
                }
            }
        },
        {
            name: 'Predict_failure',
            data: a3,
            type: 'scatter',
            symbolSize: 30,
            label: {
                emphasis: {
                    show: true,
                    formatter: function (param) {
    //                    return param.data[1];
                        return 'failure: ' + param.data[0];

                    },
                    position: 'top'
                }
            },
            itemStyle: {
                normal: {
//                    shadowBlur: 10,
//                    shadowColor: 'rgba(25, 100, 150, 0.5)',
//                    shadowOffsetY: 5,
                    color: '#b2b5ba'
                }
            }
        }]
    };

    myChart.setOption(option);
}