$( document ).ready(function() {
    const userID = $('#my-data').data("userid");
    //Stub
    const distance = '300m'
    //End of Stub
    loadAllShots(userID, distance)
    function loadAllShots(userID, distance){
        if (userID != null){
            $.ajax({
                type: 'POST',
                url: "/getAllShotsSeason",
                data: JSON.stringify({
                        'userID': userID,
                        'distance': distance,
                        }),
                success:(function (shotData) {
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
                    let myTarget = new DrawTarget('title','300m', shotData['target'])
                })
            })
        }
    }
});