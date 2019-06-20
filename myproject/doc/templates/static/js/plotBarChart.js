function plotBarChart(myChart, type) {
    var data1 = [];
    var data2 = [];
    var data3 = [];

    if ( type == 'wp_1' ) {
        var dataCount = 15;
        var dataAxis = ['G1.1','G1.2','G1.3','G1.4','G1.5','G1.6','G1.7','G2.1','G2.2','G2.3','G2.4','G3.1','G3.2','G3.3','G3.4']
        var dataTitle = '数控程序表'
    } else if ( type == 'wp_2' ) {
        var dataCount = 20;
        var dataAxis = ['T1.1','T1.2','T1.3','T1.4','T1.5','T1.6','T1.7','T1.8','T1.9','T1.10','T2.1','T2.2','T2.3','T2.4','T3.1','T3.2','T3.3','T3.4','T3.5','T3.6']
        var dataTitle = '刀具使用表'
    } else {
        var dataCount = 12;
        var dataAxis = ['默认1','默认2','默认3','默认4','默认5','默认6','默认7','默认8','默认9','默认10','默认11','默认12']
        var dataTitle = '默认表'
    }

    for (var i = 0; i<dataCount; i ++) {
        data1.push(Math.round(Math.random()*60))
        data2.push(0)
        data3.push(Math.round(Math.random()*30))
    };

    if ( type == 'wp_1' ) {
        data2[7]=data1[7]
        data1[7]=0
    } else if ( type == 'wp_2' ) {
        data1[9]+=100;
        data2[6]=56;
        data1[6]=0;
    }


    option = {
        tooltip: {
            formatter: '{c} min'
        },
        legend: {
            data: ['正常工序','异常振动'],
            itemWidth: 20,
            icon: "rect"
        },
        title: [
            {
                text: dataTitle,
                textStyle: {
                    fontSize: 14,
                    fontWeight: 'bold'
                },
                padding: 3
            },
            {
                text: 'More>>',
                left: 'right',
                textStyle: {
                    color: '#23527c',
                    fontSize: 14,
                    fontWeight: 'normal',
                    fontFamily: 'Arial'
                },
                link: '#',
                target: 'self',
                padding: 3
            }
        ],
        grid: [
            {
                left: 56,
                right: 40,
                top: 28,
                bottom: 20,
                containLabel: false,
                show: true
            }
        ],
        xAxis: {
            name: '工序',
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
            name: '切削时间',
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
                data: data1,
                name: '正常工序',
                itemStyle: {
                    normal: {
                        color: '#00ba38',
                    }
                },
            },
            {
                name:"异常振动",
                type: 'bar',
                stack:'all',
                data: data2,
                itemStyle: {
                    normal: {
                        color: '#c23531',
                    }
                },
            },
            {
                type: 'bar',
                stack:'all',
                data: data3,
                itemStyle: {
                    normal: {
                        color: '#afafaf',
                    }
                },
            }
        ]
    };
    myChart.setOption(option);
}