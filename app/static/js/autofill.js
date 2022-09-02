$( document ).ready(function() {
    const clubID = $( "#my-data" ).data("clubid")
    $.ajax({
        type: 'GET',
        url: "/get_names",
        data: {
           clubID
        },
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
