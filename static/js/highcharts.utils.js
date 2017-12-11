// Aggregate all data in a matrix
function aggregateAll(matrix, aggregatedSet, propertyValue){

    for (var line in matrix){

        aggregateLine(matrix[line], aggregatedSet, propertyValue)

    }
}

// Aggregate a line
function aggregateLine(line, aggregatedSet, propertyValue){

    for (var prop in line) {

        aggregateProperty(prop, line, aggregatedSet, propertyValue)

    }
}

function aggregateProperty(prop, line, aggregatedSet, propertyValue){

    var propertyAggregation = getPropertyAggregation(prop,aggregatedSet) ;

    var value = line[prop];

    value = normalizeValue(value, prop);

    aggregateValue(value, propertyAggregation, line[propertyValue])

}

function normalizeValue(value, property){

    if (isDate(value, property)){
        return normalizeDate(value);
    } else {
        return value;
    }


}

function isDate(value, property){

    return property == "timeStamp"
}
function normalizeDate(date){

    if (typeof(date) == "string") {
        date = new Date(date);
    }

    return removeTimeFromDate(date)

}

function removeTimeFromDate(date){

    return new Date(date.toISOString().slice(0,10));
}

function aggregateValue(attribute, aggregation, value){

    if (value == undefined){
        value = 1;
    };

    aggregation[attribute] = getObjectAttribute(aggregation, attribute,0)+value;

}

function getObjectAttribute(object, attribute, defaultValue){

    if (object[attribute] === undefined){
        object[attribute]= defaultValue;
    }

    return object[attribute];

}
function getPropertyAggregation(prop, aggregatedSet){

    return getObjectAttribute(aggregatedSet, prop, {})
}


function propertyAggregationToPieChartData(propertyAggregation, name, min) {

    var series = [{
        name:name,
        data:[]
    }];

    var total = 0;
    var minPctg = min/100;

    // Calculate the total value
    for (prop in propertyAggregation){
        var value = propertyAggregation[prop];
        total = total + value;
    };

    var minPie = {name:"Others (&lt;" + min + '%)', y:0}
    for (prop in propertyAggregation){

        var value = propertyAggregation[prop];

        if( min !== undefined && value/total < minPctg ) {
            minPie.y = minPie.y + value;

        } else {

            var pie = {
            name: prop,
            y:value

        };

        series[0].data.push(pie);
        }
    }

    // If there is a min
    if (min){
        series[0].data.push(minPie);
    }

    return series;

};

function propertyAggregationToTimeSeries(propertyAggregation, name) {
// Sample chart: http://www.highcharts.com/demo/line-time-series/sand-signika
// Sample data: https://www.highcharts.com/samples/data/jsonp.php?filename=usdeur.json
    var series = [{
        type: 'column',
        name: name,
        data: []
    }];

    var serie = [];

    for (prop in propertyAggregation){

        var date = new Date(prop);
        var dateMilis = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        var point = [
        dateMilis, propertyAggregation[prop]
        ];

        serie.push(point);
    }

    series[0].data = serie;

    return series;

};

function accumulateData(data){

    var previousValue = 0;
    for (var i=0; i<data.length; i++){

        var point = data[i];
        point[1]= parseInt(point[1]) + previousValue;

        previousValue = point[1];
    };

    return data;
};


function loadPieChart(container, title, data){

    // Build the chart
    $(container).highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: title
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.1f}%)'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            }
        },
        series: data
    });
};

function loadAreaChart(container, title, data){

    // Build the chart
    $(container).highcharts({
        chart: {

            zoomType: 'x'
        },
        title: {
            text: title
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Downloads'
            }
        },
        series: data
    });
};

function loadZoomableTimeSeries(container, title, data){

    $(container).highcharts({
        chart: {
            zoomType: 'x'
        },
        title: {
            text: title
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Downloads'
            }
        },
        legend: {
            enabled: false
        },
        series: data
    });
};

function loadStackedColumnChart(container, title, rawData,
                                groupByProperty, seriesProp, valueProp,
                                YAxisLabel){

    // Need to prepare the raw data
    // Find all groups/categories
    var categories = [];

    if (YAxisLabel == undefined){
        YAxisLabel = valueProp
    }

    for (var i=0; i<rawData.length; i++) {
        item = rawData[i];
        var groupValue = item[groupByProperty];

        if (groupValue == ""){
            continue;
        } else if ($.inArray(groupValue, categories) == -1){
            categories.push(groupValue);
        };
    };

    if (categories.length == 0){
        return;
    }

    function addValueToSerie(seriesName, value, categoryName){

        function getSerie(serieName){

            for (var s=0;s<series.length;s++){
                serie = series[s];
                if (serie.name == seriesName) {

                    return serie;
                };
            };

            // no serie found... create one
            emptyData = [].slice.apply(new Uint8Array(categories.length));

            var newSerie = {
                name: serieName,
                data: emptyData
            };

            series.push(newSerie);

            return newSerie;
        };

        function getCategoryIndex(categoryName){
            for (var i=0;i<categories.length;i++){
                if (categories[i] == categoryName) {
                    return i;
                };
            };
        };

        if (value > 0){
            var serie = getSerie(seriesName);

            var categoryIndex = getCategoryIndex(categoryName);

            // Add the value to the category
            serie.data[categoryIndex] = serie.data[categoryIndex] + value;
        };

    };

    // Generate series based on number for categories found
    var series = [];
    for (var i=0; i<rawData.length; i++) {
        item = rawData[i];
        var serieName = item[seriesProp];
        var value = item[valueProp];
        var categoryValue = item[groupByProperty];

        if (categoryValue == ""){
            continue;
        } else {
            addValueToSerie(serieName, value, categoryValue);
        }

    };


    $(container).highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: title
        },
        xAxis: {
            categories: categories
        },
        yAxis: {
            min: 0,
            title: {
                text: YAxisLabel
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'percent',
                dataLabels: {
                    enabled: true,
                    formatter: function(){
                        console.log(this);
                        var val = this.y;
                        if (val < 1) {
                            return '';
                        }
                        return val;
                    },
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                }
            }
        },
        series: series
    });
};