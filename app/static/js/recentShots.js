$(document).ready(function(){
    console.log('hello')
    //TODO add loading symbols
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userID = urlParams.get('userID')
    loadTable(userID)
    function loadTable(user){
        if (userID != null){
            let numLoaded = $("div[class*='stage-overview']").length
            console.log(numLoaded)
            $.ajax({
                type: 'POST',
                url: "/getShots",
                data: JSON.stringify([user, numLoaded]),
                success:(function (data) {
                    console.log(data)
                    for (let stage in data){
                        let shots = data[stage]['scores']
                        let htmlScoresHead = ``
                        let htmlScoresBody = ``
                        for (let shot in data[stage]['scores']){
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
                            <div class="row">
                                <div class="col-12 pb-4">
                                    <div class="card shadow border-0 h-100">
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
                                </div>
                            </div>
                        </div>
                        `;
                        $("#recentShots").append(htmlstring);
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
