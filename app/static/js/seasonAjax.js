$( document ).ready(function() {
    const userID = $('#my-data').data("userid");
    //Initialise variables
    $('.season-spinner').show()
    var distance = '300m'
    var size = '600'
    var dateRange = $('#date-selector-season').html();
    loadAllShots(userID, distance, size, dateRange)
    function loadAllShots(userID, distance, size, dateRange){
        //generate the needed html if they are missing
        if ($('#heatMap').length <= 0) {
            let heatMapHtml = `
              <div class='pt-2' id='heatMap' style="width:600px; height:600px; margin: auto; padding: 10px;">
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
        if ($('#bestWorstDiv').length <= 0) {
            let bestWorstHtml = `
                <div id="bestWorstDiv" style="display: flex; justify-content: space-around">
                </div>
            `;
            $('#bestWorstCol').append(bestWorstHtml);
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
                        $('#heatMap').append(`<canvas class='canvas' id="title" style="border: 1px solid black; position: absolute; top: 0px; left: 0px;"></canvas>`)
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
                    let myTarget = new DrawTarget('title',distance, shotData['target'], null, size)
                    if (shotData['boxPlot'].length > 1) {
                        $('#boxAlert').hide();
                        boxPlot("boxPlot", shotData['boxPlot'])
                    }
                    else {
                        $('#boxAlert').show();
                    }
                    function boxPlot(canvasID, values) {
                        var lowerbound = 0
                        let lowest = values[0]
                        lowerbound = Math.floor(lowest/5)*5
                        const ctx = document.getElementById(canvasID).getContext('2d');
                        const myBar = new Chart(ctx, {
                          type: 'boxplot',
                          data: {
                                labels: [''],
                                datasets: [
                                    {
                                        label: 'Score out of 50',
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
                    $('.season-spinner').hide()

                    //Show best and worst stages
                    let bestHtml = `
                    <div style="display: flex; flex-direction: column; justify-content: space-between">
                    <h4>Best Stage: ${shotData['bestStage'].score} / 50</h4>
                    <a href="/target?stageID=${shotData['bestStage'].id}" class="btn btn-primary" target="_blank">View Plotsheet <i class="fas fa-external-link-alt" style="color:black;"></i></a>
                    </div>
                 
                    `;
                    $('#bestWorstDiv').append(bestHtml);
                    let worstHtml = `
                    <div style="display: flex; flex-direction: column; justify-content: space-between">
                    <h4>Worst Stage: ${shotData['worstStage'].score} / 50</h4>
                    <a href="/target?stageID=${shotData['worstStage'].id}" class="btn btn-primary" target="_blank">View Plotsheet <i class="fas fa-external-link-alt" style="color:black;"></i></a>
                    </div>
                    `;
                    $('#bestWorstDiv').append(worstHtml);

                })
            })
        }
    }
    function removeGraphs() {
        $('#heatMap').remove();
        $('#boxPlot').remove();
        $('#bestWorstDiv').remove();
        $('.season-spinner').show();
        $('#boxAlert').hide();

    }
    $('#date-selector-season').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          dateRange = $('#date-selector-season').html();
          removeGraphs();
          loadAllShots(userID, distance, size, dateRange);
      }
    });
    $('#select-range-span').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          distance = $('#select-range-span').html();
          removeGraphs();
          loadAllShots(userID, distance, size, dateRange);
      }
    });
});
