$( document ).ready(function() {
    $.ajax({
        type: 'GET',
        url: "/get_names",
        success:(function (data) {
            $( ".user-searchbar" ).autocomplete({
                source: data
             });
        })
    })
});

/*
Attaches an autofill searchbar to any field with the class user-searchbar. The data in the dropdown is defined in the
get_users url in the routes.py
 */
