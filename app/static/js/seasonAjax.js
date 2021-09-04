$( document ).ready(function() {
    const userID = $('#my-data').data("userid");
    //Initialise variables
    var distance = '300m'
    var size = '600'
    var dateRange = $('#date-selector-season').html();
    loadAllShots(userID, distance, size, dateRange)
    function loadAllShots(userID, distance, size, dateRange){
        //generate the needed html if they are missing
        console.log($('#heatMap').length)
        if ($('#heatMap').length <= 0) {
            let heatMapHtml = `
              <div class='pt-2' id='heatMap' style="width:600px; height:600px">
              </div>
            `;
            $('#heatMapDiv').append(heatMapHtml);
        }
        if ($('#boxPlot').length <= 0) {
            let boxPlotHtml = `
                <canvas id="boxPlot"></canvas>
            `;
            $('#boxPlotDiv').append(boxPlotHtml);
        }
        if ($('#seasonLine').length <= 0) {
            let seasonlineHtml = `
            <div class="col-12" id="seasonlineDiv">
                <div id="seasonLineDiv">
                    <canvas id="seasonLine"></canvas>
                </div>
            </div>
            `;
            $('#seasonlineDiv').append(seasonlineHtml);
        }
        //load shots
        if (userID != null){
            $.ajax({
                type: 'POST',
                url: "/getAllShotsSeason",
                data: JSON.stringify({
                        'userID': userID,
                        'distance': distance,
                        'size': size,
                        'dateRange': dateRange,
                        }),
                success:(function (shotData) {
                    //Add canvas for target (if missing)
                    if ($('#title').length <= 0) {
                        $('#heatMap').append(`<canvas class='canvas' id="title" style="border: 1px solid black"></canvas>`)
                    }
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
    function removeGraphs() {
        $('#heatMap').remove();
        $('#boxPlot').remove();
        $('#seasonlineDiv').remove();
    }
    $('#date-selector-season').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          console.log($('#date-selector-season').html());
          dateRange = $('#date-selector-season').html();
          removeGraphs();
          loadAllShots(userID, distance, size, dateRange);
      }
    });
    $('#select-range-span').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          console.log($('#select-range-span').html());
          distance = $('#select-range-span').html();
          removeGraphs();
          loadAllShots(userID, distance, size, dateRange);
      }
    });
});
