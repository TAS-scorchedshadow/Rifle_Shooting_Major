function setActive(sourceElement,user,state){
    $(sourceElement).attr('disabled','true')
    $.ajax({
    data : JSON.stringify({"id": user, "state": state}),
    type : 'POST',
    url : '/activate',
    dataType: "JSON",
    }).success(function (data) {
        // data.newState refers to the new value of state that will be taken on next call of this function
        var stringState = data.newState.toString()
        //newHref is a link inside the html button that calls this function with the given parameters
        newHref = "javascript:setActive('"+sourceElement+"','"+user+"','"+stringState+"')"
        $(sourceElement).attr("href",newHref)
        $(sourceElement).attr('disabled','false')
        if (data.newState === false) {
            $(sourceElement).text("Deactivate Account")
            $(sourceElement).removeClass("btn-secondary")
            $(sourceElement).addClass("btn-primary")
        }
        else{
            $(sourceElement).text("Activate Account")
            $(sourceElement).removeClass( "btn-primary" )
            $(sourceElement).addClass("btn-secondary")
        }
    })

}