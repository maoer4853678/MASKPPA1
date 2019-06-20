function plotGauge(myChart, title) {
    option = {
        grid: {
            height: '140px',
        },
        series: [
            {
                name: title,
                startAngle: 180,
                endAngle: 0,
                center: ["50%", "65%"],
                type: 'gauge',
                radius: "110%",
                data: [{value: (Math.random() * 100).toFixed(2), name: title}],
                splitNumber: 4,
                splitLine: { show: false },
                axisTick: { show: false },
                axisLabel: { show: false },
                axisLine: {
                    lineStyle: {
                        color: [[0.05, '#ba0000'], [0.2, '#edc309'], [1, '#00ba38']],
                        width: 18
                    }
                },
                title: {
                    show: true,
                    offsetCenter: [0, '55%']
                },
                detail: {
                    formatter:'{value} %',
                    textStyle: {
                        fontSize: 20
                    },
                    offsetCenter: [0, '20%']
                },
                pointer: { width: 4, }
            }
        ]
    };

    myChart.setOption(option);
}