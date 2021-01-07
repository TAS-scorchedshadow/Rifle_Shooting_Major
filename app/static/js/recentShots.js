$(document).ready(function(){
    console.log('hello')
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userID = urlParams.get('userID')
    loadTable(userID, 0)
    function loadTable(user, numLoaded){
        if (userID != null){
            console.log(user)
            $.ajax({
                type: 'POST',
                url: "/getShots",
                data: JSON.stringify([user, numLoaded]),
                // success:(function (data) {
                //     console.log(data)
                //     for (var key in data) {
                //         var value = data[key]
                //         var htmlstring = `<tr><td>`+key+`</td><td><input type="test" id="cD" class="ajaxField" name="` + key + `" value=` + value + `></td></tr>`
                //         $("#gearTable").append(htmlstring);
                //     }
                //
                // })
            })
        }
    }
})