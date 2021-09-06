$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const stageID = urlParams.get('stageID')
    loadTable(stageID)
    function loadTable(stage){
        if (stageID != null){
            $.ajax({
                type: 'POST',
                url: "/getTargetStats",
                data: stage,
                success:(function (data) {
                })
            })
        }
    }
});