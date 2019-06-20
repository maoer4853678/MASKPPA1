function plotHistoChart(myChart, grida, inputType = 0) {
    var dataCount = 12;
    var data1 = []; data2 = []; data3 = [];
    var dataAxis = (function (){
                var res = [];
                var len = dataCount;
                while (len--) {
                    res.push(dataCount - len - 1);
                }
                return res;
            })();

    for (var i = 1; i<=dataCount; i ++) {
        data1.push(Math.round(Math.random()*20) + 80)
        data2.push(0)
        data3.push(0)
    };

    if ( inputType == 0 ) {
        data2[6]=56; data1[6]=0
        data2[8]=52; data1[8]=18
    }
    else if ( inputType == 1 ) {
        data3[6]=56; data1[6]=0
        data3[8]=52; data1[8]=0
    }
    else {
        data1[6]=56; data2[6]=12; data3[6]=8
        data1[8]=52; data2[8]=18; data3[6]=22
    }

    option = {
        tooltip: {
            formatter: '{c}%'
        },
        legend: {
            data: ['指标完成', '指标未完成', '指标待完成'],
            itemWidth: 20,
            icon: "rect"
        },
        title: [
            {
                text: '生产状态',
                textStyle: {
                    fontSize: 14,
                    fontWeight: 'normal'
                }
            },
            {
                text: 'More>>',
                left: 'right',
                textStyle: {
                    color: '#23527c',
                    fontSize: 14,
                    fontWeight: 'normal'
                },
                link: '#',
                target: 'self'
            }
        ],
        grid: [
            {
                left: '5%',
                right: '5%',
                top: 28,
                bottom: '0%',
                containLabel: true,
                show: true
            }
        ],
        xAxis: {
            data: dataAxis,
            axisTick: {
                show: false
            },
            axisLine: {
                show: false
            },
            z: 10
        },
        yAxis: {
            name: '计划完成度',
            nameLocation: 'middle',
            nameGap: 30,
            axisLine: {
                show: false
            },
            axisTick: {
                show: false
            },
            axisLabel: {
                textStyle: {
                    color: '#999'
                }
            }
        },
        series: [
            {
                type: 'bar',
                stack:'all',
                name: '指标完成',
                data: data1,
                itemStyle: {
                    normal: {
                        color: '#00ba38'
                    }
                },
            },
            {
                type: 'bar',
                stack:'all',
                name: '指标待完成',
                data: data2,
                itemStyle: {
                    normal: {
                        color: '#ba0000'
                    }
                },
            },
            {
                type: 'bar',
                stack:'all',
                name: '指标未完成',
                data: data3,
                itemStyle: {
                    normal: {
                        color: '#edc309'
                    }
                },
            }
        ]
    };

    if(grida == 0) {
        option.grid = [
            {
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
                containLabel: false,
                show: true
            }
        ]
        option.legend = {show: false}
        option.title = {show: false}
    }
    myChart.setOption(option);
}