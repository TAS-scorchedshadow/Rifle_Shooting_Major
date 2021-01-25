$(document).ready(function(){
    console.log('hello')
    //TODO add loading symbols
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userID = urlParams.get('userID')
    loadTable(userID)
    function loadTable(user){
        if (userID != null){
            let numLoaded = $("div[class*='stage-overview']").length;
            $('#spinner').toggleClass('d-flex');
            $('#spinner').show();
            console.log(numLoaded);
            $.ajax({
                type: 'POST',
                url: "/getShots",
                data: JSON.stringify([user, numLoaded]),
                success:(function (data) {
                    console.log(data)
                    $('#spinner').toggleClass('d-flex');
                    $('#spinner').hide()
                    if (Array.isArray(data) && data.length){
                        for (let stage in data) {
                            let shots = data[stage]['scores']
                            let htmlScoresHead = ``
                            let htmlScoresBody = ``
                            for (let shot in data[stage]['scores']) {
                                htmlScoresHead = htmlScoresHead + `
                            <th>${shot}</th>
                            `;
                                htmlScoresBody = htmlScoresBody + `
                            <th>${data[stage]['scores'][shot]}</th>
                            `;
                            }
                            //missing icons for duration and weather
                            let htmlstring = `
                        <div class="stage-overview">
                            <a class="row">
                                <div class="col-12 pb-4">
                                    <a class="stretched-link" href="/target?stageID=${data[stage]['stageID']}" target="_blank">
                                        <div class="card shadow border-0">
                                            <div class="card-header">
                                                <div class="row">
                                                    <div class="col-4 align-self-center"
                                                        <p>${data[stage]['duration']}</p>
                                                    </div>
                                                    <div class="col-4 align-self-center">
                                                        <p class="text-center">${data[stage]['timestamp']}</p>
                                                    </div>
                                                    <div class="col-4 align-self-center">
                                                        <p class="text-right">weather</p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="col-12">
                                                        <div class="table-responsive">
                                                            <table class="table table-sm table-bordered">
                                                                <thead>
                                                                    <tr>
                                                                        <th>Range</th>
                                                                        ${htmlScoresHead}
                                                                        <th>Total Score</th>
                                                                        <th>Group Size</th>
                                                                        <th>Std</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    <tr>
                                                                        <th>${data[stage]['rangeDistance']}</th>
                                                                        ${htmlScoresBody}
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
                        }
                    }
                    else{
                        let htmlstring = `
                        <div class="text-center align-items-center p-3">
                            <h2>No Recent Stages Found :(</h2>
                            <svg class="py-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 231.1 175.2" style="width:10rem;">
                               <polygon class="logoCol" points="113.9 67.9 153.1 0 74.7 0 113.9 67.9"/>
                               <polygon class="logoCol" points="69.4 13.1 108.6 79 32.6 175 0 138.9 69.4 13.1"/>
                               <polygon class="logoCol" points="158.8 11.6 120.2 79.1 198.6 175.2 231.1 138.1 158.8 11.6"/>
                            </svg>
                            <h5>A summary of recent stages will be shown here. Make sure to enter the correct username at the range!</h5>
                        </div>
                        `
                        $("#recentShotsContainer").replaceWith(htmlstring);
                    }
                })
            })
        }
        else {
            console.log('Error: No userID')
        }
        $('#moreShoots').click(function() {
            loadTable(userID)
        })
    }
})
