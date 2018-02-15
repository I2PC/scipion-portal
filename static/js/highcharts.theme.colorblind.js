/**
 * Accessible high-contrast theme for Highcharts. Considers colorblindness and
 * monochrome rendering. As described at http://www.somersault1824.com/tips-for-designing-scientific-figures-for-color-blind-readers/
 * @author Pablo Conesa
 */

Highcharts.theme = {
   colors: ['#000000', '#004949',
            '#009292', '#FF6DB6',
            '#FEB5DA', '#490092',
            '#006DDB', '#B66DFF',
            '#6DB6FF', '#B6DBFF',
            '#920000', '#924900',
            '#DB6D00', '#24FF24',
            '#FFFF6D'],
   colorAxis: {
      maxColor: '#05426E',
      minColor: '#F3E796'
   },

   plotOptions: {
      map: {
         nullColor: '#fcfefe'
      }
   },

   navigator: {
      maskFill: 'rgba(170, 205, 170, 0.5)',
      series: {
         color: '#95C471',
         lineColor: '#35729E'
      }
   }
};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);