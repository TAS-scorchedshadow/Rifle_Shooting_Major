$( document ).ready(function() {
    const userID = $('#my-data').data("userid");
    //Stub
    let distance = '300m'
    let size = '600'
    //End of Stub
    loadAllShots(userID, distance, size)
    function loadAllShots(userID, distance, size){
        if (userID != null){
            $.ajax({
                type: 'POST',
                url: "/getAllShotsSeason",
                data: JSON.stringify({
                        'userID': userID,
                        'distance': distance,
                        'size': size,
                        }),
                success:(function (shotData) {
                    var heatmapInstance = h337.create({
                      container: document.getElementById('heatMap')
                    });
                    var testData = {
                          max: 10,
                          min: 0,
                          data: shotData['heatmap'],

                    };
                    heatmapInstance.setData(testData);
                    console.log(heatmapInstance.getData());
                    //TODO add slider to change intensity of heatmap
                    let myTarget = new DrawTarget('title',distance, shotData['target'], null, size)
                    console.log(shotData['boxPlot'])
                    boxPlot(boxData['canvasID'], shotData['boxPlot'])
                    function boxPlot(canvasID, values) {
                        var lowerbound = 0
                        let lowest = values[0]
                        lowerbound = Math.floor(lowest/5)*5
                        const ctx = document.getElementById("boxPlot").getContext('2d');
                        const myBar = new Chart(ctx, {
                          type: 'boxplot',
                          data: {
                                labels: ['A'],
                                datasets: [
                                    {
                                        label: 'Test',
                                        backgroundColor: 'rgba(255, 0, 0, 0.1)',
                                        borderColor: 'rgba(255,0,0,1)',
                                        borderWidth: 1,
                                        data: [values],
                                    },
                                ]
                            },
                          options: {
                            indexAxis: 'y',
                            responsive: true,
                            legend: {
                              position: 'top',
                            },
                            title: {
                              display: true,
                              text: 'Chart.js Box Plot Chart',
                            },
                             scales: {
                                      x: {
                                          max: 50,
                                          min: lowerbound,
                                      }
                                  }
                          },
                        });
                    }
                })
            })
        }
    }
});
