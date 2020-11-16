// Aggregate all data in a matrix
function aggregateAll(matrix, aggregatedSet, propertyValue){

    for (let line in matrix){

        aggregateLine(matrix[line], aggregatedSet, propertyValue)

    }
}


function aggregateLine(line, aggregatedSet, propertyValue){
/*
    Line --> {city: "Madrid", type: "soft"}
    aggregatedSet --> {city:{Madrid: 1}, type:{soft:1}
 */
    for (let prop in line) {

        aggregateProperty(prop, line, aggregatedSet, propertyValue)

    }
}

function aggregateProperty(prop, line, aggregatedSet, propertyValue){
// Reads a property (prop) from line and adds it's value to the prop series in the aggregated set

    let propertyAggregation = getPropertyAggregation(prop, aggregatedSet);

    let value = line[prop];

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

    return property === "timeStamp"
}
function normalizeDate(date){

    if (typeof(date) == "string") {
        date = new Date(date);
    }

    return removeTimeFromDate(date)

}

function removeTimeFromDate(date){

    return new Date(date).toISOString().slice(0,10);
}

function aggregateValue(attribute, aggregation, value){
// increase the attribute of aggregation by the value

    // default value to 1
    if (value === undefined){
        value = 1;
    }
    aggregation[attribute] = getObjectAttribute(aggregation, attribute,0)+value;

}

function getObjectAttribute(object, attribute, defaultValue){
// returns the attribute of an object if exists, otherwise creates it with defaultValue.
    if (object[attribute] === undefined){
        object[attribute]= defaultValue;
    }

    return object[attribute];

}
function getPropertyAggregation(prop, aggregatedSet){
// returns the property or an empty object.
    return getObjectAttribute(aggregatedSet, prop, {})
}

function objToArray(object){
    // Turns an object {"prop1": value, ...}
    // into ........... [["prop1", value], ...]

    data = []
    for (prop in object){
        data.push([prop, object[prop]])
    }

    return data
}

function propertyAggregationToPieChartData(propertyAggregation, name, min) {

    let value;
    const series = [{
        name: name,
        dataSorting: { enabled: true},
        data: []
    }];

    let total = 0;
    const minPctg = min / 100;

    // Calculate the total value
    for (let prop in propertyAggregation){
        value = propertyAggregation[prop];
        total = total + value;
    }
    const minPie = {name: "Others (&lt;" + min + '%)', y: 0};
    for (let prop2 in propertyAggregation){

        value = propertyAggregation[prop2];

        if( min !== undefined && value/total < minPctg ) {
            minPie.y = minPie.y + value;

        } else {

            const pie = {
                name: prop2,
                y: value

            };

            series[0].data.push(pie);
        }
    }

    // If there is a min
    if (min){
        series[0].data.push(minPie);
    }

    return series;

}
function propertyAggregationToTimeSeries(propertyAggregation, name, type, series) {
// Sample chart: http://www.highcharts.com/demo/line-time-series/sand-signika
// Sample data: https://www.highcharts.com/samples/data/jsonp.php?filename=usdeur.json

    if (series === undefined) {
        series = [];
    }
    const serie = {
        type: type,
        name: name,
        data: []
    };

    for (let prop in propertyAggregation){

        const date = new Date(prop);
        const dateMilis = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
        const point = [
            dateMilis, propertyAggregation[prop]
        ];

        serie.data.push(point);
    }

    series.push(serie);

    return series;

}
function accumulateData(data){

    let previousValue = 0;
    for (let i=0; i<data.length; i++){

        const point = data[i];
        point[1]= parseInt(point[1]) + previousValue;

        previousValue = point[1];
    }
    return data;
}
function createLines(data, seriesNameCallBack, valueCallBack ) {
    /* From a source data (coming from Django) like:
    [
        {attr1: "value1", attr2: 3, ....},
        ...
    ]

    it creates a new set of simple lines like:
    [
        {value1:3},
        ...
    ]
     */
    const lines = [];

    for (let i=0;i<data.length;i++){
        let line = data[i];
        const serieName = seriesNameCallBack(line);
        const value = valueCallBack(line);
        let newLine = {};
        newLine[serieName]= value;
        lines.push(newLine);

    }
    return lines

}

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
}

function loadBarChart(container, title, data, tweakerCallback){

    let options = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'column'
        },
        title: {
            text: title
        },
        xAxis: {
            type: "category"
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.1f}%)'
        },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true,
                    rotation: -45,
                    color: '#000000',
                    align: 'left',
                    format: '{point.y}', // one decimal
                    y: -10, // 10 pixels down from the top
                    x: 0, // 0 pixels
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            }
        },
        series: data
    };

    // If there is a "tweaker" callback
    if (tweakerCallback !== undefined) {
        tweakerCallback(options)
    }
    // Build the bar
    $(container).highcharts(options);
}
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
}
function loadZoomableTimeSeries(container, title, data, dateFormat){

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
        tooltip: {
            xDateFormat: dateFormat
        },
        legend: {
            enabled: true
        },
        series: data
    });
}
function loadStackedColumnChart(container, title, rawData,
                                groupByProperty, seriesProp, valueProp,
                                YAxisLabel){

    // Need to prepare the raw data
    // Find all groups/categories
    const categories = [];

    if (YAxisLabel === undefined){
        YAxisLabel = valueProp
    }

    for (let i=0; i<rawData.length; i++) {
        let item = rawData[i];
        const groupValue = item[groupByProperty];

        if (groupValue === ""){
            continue;
        } else if ($.inArray(groupValue, categories) === -1){
            categories.push(groupValue);
        }
    }
    if (categories.length === 0){
        return;
    }

    function addValueToSerie(seriesName, value, categoryName){

        function getSerie(serieName){

            for (let s=0; s<series.length; s++){
                serie = series[s];
                if (serie.name === seriesName) {

                    return serie;
                }
            }
            // no serie found... create one
            emptyData = [].slice.apply(new Uint8Array(categories.length));

            const newSerie = {
                name: serieName,
                data: emptyData
            };

            series.push(newSerie);

            return newSerie;
        }
        function getCategoryIndex(categoryName){
            for (let i=0; i<categories.length; i++){
                if (categories[i] == categoryName) {
                    return i;
                }
            }
        }
        if (value > 0){
            let serie = getSerie(seriesName);

            const categoryIndex = getCategoryIndex(categoryName);

            // Add the value to the category
            serie.data[categoryIndex] = serie.data[categoryIndex] + value;
        }
    }
    // Generate series based on number for categories found
    let series = [];
    for (let i=0; i<rawData.length; i++) {
        item = rawData[i];
        let serieName = item[seriesProp];
        let value = item[valueProp];
        const categoryValue = item[groupByProperty];

        if (categoryValue == ""){
            continue;
        } else {
            addValueToSerie(serieName, value, categoryValue);
        }

    }
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
                        const val = this.y;
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
}