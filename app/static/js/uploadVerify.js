// Ryan T
$(document).ready(function() {
    // When submit button is pressed run fetchData
    $(#submit).click(function() {
        let usernameDict = {};
        $(".user-searchbar").each(function() {
            let name = $(this).attr("name")
            let value = $(this).attr("value")
            usernameDict[name] = value;
        console.log(usernameDict)
        })
        // fetchData()
    })
    function fetchData() {
        $.ajax({
            type: 'POST',
            url: '/uploadVerify'
        })
    }
    // Data needs to be returned in a variable stageList, as well as invalidListID,
    // which then needs to be broken down into parts

    // After this a loop needs to be added which uploads shoots one (or multiple) at a time to the database
    // Each pass increments a loading bar, as well as adds to a 'success' or 'failure' count, as well as 'total' count

    // After completion, depending on number of success or failure, switch to correct page
})
