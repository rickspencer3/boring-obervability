// Select the container element
var container = document.getElementById('my-graph');

// Create a new graph and set the container
var graph = new Graph(container);

// Set the data for the graph
var data = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr'],
  datasets: [
    {
      label: 'Sales',
      data: [10, 15, 20, 12]
    },
    {
      label: 'Expenses',
      data: [5, 8, 12, 10]
    }
  ]
};

// Set the options for the graph
var options = {
  type: 'line',
  height: 400,
  width: 600
};

// Render the graph
graph.render(data, options);