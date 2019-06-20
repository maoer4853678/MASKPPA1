function plotWorldMap(myChart){
//    var myChart = echarts.init(document.getElementById(id_div));
    var latlong = {};
    latlong.CN1 = {'latitude':35, 'longitude':105};
    latlong.CN2 = {'latitude':30, 'longitude':115};
    latlong.DE = {'latitude':51, 'longitude':9};
    latlong.US = {'latitude':38, 'longitude':-97}

    var mapData = [
    {'code':'CN1' , 'name':'中国西安机床工厂', 'value':1800, 'color':'#eea638'},
    {'code':'CN2' , 'name':'西门子宜兴工厂', 'value':4600, 'color':'#00ba38'},
    {'code':'DE' , 'name':'德国柏林轴承厂', 'value':2200, 'color':'#d8854f'},
    {'code':'US' , 'name':'美国奥兰多总装厂', 'value':1200, 'color':'#a7a737'}
    ]

    var max = -Infinity;
    var min = Infinity;
    mapData.forEach(function (itemOpt) {
        if (itemOpt.value > max) {
            max = itemOpt.value;
        }
        if (itemOpt.value < min) {
            min = itemOpt.value;
        }
    });

    option = {
        title : {
            left: 'left',
            top: 'top',
            textStyle: {
                color: '#000000',
                fontSize: 14,
                fontWeight: 'normal'
            },
            padding: 10
        },
        tooltip : {
            trigger: 'item',
            formatter : function (params) {
                return params.name;
            }
        },
        visualMap: {
            show: false,
            min: 0,
            max: max,
            inRange: {
                symbolSize: [6, 60]
            }
        },
        geo: {
            name: 'Global Factories Status',
            type: 'map',
            map: 'world',
            roam: true,
            zoom: 1.2,
            label: {
                emphasis: {
                    show: false
                }
            },
            itemStyle: {
                normal: {
                    areaColor: '#afafaf',
                    borderColor: '#fff'
                },
                emphasis: {
                    areaColor: '#008c95' //'#2a333d'
                }
            }
        },
        series : [
            {
                type: 'scatter',
                coordinateSystem: 'geo',
                data: mapData.map(function (itemOpt) {
                    return {
                        name: itemOpt.name,
                        value: [
                            latlong[itemOpt.code].longitude,
                            latlong[itemOpt.code].latitude,
                            itemOpt.value
                        ],
                        label: {
                            emphasis: {
                                position: 'right',
                                show: true
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: itemOpt.color
                            }
                        }
                    };
                })
            }
        ]
    };
    myChart.setOption(option);
    myChart.on('dblclick', function (params) {
        if (params.name == '西门子宜兴工厂') {
            window.location.href='/MDI/machine_unity3D'
        }
//        console.log(params.name)
    });
}