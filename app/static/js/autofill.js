$( document ).ready(function() {
    $.ajax({
        type: 'POST',
        url: "/getUsers",
        success:(function (data) {
            $( "#user-searchbar-field" ).autocomplete({
                source: data
             });
        })
    })
});