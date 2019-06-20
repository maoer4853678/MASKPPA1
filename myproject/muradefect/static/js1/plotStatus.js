function plotStatus(myChart, dataCount, title){
    var data = [];
    var startTime = +new Date();
    var categories = ['机床状态'];
    var types = [
        {name: '切削', color: '#00ba38'},
        {name: '生产', color: '#619cff'},
        {name: '待机', color: '#edc309'},
        {name: '停机', color: '#afafaf'}
    ];

    if ( title == 0 ) {
        dataCount = Math.round(Math.random()*5+10)
        var dataTitle = { show: false }
        var dataGrid = [
            {
                left: '0%',
                right: '0%',
                top: '0%',
                bottom: '0%',
                containLabel: false,
                show: true
            }
        ];
    }
    else {
        var dataTitle = [
            {
                text: title,
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
        ]
        var dataGrid = [
            {
                left: 0,
                right: '5%',
                top: 20,
                bottom: 0,
                containLabel: true,
                show: true
            }
        ];
    }

    // Generate mock data
    echarts.util.each(categories, function (category, index) {
        var baseTime = startTime;
        for (var i = 0; i < dataCount; i++) {
            var typeItem = types[Math.round(Math.random() * (types.length - 1))];
            var duration = Math.round(Math.random() * 200);
            data.push({
                name: typeItem.name,
                value: [
                    index,
                    baseTime,
                    baseTime += duration,
                    duration
                ],
                itemStyle: {
                    normal: {
                        color: typeItem.color
                    }
                }
            });
            baseTime += Math.round(Math.random() * 1);
        }
    });

    function renderItem(params, api) {
        var categoryIndex = api.value(0);
        var start = api.coord([api.value(1), categoryIndex]);
        var end = api.coord([api.value(2), categoryIndex]);
        var height = api.size([0, 1])[1] * 0.8;

        return {
            type: 'rect',
            shape: echarts.graphic.clipRectByRect({
                x: start[0],
                y: start[1] - height / 2,
                width: end[0] - start[0],
                height: height
            }, {
                x: params.coordSys.x,
                y: params.coordSys.y,
                width: params.coordSys.width,
                height: params.coordSys.height
            }),
            style: api.style()
        };
    }


    option = {
        tooltip: {
            formatter: function (params) {
                return params.marker + params.name + ': ' + params.value[3] + 'min';
            }
        },
        title: dataTitle,
        grid: dataGrid,
        xAxis: {
            show: true,
            min: startTime,
            scale: true,
            axisLabel: {
                formatter: function (val) {
                    return Math.max(0, val - startTime) + 'min';
                }
            },
            axisLine: {
                show: false
            },
            axisTick: {
                show: false
            },
            z: 10
        },
        yAxis: {
            data: categories,
            name: "机床状态",
            nameGap: 24,
            nameLocation: 'middle',
            show: true,
            axisLine: {
                show: false
            },
            axisLabel: {
                show: false
            },
            axisTick: {
                show: false
            }
        },
        series: [{
            type: 'custom',
            renderItem: renderItem,
            itemStyle: {
                normal: {
                    opacity: 1
                }
            },
            encode: {
                x: [1, 2],
                y: 0
            },
            data: data
        }]
    };
    myChart.setOption(option)
}