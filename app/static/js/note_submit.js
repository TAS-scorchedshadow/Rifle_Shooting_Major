$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const stageID = urlParams.get('stageID')
    $('#notes').focus(function () {
        $("#tick").fadeOut(500);
    })
    $( "#notes" ).change(function() {
        $("#spinner").show()
        var fieldVal = $( this ).val();
        console.log(fieldVal)
        $.ajax({
            type:"POST",
            url: "/submit_notes",
            data: JSON.stringify([stageID, fieldVal]),
            success:(function () {
                $("#spinner").hide();
                $("#tick").show();
            })
        })
    });
});