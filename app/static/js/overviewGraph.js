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
                            label: 'Averages',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            borderColor: 'rgba(255,0,0,1)',
                            borderWidth: 1,
                            fill: true,
                            data: data['scores'],
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
                                min: 0,
                                ticks: {
                                    min: 0,
                                    beginAtZero:true
                                }
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