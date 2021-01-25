function deleteAccount(user){
    modal = "#RemoveModal" + user
    $(modal).modal('toggle')
    $.ajax({
        data: JSON.stringify(user),
        type: 'POST',
        url: '/deleteAccount',
        dataType: "JSON",
        success: (function (data) {
            rowID = '#row' + user
            $('#tableBody').find(rowID).fadeOut()
        })
    })

}

function setAdmin(sourceElement,user,state){
    $(sourceElement).attr('disabled','true')
    $.ajax({
        data: JSON.stringify({"id": user, "state": state}),
        type: 'POST',
        url: '/admin',
        dataType: "JSON",
        success: (function (data) {
            // data.newState refers to the new value of state that will be taken on next call of this function
            var stringState = data.newState.toString()
            //newHref is a link inside the html button that calls this function with the given parameters
            $(sourceElement).attr('disabled', 'false')
             if (data.newState === false) {
                $(sourceElement).removeAttr("href")
                $(sourceElement).attr("data-target","#RemoveModal"+user)
                $(sourceElement).attr("data-toggle","modal")
                $(sourceElement).text("Revoke Admin Access")
                $(sourceElement).removeClass("btn-secondary").addClass("btn-danger")
                 //Close respective modal
                modal = "#AdminModal" + user
                $(modal).modal('toggle')
            } else {
                newHref = "javascript:setAdmin('" + sourceElement + "','" + user + "','" + stringState + "')"
                $(sourceElement).attr("href", newHref)
                $(sourceElement).removeAttr("data-target")
                $(sourceElement).removeAttr("data-toggle")

                $(sourceElement).text("Make Admin")
                $(sourceElement).removeClass("btn-danger").addClass("btn-secondary")
            }
        })
    })

}