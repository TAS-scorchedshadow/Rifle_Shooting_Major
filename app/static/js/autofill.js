$( document ).ready(function() {
    $.ajax({
        type: 'POST',
        url: "/getUsers",
        success:(function (data) {
            $( ".user-searchbar" ).autocomplete({
                source: data
             });
        })
    })
});

/*
Attaches an autofill searchbar to any field with the class user-searchbar. The data in the dropdown is defined in the
getUsers url in the routes.py
 */
