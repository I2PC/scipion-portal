
function drawScipionIntegrationGraph(id, elements) {


    var cy = cytoscape({

        container: document.getElementById(id), // container to render in

        elements: elements,

        style: [ // the stylesheet for the graph
            {
                selector: 'node',
                style: {
                    'background-color': '#bb797a',
                    'font-size': 9
                }
            },

            {
                selector: 'edge',
                style: {
                    'width': 1,
                    'line-color': '#222',
                    "line-style": "dotted",
                    'target-arrow-color': '#b22',
                    'target-arrow-shape': 'triangle'
                }
            }
        ],
        userZoomingEnabled: false,
        layout: getLayout()
    });

    cy.on('tap', 'node', function() {
        window.location.href = this.data('href');
    });
}

function getLayout() {

let options = {
        name: 'cose',
        nodeDimensionsIncludeLabels: false,
        animate: true,
        numIter: 500,
        randomize: false,
        componentSpacing: 200,
      }
    return options;

}