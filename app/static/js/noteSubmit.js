$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const stageID = urlParams.get('stageID')
    var dict = {
        elevation: 100,
        foresight: 10,
        sight: 10,
        sling: 4
    }
    
    $('#notes').focus(function () {
        $("#tick").fadeOut(500);
    })
    $( "#notes" ).change(function() {
        $("#spinner").show()
        var fieldVal = $( this ).val();
        console.log(fieldVal)
        $.ajax({
            type:"POST",
            url: "/submitNotes",
            data: JSON.stringify([stageID, fieldVal]),
            success:(function () {
                $("#spinner").hide();
                $("#tick").show();
            })
        })
    });
    // $( "#settings-button" ).click(function() {
    //     $(this).html("<button type=\"button\" class=\"btn btn-warning btn-lg btn-block\" id=\"save-button\">\n" +
    //         "<i class=\"fas fa-save\"></i>\n" +
    //         "<h5>Save</h5>\n" +
    //         "</button>")
    //     $("#stage-table tbody tr td").each(function () {
    //         $(this).html(`<input type='text' value=${$(this).text()}>`)
    //     })
    // })
});