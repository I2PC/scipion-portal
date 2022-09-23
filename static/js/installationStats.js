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

function sortDict(dict){

    let keys = Object.keys(dict); // or loop over the object to get the array
    // keys will be in any order
    keys.sort(); // maybe use custom sort, to change direction use .reverse()
    // keys now will be in wanted order

    sorted = {}
    for (var i=0; i<keys.length; i++) { // now lets iterate in sort order
        var key = keys[i];
        var value = dict[key];
        sorted[key] = value
    }
    return sorted
}
function addDateRange(start, end, data){

    let current = new Date(start); // date for the loop

    do {
        let category = current.getFullYear() + "-" + (current.getMonth()+1).toString().padStart(2,"0")
        if (data[category] === undefined) {
            data[category] = 1
        }else{
            data[category] = data[category] + 1
        }

        // Increment by 1 month
        current.setMonth(current.getMonth() +1)

    } while (current < end)


}
function data2ProjectOverTime(chartOptions,data){

    /* Data comes like :
    [
        {"client_country": "Spain", "date": "2017-04-12T08:47:26.801Z", "timesModified": 1, "lastModificationDate": "2017-04-12T08:47:27.093Z", "prot_count": 0}
        ...
    ]
    We need to get categories: categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    And series:
        [7.0, 6.9, 9.5, 14.5, 18.4, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
    */

    series = {}
    data.forEach(function (workflow){
        addDateRange(new Date(workflow.date), new Date(workflow.lastModificationDate), series)
    });

    series = sortDict(series)

    chartOptions.xAxis = {
        categories: Object.keys(series)
    };

    chartOptions.series = [{
                    name: 'Active projects per month',
                    data: Object.values(series)
                }];

};


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
