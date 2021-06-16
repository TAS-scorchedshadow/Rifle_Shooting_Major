$( document ).ready(function() {
    const userID = $('#my-data').data("userid");
    //Stub
    const distance = '300m'
    //End of Stub
    loadAllShots(userID, distance)
    function loadAllShots(userID, distance){
        if (userID != null){
            $.ajax({
                type: 'POST',
                url: "/getAllShotsSeason",
                data: JSON.stringify({
                        'userID': userID,
                        'distance': distance,
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
                    let myTarget = new DrawTarget('title','300m', shotData['target'])
                })
            })
        }
    }
    boxPlot(boxData['canvasID'], boxData['values'])
    function boxPlot(canvasID, values) {
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
                          min: 40,
                      }
                  }
          },
        });
    }
});
