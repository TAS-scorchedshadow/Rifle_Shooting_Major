$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const stageID = urlParams.get('stageID')
    $( "#notes").on( "change", "input", function() {
        var fieldVal = $( this ).val();
        console.log(fieldVal)
        $.ajax({
            type:"POST",
            url: "/submitNotes",
            data: JSON.stringify([stageID, fieldVal])
        })
    });
});