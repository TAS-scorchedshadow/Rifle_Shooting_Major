function deleteAccount(user){
    modal = "#RemoveModal" + user
    const clubID = $('#club-data').data("clubid");
    $(modal).modal('toggle')
    $.ajax({
        data: JSON.stringify({"userID": user, "clubID": clubID}),
        type: 'POST',
        url: '/delete_account',
        dataType: "JSON",
        success: (function (data) {
            rowID = '#row' + user
            $('#tableBody').find(rowID).fadeOut()
        })
    })

}

function setAdmin(sourceElement,userID,clubID){
    $(sourceElement).html(`<div class="spinner-border spinner-border-sm text-primary ml-2"
                                 id="spinner" role="status">
                            </div>`)
    $.ajax({
        data: JSON.stringify({"userID": userID, "clubID": clubID}),
        type: 'POST',
        url: '/make_admin',
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

const role_replace = []
role_replace[0] = ["<i class=\"fas fa-lock\"></i> Restricted", "btn-warning"]
role_replace[1] = ["<i class=\"fas fa-unlock\"></i> Standard", "btn-primary"]
role_replace[2] = ["<i class=\"fas fa-whistle\"></i> Manager", "btn-dark"]

function source_element(source, access_level) {
    console.log(source.html())

    source.removeClass("btn-primary btn-secondary btn-warning btn-dark")
    source.html(role_replace[access_level][0])
    source.addClass(role_replace[access_level][1])
}

$(document).ready(function () {
    var x = $("#emailContext").data()['mail']
    const clubID = $('#club-data').data("clubid");
    $("#emailContext").children().eq(x).fadeIn("slow")
    $( "#select" ).change(function() {
        update_email_context()
        $("#spinner").show()
         $.ajax({
        data: JSON.stringify({"email_setting": $( this ).val(), "clubID": clubID}),
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
        $("#spinner").show()
        $.ajax({
            type: 'POST',
            url: "/update_season_date",
            data: JSON.stringify({
                    'date_range': date_range,
                    'clubID' : clubID
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


     $(".role-swapper").click(function() {
         const level = $(this).data("lvl")
         console.log($(this).data("lvl"))
         $.ajax({
            data: JSON.stringify({"level": level, "userid": $(this).data("userid")}),
            type: 'POST',
            url: '/make_admin',
            dataType: "JSON",
            success: source_element($(this).parent().parent().children(".role-btn"), level)
        })
         return false;
     })
}
)

function update_email_context(){
    var fieldVal = $( "#select" ).val();
    $("#emailContext").children().hide()
    $("#emailContext").children().eq(fieldVal).fadeIn("slow")
}