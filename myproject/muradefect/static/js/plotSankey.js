myChart.showLoading();
myChart.hideLoading();

myChart.setOption(option = {
    title: {
        text: 'Sankey Diagram'
    },
    tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'

    },
    series: [
        {
            type: 'sankey',
            layout:'none',
            data: [{
                name: 'n1'
            }, {
                name: 'n2'
            }, {
                name: 'n3'
            }],
            links: [{
                source: 'n1',
                target: 'n2',
                value: 3
            }, {
                source: 'n1',
                target: 'n3',
                value: 4
            }],
            itemStyle: {
                normal: {
                    borderWidth: 1,
                    borderColor: '#aaa'
                }
            },
            lineStyle: {
                normal: {
                    curveness: 0.5
                }
            }
        }
    ]
});
