// Deprecated see table.js
$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userID = urlParams.get('userID')
    $( "#gearTable tbody" ).on( "change", "input", function() {
        var fieldVal = $( this ).val();
        var equipment = $( this ).attr('name');
        $.ajax({
            type:"POST",
            url: "/setGear",
            data: JSON.stringify([userID,equipment,fieldVal])
        })
    });
    loadTable(userID)
    function loadTable(user){
        if (userID != null){
            console.log(user)
            $.ajax({
                type: 'POST',
                url: "/get_gear",
                data: user,
                success:(function (data) {
                    console.log(data)
                    for (var key in data) {
                        var value = data[key]
                        var htmlstring = `<tr><td>`+key+`</td><td><input type="test" id="cD" class="ajaxField"
                            name="` + key + `" value=` + value + `></td></tr>`
                        $("#gearTable").append(htmlstring);
                    }

                })
            })
        }
    }
});