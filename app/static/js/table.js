//Henry & Rishi
$(document).ready(function () {
    console.log("Confirmed")
    let hideSubmit = document.getElementById("submit")
    let hideEdit = document.getElementById("edit")
    hideSubmit.style.display = "none"

    $("#edit").click(function () {
        console.log("Click edit")

        hideEdit.style.display = "none"
        hideSubmit.style.display = "block"

        var OriginalContent = $(this).text();

        $('#editableTable tr').each(function (){
            $('td', this).each(function (){
                let value = $(this).text()

                $(this).addClass("cellEditing");
                $(this).html("<input type='text' value='" + value + "' />");
                $(this).children().focus();
            })
        })


    $("td").children().first().blur(function(){
        $("td").parent().text(OriginalContent);
        $("td").parent().removeClass("cellEditing");
    });
    });

    let infoDict = {
        "shooterID": '',
        "dob": '',
        "rifleSerial": '',
        "schoolID": '',
        "schoolYr": '',
        "email": '',
        "permitNumber": '',
        "permitExpiry": '',
        "sharing": '',
        "mobile": '',
    }

    $('#submit').click(function () {
        console.log("Click submit")
        hideEdit.style.display = "block"
        hideSubmit.style.display = "none"

        $('#editableTable tr').each(function () {
            $('td', this).each(function () {
                let value = $(this).find(":input").val()
                infoDict[$(this).attr("id")] = value
                $(this).html("<td>" + value +  "</>");
            })
        })
        let userID =$('#user-data').data('userid')
        submitTable(userID, infoDict)
    })

    function submitTable(userID, infoDict) {
        $.ajax({
                type: 'POST',
                url: "/submitTable",
                data: JSON.stringify([userID, infoDict]),
                success:(function () {
                    console.log('success')
                })
            })
    }
});
