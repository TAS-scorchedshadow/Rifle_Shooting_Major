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

function setAdmin(sourceElement,user){
    $(sourceElement).html(`<div class="spinner-border spinner-border-sm text-primary ml-2"
                                 id="spinner" role="status">
                            </div>`)
    $.ajax({
        data: JSON.stringify({"id": user}),
        type: 'POST',
        url: '/admin',
        dataType: "JSON",
        success: (function (data) {
            // data.newState refers to the new value of state that will be taken on next call of this function
            var new_access = data.access_lvl
            //newHref is a link inside the html button that calls this function with the given parameters
            if (new_access === 0){
                $(sourceElement).html("<i class=\"fas fa-lock\"></i> Student")
                $(sourceElement).removeClass("btn-dark").addClass("btn-secondary")
            }
            else{
                $(sourceElement).html("<i class=\"fas fa-unlock\"></i> Coach")
                $(sourceElement).removeClass("btn-secondary").addClass("btn-dark")
            }
        })
    })

}

function createAccount(sourceElement,user_obj){
    var djangoData = $('#testing').data();
    console.log(djangoData[0])
     $(sourceElement).html(`<div class="spinner-border spinner-border-sm text-primary ml-2"
                                 id="spinner" role="status">
                            </div>`)
    console.log(user_obj)
     $.ajax({
        data: JSON.stringify(djangoData),
        type: 'POST',
        url: '/createAccount',
        dataType: "JSON",
        success: (function (data) {
            console.log("hello")
        })
    })
}

$(document).ready(function () {
    var x = $("#emailContext").data()['mail']
    console.log(x)
    $("#emailContext").children().eq(x).fadeIn("slow")
    $( "#select" ).change(function() {
        update_email_context()
        $("#spinner").show()
         $.ajax({
        data: JSON.stringify($( this ).val()),
        type: 'POST',
        url: '/emailSettings',
        dataType: "JSON",
        success: (function () {
            $("#spinner").hide()
            $("#tick").fadeIn("slow")
            $("#tick").fadeOut(10000)
        })
    })
    });
}
)

function update_email_context(){
    var fieldVal = $( "#select" ).val();
    $("#emailContext").children().hide()
    $("#emailContext").children().eq(fieldVal).fadeIn("slow")
}