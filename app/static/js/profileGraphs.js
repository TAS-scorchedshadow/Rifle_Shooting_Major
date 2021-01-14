function Attendance(){
    var ctx = document.getElementById('attendance').getContext('2d');
    console.log(ctx);
    var attendance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [155, 13],
                backgroundColor: [
                    'rgba(91, 188, 228, 0.85)',
                    'rgba(139, 69, 19, 0.85)',
                                ],
                label: 'Dataset 1'
                    }],
            labels: [
                'Attended',
                'Not Attended'
                    ]
            },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Attendance'
                },
            plugins: {
                legend: {
                    position: 'top',
                        },
                    },
            animation: {
                                        animateScale: true,
                                        animateRotate: true
                                    }
                                }
                                });
}

function lineGraph(dateData, scores){
    var ctx = document.getElementById('lineSTDEV').getContext('2d');
    console.log(dateData);
    var barChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: dateData,
            datasets: [{
                label: 'Averages',
                backgroundColor: 'rgba(255,0,0,0)',
                borderColor: 'rgba(255,0,0,1)',
                borderWidth: 1,
                fill: false,
                data: scores
                        }]},
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
}