//By Henry Guo with some edit from Dylan Huynh
$(document).ready(function(){
    // const queryString = window.location.search;
    // const urlParams = new URLSearchParams(queryString);
    // const userID = urlParams.get('userID')
    let dateRange = $('#date-selector').html();
    const userID = $('#my-data').data("userid");
    loadTable(userID, dateRange);
    function removeTables(){
        $('.stage-overview').remove();
        $('.no-stages-found').remove();
    }
    function loadTable(user, dateRange){
        if (userID != null){
            let numLoaded = $("div[class*='stage-overview']").length;
            $('#shotSpinner').toggleClass('d-flex');
            $('#shotSpinner').show();
            $.ajax({
                type: 'POST',
                url: "/getShots",
                data: JSON.stringify([user, numLoaded, dateRange]),
                success:(function (data) {
                    console.log(data)
                    $('#shotSpinner').toggleClass('d-flex');
                    $('#shotSpinner').hide()
                    if (Array.isArray(data) && data.length){
                        for (let stage in data) {
                            let shots = data[stage]['scores']
                            let htmlScoresBody = ``
                            let htmlSighters = ``
                            for (let shot in data[stage]['scores']) {
                                htmlScoresBody = htmlScoresBody + `${data[stage]['scores'][shot]} `;
                            }
                            for (let shot in data[stage]['sighters']){
                                htmlSighters = htmlSighters + `${data[stage]['sighters'][shot]} `;
                            }
                            //missing icons for duration and weather
                            let htmlstring = `
                        <div class="stage-overview">
                            <div class="row">
                                <div class="col-12 pb-4">
                                    <a href="/target?stageID=${data[stage]['stageID']}" target="_blank">
                                        <div class="card shadow border-0 card-hover">
                                            <div class="card-header recent-header">
                                                <div class="row">
                                                    <div class="col-4 align-self-center">
                                                        <p style="font-size:12px">${data[stage]['duration']}</p>
                                                    </div>
                                                    <div class="col-4 align-self-center">
                                                        <p display="block" class="text-center" style="font-size:12px;">${data[stage]['timestamp']}</p>
                                                    </div>
                                                    <div class="col-4 align-self-center">
                                                        <p class="text-right" style="font-size:12px"></p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="recent-body">
                                                <div class="row">
                                                    <div class="col-12">
                                                        <div class="table-responsive">
                                                            <table class="table table-sm table-bordered recentShotsTable">
                                                                <thead>
                                                                    <tr>
                                                                        <th style='width: 50px;'>Range</th>
                                                                        <th style='width: 62px;'>Sighters</th>
                                                                        <th>Shots</th>
                                                                        <th style='width: 43px;'>Total</th>
                                                                        <th style='width: 48px;'>Group</th>
                                                                        <th style='width: 37px;'>Std</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    <tr>
                                                                        <th>${data[stage]['distance']}</th>
                                                                        <th>${htmlSighters}</th>
                                                                        <th>${htmlScoresBody}</th>
                                                                        <th>${data[stage]['totalScore']}</th>
                                                                        <th>${data[stage]['groupSize']}</th>
                                                                        <th>${data[stage]['std']}</th>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                            </div>
                        </div>
                        `;
                            $("#recentShots").append(htmlstring);
                            $("#moreShoots").prop("disabled", false);
                        }
                    }
                    else{
                        let htmlstring = `
                        <div class="text-center align-items-center p-3 no-stages-found">
                            <h2>No Stages Found :(</h2>
                            <svg class="py-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 231.1 175.2" style="width:10rem;">
                               <polygon class="logoCol" points="113.9 67.9 153.1 0 74.7 0 113.9 67.9"/>
                               <polygon class="logoCol" points="69.4 13.1 108.6 79 32.6 175 0 138.9 69.4 13.1"/>
                               <polygon class="logoCol" points="158.8 11.6 120.2 79.1 198.6 175.2 231.1 138.1 158.8 11.6"/>
                            </svg>
                            <h5>A summary of recent stages will be shown here. Make sure to enter the correct username at the range!</h5>
                        </div>
                        `
                        $("#recentShots").append(htmlstring);
                        $('#moreShoots').hide();
                    }
                })
            })
        }
        else {
            console.log('Error: No userID');
        }
    }
    //Append more shoots when the more button has been clicked
    $('#moreShoots').click(function() {
            console.log('running loadTable');
            $(this).prop("disabled", true);
            loadTable(userID);
        })
    //Check for date range change then update the shoots accordingly
    $('#date-selector').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          console.log($('#date-selector').html());
          let dateRange = $('#date-selector').html();
          removeTables();
          loadTable(userID, dateRange);
      }
    });
})