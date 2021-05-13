///Henry & Rishi
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

        $('.editableTable tr').each(function (){
            $('td', this).each(function (){
                let value = $(this).text()
                let width = $(this).width();
                $(this).addClass("cellEditing");
                $(this).html("<input style=width:" + width+ "px type='text' value='" + value + "' />");
                $(this).children().focus();
            })
        })


    });

    let infoDict = {
        "empty": ''
    }

    $('#submit').click(function () {
        console.log("Click submit")
        hideEdit.style.display = "block"
        hideSubmit.style.display = "none"

        $('.editableTable tr').each(function () {
            $('td', this).each(function () {
                let value = $(this).find(":input").val()
                infoDict[$(this).attr("id")] = value
                $(this).html(value);
            })
        })
        let userID =$('#my-data').data('userid')
        let endroute =$('#my-data').data('endroute')
        submitTable(userID, infoDict, endroute)
    })

    function submitTable(userID, infoDict, url) {
        $.ajax({
                type: 'POST',
                url: url,
                data: JSON.stringify([userID, infoDict]),
                success:(function () {
                    console.log('success')
                })
            })
    }
});
