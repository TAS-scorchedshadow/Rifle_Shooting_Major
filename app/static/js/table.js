///Henry & Rishi
$(document).ready(function () {
    $(".submit").hide()

    $(".edit").click(function () {
        $(this).hide()
        $(".submit").show()

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
    }

    $('.submit').click(function () {
        $("#spinner").show()


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
                    $("#spinner").hide();
                    $(".edit").show()
                    $(".submit").hide()
                })
            })
    }
});
