$( document ).ready(function() {
    const target_widths = {
        "300m": 600,
        "400m": 800,
        "500m": 1320,
        "600m": 1320,
        "700m": 1830,
        "800m": 1830,
        "274m": 390,
        "365m": 520,
        "457m": 915,
        "548m": 915,
    }
    const userID = $('#my-data').data("userid");

    //Initialise variables
    $('.season-spinner').show()
    var distance = '300m'
    let size = 0
    let dateRange = $('#date-selector-season').html();
    var seasonData;
    getSeasonShots(userID, distance, dateRange);
    var graphReady = false
    function getSeasonShots(userID, distance, dateRange) {
        if (userID != null){
            $.ajax({
                type: 'POST',
                url: "/get_all_shots_season",
                data: JSON.stringify({
                        'userID': userID,
                        'distance': distance,
                        'dateRange': dateRange,
                        }),
                success:(function (shotData) {
                    // If container is of size 0, then wait till resize then load all shots
                    if ($('#heatMapDiv').width() > 0) {
                        loadAllShots(shotData);
                    }
                    graphReady = true;
                    new ResizeSensor($("#heatMapDiv"), function(){
                        if (graphReady === true) {
                            removeGraphs()
                            loadAllShots(shotData);
                            graphReady = true;
                        }
                    });
                })
            })
        }
    }


    function loadAllShots(shotData){
        //generate the needed html if they are missing
        if ($('#heatMap').length <= 0) {
            let heatMapHtml = `
              <div class='pt-2 mt-2' id='heatMap' style="width:600px; height:600px; margin: auto; padding: 10px;">
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
        // Remove existing heatmap if it exists
        if ($('.heatmap-canvas').length > 0) {
            $('.heatmap-canvas').remove()
        }
        //load shots
        if (userID != null) {
            // Subtract padding
            size = $("#heatMapDiv").width();
            $('#heatMap').css('width', size + 'px');
            $('#heatMap').css('height', size + 'px');

            // Generate heatmap data from shot data
            const ratio = size / target_widths[distance]
            let heatMapData = []
            let heatShotData = {}
            for (let i=0; i<shotData['target'].length; i++) {
                heatShotData = {'x': 0, 'y': 0, 'value': 1}
                heatShotData['x'] = Math.round(shotData['target'][i]['xPos'] * ratio + (size / 2));
                heatShotData['y'] = Math.round(size / 2 - shotData['target'][i]['yPos'] * ratio);
                heatMapData.push(heatShotData);
            }
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
                  data: heatMapData,

            };
            heatmapInstance.setData(testData);
            new DrawTarget('title',distance, shotData['target'], null, size)

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
            if (shotData['bestStage'].score != undefined) {
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
            }
        }
        // Reset the card to 100% instead of a set height
        $('#heatmapCard').css('height', '100%');
    }
    function removeGraphs() {
        graphReady = false;
        $('#heatMap').remove();
        $('#boxPlot').remove();
        $('#bestWorstDiv').remove();
        $('.season-spinner').show();
        $('#boxAlert').hide();

    }
    $('#date-selector-season').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          dateRange = $('#date-selector-season').html();
          // Set the height so that the card doesn't shrink and scroll the user back to the top of the page
          let heatmapWidth = $('#heatmapCard').height();
          $('#heatmapCard').css('height', heatmapWidth.toString() + 'px');
          removeGraphs();
          getSeasonShots(userID, distance, dateRange);
      }
    });
    $('#select-range-span').on('DOMSubtreeModified', async function () {
      if ($(this).html() !== '') {
          distance = $('#select-range-span').html();
          // Set the height so that the card doesn't shrink and scroll the user back to the top of the page
          let heatmapWidth = $('#heatmapCard').height();
          $('#heatmapCard').css('height', heatmapWidth.toString() + 'px');
          removeGraphs();
          getSeasonShots(userID, distance, dateRange);
      }
    });
});
