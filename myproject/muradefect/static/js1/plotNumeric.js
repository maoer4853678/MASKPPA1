function plotNumeric(myChart, input_data, color) {
    option = {
        animation: false,
        backgroundColor: "#ffffff",
        grid: [
            {
                left: '4%',
                right: '10%',
                top: '6%',
                bottom: 20,
                containLabel: false,
                show: true
            }
        ],
        xAxis: [
            {
                type: 'time',
                boundaryGap: false,
                name: 'Time',
                nameLocation: 'middle',
                nameGap: 36,
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
                type: 'value',
                position: 'right',
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
                name: 'Spindle Speed',
                type:'line',
                showSymbol: false,
                data:input_data,
                lineStyle: {
                    normal: {
                        color: color,
                        width: 1
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
}