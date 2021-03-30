$(document).ready(function () {
    console.log("Confirmed")

    $("#edit").click(function () {
        console.log("Click edit")
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
        "code1": '',
        "name1": '',
        "email1": '',
        "number1": '',
        "code2": '',
        "name2": '',
        "email2": '',
        "number2": '',
        "code3": '',
        "name3": '',
        "email3": '',
        "number3": '',
    }

    $('#submit').click(function () {
        console.log("Click submit")

        $('#editableTable tr').each(function () {
            $('td', this).each(function () {
                let value = $(this).find(":input").val()
                infoDict[$(this).attr("id")] = value
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
