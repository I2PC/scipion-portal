function getDataAndDrawCharts(){
    // From: http://scipion.i2pc.es/report_protocols/api/workflow/workflow/full/?
    var scipionUsageDataURL = "/report_protocols/api/workflow/workflow/full/";
    var filter = "?project_workflow__gt=[]";

    if (window.location.search != ""){
        filter = window.location.search;
    };

    scipionUsageDataURL = scipionUsageDataURL + filter;

    $.getJSON( scipionUsageDataURL).done(function( data ) {

        drawCharts(data)

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

    drawProjByCountry(aggregatedData.client_country)
    drawProjByProtCount(aggregatedData.prot_count)
    drawProjOverTime(data)
    drawProjLength(data)
}

function drawProjLength(data){
    let yInterval= 500

    let chartOptions = {
          chart: {
            type: 'column',
            zoomType:'xy'
          },
          title: {
            text: 'Project by duration'
          },
          subtitle: {
            text: 'in days, zoomed by default'
          },
          xAxis:{
              zoomable : true,
              title: {
                  text: 'Days'
              }
          },
          yAxis: {
            min: 0,
            title: {
              text: 'Number of projects'
            },
            tickInterval: yInterval
          },
          tooltip: {
              pointFormat: "{point.y} projects {point.x} old",
          },
          plotOptions: {
            column: {
              pointPadding: 0,
              borderWidth: 0,
              groupPadding: 0,
              shadow: false
            }
          }
    };

    fillProjLengthData(chartOptions, data)

    // Break Y axis
    let from =  chartOptions.series[0].data[2];
    let to = chartOptions.series[0].data[1];
    from = Math.ceil(from/yInterval)* yInterval + 200
    to = Math.floor(to/yInterval)* yInterval
    chartOptions.yAxis.breaks=[{
          from: from,
          to: to,
          breakSize: 1
        }]

    chart = Highcharts.chart('projLength', chartOptions)

    // Setting extremes  to start zoomed
    chart.xAxis[0].setExtremes(1, 50);
    chart.showResetZoom();
}
function  fillProjLengthData(chartOptions, data){

    computed = {}

    // calculate the length of each project and accumulate it in the right bin
    data.forEach(function (workflow){
        let start = new Date(workflow.date);
        let end = new Date(workflow.lastModificationDate);
        let length = dateDiffInDays(start, end);
        if (computed[length] == undefined) {
            computed[length] = 1;
        } else {
            computed[length] = computed[length] + 1
        }
    })

    chartOptions.series = [{
            name: 'Project age (days)',
            data: Object.values(computed)
          }];
    chartOptions.xAxis.categories= Object.keys(computed)
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

function drawProjOverTime(data){
    // Prepares the data and draws the evolution of projects over time

    chartOptions = {
        chart: {
            type: 'line'
        },
        title: {
            text: 'Active projects over time'
        },
        subtitle: {
            text: ''
        },
        xAxis: {
        },
        yAxis: {
            title: {
                text: 'Number of projects'
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

    data2ProjectOverTime(chartOptions, data)

    Highcharts.chart('projOvertime', chartOptions);

}

function drawProjByCountry(aggData) {
    const data = propertyAggregationToPieChartData(
        aggData, 'Projects count');

    loadBarChart('#projByCountry', 'Number of projects per country', data, projByCountryTweaker);

}

function projByCountryTweaker(options){
    options.tooltip.pointFormat = '<b>{point.y}</b> projects.';
    options.chart.zoomType='xy';
    options.yAxis ={title:{text:"Number of projects"}}
    options.plotOptions.series.events = {
        click: function (event) {
            window.location.href = window.location.href + "?client_country=" + event.point.name
        }
    }
    options.subtitle = {text: "Zoomable!"}

}

function drawProjByProtCount(aggData) {
    const data = propertyAggregationToPieChartData(
        aggData, 'Projects grouped by protocols count');

        loadBarChart('#projByProtCount', 'Projects grouped by its number of protocols.', data, projByProtCountTweaker);

}

function projByProtCountTweaker(options){
    options.tooltip.headerFormat = '<b>{point.y}</b> projects with {point.key} protocols.';
    options.tooltip.pointFormat = '';
    options.yAxis ={title:{text:"Number of projects"}};
    options.xAxis.title = {text:"Number of protocols in the project"};
    options.chart.zoomType='xy';
    options.xAxis.zoomable = true;
    options.subtitle = {text: "Zoomable!"}
}

$(window).ready(function(){
    getDataAndDrawCharts();
});
