$(document).ready(function () {
    console.log("Confirmed")

    $("button").click(function () {
        console.log("Click")
        var OriginalContent = $(this).text();

        $("td").addClass("cellEditing");
        $("td").html("<input type='text' value='" + OriginalContent + "' />");
        $("td").children().focus();

        $("td").children().keypress(function (e) {
            if (e.which == 13) {
                var newContent = $(this).val();
                $("td").parent().text(newContent);
                $("td").parent().removeClass("cellEditing");
            }
        });

    $("td").children().first().blur(function(){
        $("td").parent().text(OriginalContent);
        $("td").parent().removeClass("cellEditing");
    });
    });
    function submitTable(userID, cell, info) {
        $.ajax({
                type: 'POST',
                url: "/submitTable",
                data: [userID, cell, info],
                success:(function () {
                    console.log('success')
                })
            })
    }
});
