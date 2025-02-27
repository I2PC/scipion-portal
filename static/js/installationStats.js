function getDataAndDrawCharts(){
    // From: http://scipion.i2pc.es/report_protocols/api/workflow/workflow/full/?
    var scipionUsageDataURL = "api/v2/installations/";
    var filter = "?limit=0";

    if (window.location.search != ""){
        filter = window.location.search;
    };

    scipionUsageDataURL = scipionUsageDataURL + filter;

    $.getJSON( scipionUsageDataURL).done(function( response ) {

        drawCharts(response.objects)

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete" );
    });
};

function drawCharts(data){
    let aggregatedData = {}
    aggregateAll(data, aggregatedData)

    drawInstallationsByCountry(aggregatedData.client_country, data.length)
    drawInstallationsByCity(aggregatedData.client_city, data.length)
    drawInstallationsOverTime(data)

}


const _MS_PER_DAY = 1000 * 60 * 60 * 24;
const _MS_PER_WEEK = _MS_PER_DAY *7;

// a and b are javascript Date objects
function dateDiffInDays(start, end) {

  return dateDiff(start, end, _MS_PER_DAY)
}

function dateDiffInWeeks(start, end) {

  return dateDiff(start, end, _MS_PER_WEEK)
}

function  dateDiff(start, end, msPerGroup){
  return Math.ceil((end - start) / msPerGroup);
}

function drawInstallationsByCountry(aggData, total) {
    const data = propertyAggregationToPieChartData(
        aggData, 'Installations count');

    loadBarChart('installationsByCountry', 'Number of installations per country (' + total + ')', data, installationsByCountryTweaker);

}

function drawInstallationsByCity(aggData, total) {
    const data = propertyAggregationToPieChartData(
        aggData, 'Installations count');

    loadBarChart('installationsByCity', 'Number of installations per city (' + total + ')', data, installationsByCountryTweaker);

}


function installationsByCountryTweaker(options){
    options.tooltip.pointFormat = '<b>{point.y}</b> installations.';
    options.chart.zoomType='xy';
    options.yAxis ={title:{text:"Number of installations"}}
    options.plotOptions.series.events = {
        click: function (event) {
            window.location.href = window.location.href + "?limit=0&client_country=" + event.point.name
        }
    }
    options.subtitle = {text: "Zoomable!"}

}
function drawInstallationsOverTime(data){
    // Prepares the data and draws the evolution of projects over time

    chartOptions = {
        chart: {
            type: 'line'
        },
        title: {
            text: 'Installations creation'
        },
        subtitle: {
            text: 'Months when installations where first seen'
        },
        xAxis: {
        },
        yAxis: {
            title: {
                text: 'Number of installations'
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: false
            }
        },
    };

    data2InstallationOverTime(chartOptions, data)

    Highcharts.chart('installationsOvertime', chartOptions);

}
function data2InstallationOverTime(chartOptions,data){

    /* Data comes like :
    [
        {"client_country": "Spain", "date": "2017-04-12T08:47:26.801Z", "timesModified": 1, "lastModificationDate": "2017-04-12T08:47:27.093Z", "prot_count": 0}
        ...
    ]
    We need to get categories: categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    And series:
        [7, 6, 9, 14, 18, 21, 25, 26, 23, 11, 13, 9]
    */

    series = {}
    data.forEach(function (installation){
        addDateRange(new Date(installation.creation_date), undefined, series)
    });

    series = sortDict(series)

    chartOptions.xAxis = {
        categories: Object.keys(series)
    };

    chartOptions.series = [{
                    name: 'Installations creation',
                    data: Object.values(series)
                }];

};


$(window).ready(function(){
    getDataAndDrawCharts();
});
