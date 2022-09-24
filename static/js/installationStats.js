function getDataAndDrawCharts(){
    // From: http://scipion.i2pc.es/report_protocols/api/workflow/workflow/full/?
    var scipionUsageDataURL = "api/v2/installations/";
    var filter = "?limit=0"; //"?project_workflow__gt=[]";

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

$(window).ready(function(){
    getDataAndDrawCharts();
});
