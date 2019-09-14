var me = sessionStorage;
var sem = me.branch_regex + "_3";

var subject = {};                              // object of subject and name map  --|
                                                                        //          |-->  both must map to same index
var data = {};          // object of all marks in form of { 'roll': [marks,...] } --|

var NAMES = {}

var rolls = ['2017UGCS005', '2017UGCS006', '2017UGCS007'];


function generate_chart() {

    var linectx = $("#lineChart");

    var labels = Object.keys(subject);

    var datasets = [];

    for(var i in data) {

            if(i != me['roll']) {

                datasets.push( [{
                    label : "ME",
                    data: data[me['roll']],
                    lineTension: 0,
                    borderColor: 'rgba(231, 243, 31)',
                    backgroundColor: 'transparent',
                },
                {
                    label: NAMES[i],
                    data: data[i],
                    lineTension: 0,
                    borderColor: 'rgba(113,156,241)',
                    backgroundColor: 'transparent',
                }] );

            }
    }

    console.log("Datasets: ", datasets);

    new Chart(linectx, {
      type: 'line',
      data: {
        labels: labels,

        datasets: datasets[0]
      },
      options: {
        title: {
          display: true,
          text: 'Line Chart'
        },

        scales: {
          yAxes:[{
            ticks: {
              min: 0,
              max: 100,
              stepSize: 20
            }
          }]
        },

        tooltips: {
          callbacks: {
            title: function(item) {
              item = item[0].xLabel;
              return subject[item]['subject_name'];
            }
          }
        }
      }
    });

    datasets[0][0].backgroundColor = "rgba(231, 243, 31)";
    datasets[0][1].backgroundColor = "rgba(113,156,241)";
    var barctx = $("#barChart");
    new Chart(barctx, {
      type: 'bar',
      data: {
        labels: labels,

        datasets: datasets[0]
      },
      options: {
        title: {
          display: true,
          text: 'Bar Chart'
        },

        scales: {
          yAxes:[{
            ticks: {
              min: 0,
              max: 100,
              stepSize: 20
            }
          }]
        },

        tooltips: {
          callbacks: {
            title: function(item) {
              item = item[0].xLabel;
              return subject[item]['subject_name'];
            }
          }
        }
      }
    });
}
