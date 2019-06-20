function plotPie(myChart, inputData = 0, inputTitle = []){
    if ( inputData == 0 ) {
        var inputData = []
        for (var i=0; i<3; i++) {
            inputData.push(
                Math.round(Math.random() * 33)
            )
        };
        inputData.push(100 - math.sum(inputData))
    }

    option = {
        backgroundColor: "#ffffff",
        title: {
            text: inputTitle,
            textStyle:{
                fontSize:14
            },
        },
        tooltip : { trigger: 'item' },
        series : [
            {
                name: 'Utility',
                type: 'pie',
                radius : ['50%', '80%'],
                center: ['50%', '50%'],
                hoverAnimation: false,
                data:[
                    {value:inputData[0], name:'Cutting', itemStyle: {normal:{color:'#00ba38'}}},
                    {value:inputData[1], name:'Productive', itemStyle: {normal:{color:'#619CFF'}}},
                    {value:inputData[2], name:'Standstill', itemStyle: {normal:{color:'#edc309'}}},
                    {value:inputData[3], name:'Off', itemStyle: {normal:{color:'#adadad'}}},
                ],
                label: {
                    normal: {
                        show: false,
                        position: 'inside'
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                tooltip : { formatter: "{a} <br/>{b} : {c} ({d}%)"  },
            }, {
                name: 'Cutting',
                type: 'pie',
                radius : ['30%', '30%'],
                hoverAnimation: false,
                label: {
                    normal: {
                        show: 'true',
                        position: 'center',
                        textStyle: {
                            fontSize: 18
                        }
                    }
                },
                data:[
                    {value:0, name: Math.round(inputData[0]/math.sum(inputData)*100) + '%', itemStyle: {normal:{color:'#00ba38'}}},
                ],
                label: {
                    normal: {
                        show: true,
                        position: 'center',
                        textStyle: {
                            fontSize: 18,
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                tooltip : { formatter: "{a}: {b}"  }
            }
        ]
    };

    myChart.setOption(option);
}