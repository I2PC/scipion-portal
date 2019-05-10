
function drawScipionIntegrationGraph(id, elements) {


    var cy = cytoscape({

        container: document.getElementById(id), // container to render in

        elements: elements,

        style: [ // the stylesheet for the graph
            {
                selector: 'node',
                style: {
                    'color': '#eee',
                    'text-outline-color': '#555',
                    'text-outline-width': 2,
                    'background-opacity': 0,
                    'font-size': 11,
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center'
                }
            },

            {
                selector: 'edge',
                style: {
                    'width': 1,
                    'line-color': '#bbb',
                    "line-style": "dotted",
                    'target-arrow-color': '#b22',
                    'target-arrow-shape': 'none'
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