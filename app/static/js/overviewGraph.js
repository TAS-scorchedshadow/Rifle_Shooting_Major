//by Henry Guo (line 13-46 by Rishi)
$(document).ready(function() {
    const userID = $('#my-data').data("userid");
    loadShotAvgGraph(userID)
    function loadShotAvgGraph(user) {
        $('#graphSpinner').toggleClass('d-flex');
        $.ajax({
            type: 'POST',
            url: "/getAvgShotGraphData",
            data: JSON.stringify(user),
            success: (function (data) {
                let ctx = document.getElementById('lineSTDEV').getContext('2d');
                let barChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: data['times'],
                        datasets: [{
                            label: 'Average',
                            yAxisID: 'Score',
                            backgroundColor: 'rgba(255, 0, 0, 0.1)',
                            borderColor: 'rgba(255,0,0,1)',
                            borderWidth: 1,
                            fill: true,
                            data: data['scores'],
                            pointRadius: 5,
                            pointHitRadius: 20,
                        },
                        {
                            label: 'Standard Deviation',
                            yAxisID: 'Standard Deviation',
                            backgroundColor: 'rgba(0, 0, 255, 0.1)',
                            borderColor: 'rgba(0,0,255,1)',
                            borderWidth: 1,
                            fill: true,
                            data: data['sd'],
                            pointRadius: 5,
                            pointHitRadius: 20,
                        }],
                    },
                    options: {
                        responsive: true,
                        title: {
                            display: true,
                            text: 'Averages Line'
                        },
                        plugins: {
                        },
                        scales: {
                            yAxes: [{
                                id: 'Score',
                                type: 'linear',
                                position: 'left',
                                ticks: {
                                  max: 50,
                                  min: 0
                                }
                            }, {
                                id: 'Standard Deviation',
                                type: 'linear',
                                position: 'right',
                            }]
                        }
                    }
                });
                $('#graphSpinner').toggleClass('d-flex');
                $('#graphSpinner').hide();
            })
        })
    }
})