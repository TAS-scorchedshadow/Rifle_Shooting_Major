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
                            yAxisID: 'score',
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
                            yAxisID: 'standard-deviation',
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
                        maintainAspectRatio: false,
                        plugins: {
                        },
                        scales: {
                            'score': {
                                position: 'left',
                                max: 50,
                                min: 0,
                                title: {
                                    display: true,
                                    text: 'Score out of 50'
                                },

                            },
                            'standard-deviation': {
                                position: 'right',
                                max: 3,
                                min: 0,
                                title: {
                                    display: true,
                                    text: 'Standard Deviation'
                                },
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Dates'
                                },
                            }
                        }
                    }
                });
                $('#graphSpinner').toggleClass('d-flex');
                $('#graphSpinner').hide();
            })
        })
    }
})