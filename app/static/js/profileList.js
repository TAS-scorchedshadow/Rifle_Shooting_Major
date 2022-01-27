$(document).ready(function() {
    let users = $('#profile-list').data("users");
    console.log(users);
    let yearGroupDiv = document.getElementById('yearGroups')
    let yearGroupsHtml = ''
    for (let i = 12; i > 6; i--) {
        yearGroupsHtml = yearGroupsHtml +
        `
        <div id="${users[i][0]}">
            <h4>${users[i][0]}</h4>
        </div>
        `
        for (let i = 0; i; i++){

        }
    }
    $('#yearGroups').append(yearGroupsHtml)
})