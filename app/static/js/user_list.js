function deleteAccount(user){
    modal = "#RemoveModal" + user
    $(modal).modal('toggle')
    $.ajax({
        data: JSON.stringify(user),
        type: 'POST',
        url: '/delete_account',
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
        url: '/email_settings',
        dataType: "JSON",
        success: (function () {
            $("#spinner").hide()
            $("#tick").fadeIn("slow")
            $("#tick").fadeOut(10000)
        })
    })
    });


    // Season Date Picker
    function changeSeasonDate(date_range) {
        console.log("running ajax");
        $("#spinner").show()
        $.ajax({
            type: 'POST',
            url: "/update_season_date",
            data: JSON.stringify({
                    'date_range': date_range,
                    }),
            success:(function (ajax_status) {
                $("#spinner").hide()
                $("#tick").fadeIn("slow")
                $("#tick").fadeOut(10000)
            })
        })
    }
    $('#date-selector').on('DOMSubtreeModified', function () {
      if ($(this).html() !== '') {
          changeSeasonDate($(this).html());
      }
    });
}
)

function update_email_context(){
    var fieldVal = $( "#select" ).val();
    $("#emailContext").children().hide()
    $("#emailContext").children().eq(fieldVal).fadeIn("slow")
}