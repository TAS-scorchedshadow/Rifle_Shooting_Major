$( document ).ready(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userID = urlParams.get('userID')
    loadTable(userID)
    function loadTable(user){
        if (userID != null){
            console.log(user)
            $.ajax({
                type: 'POST',
                url: "/getGear",
                data: user,
                success:(function (data) {
                    console.log(data)
                    for (var key in data) {
                        var value = data[key]
                        console.log(key)
                        console.log(value)
                        var htmlstring = `<tr><td>`+key+`</td><td><input type="test" name="` + key + `" value=` + value + `></td></tr>`
                        $("#gearTable").append(htmlstring);
                    }

                })
            })
        }
    }
});