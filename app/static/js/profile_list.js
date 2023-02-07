$(document).ready(function() {
    let users = $('#profile-list').data("users");
    console.log(users);
    let yearGroupDiv = document.getElementById('yearGroups')
    let yearGroupsHtml = ''
    for (let i = 12; i > 6; i--) {
        yearGroupsHtml = appendUsers(yearGroupsHtml, users, i)
    }
    yearGroupsHtml = appendUsers(yearGroupsHtml, users, 'other')
    console.log(yearGroupsHtml)
    $('#yearGroups').append(yearGroupsHtml)
})

function appendUsers(yearGroupsHtml, users, year) {
        if (users[year].length > 1) {
            yearGroupsHtml = yearGroupsHtml +
            `
            <div id="${users[year][0]}" class="mt-3">
                <h4>${users[year][0]}</h4>
            </div>
            `
            for (let j = 1; j < users[year].length; j++){
                yearGroupsHtml = yearGroupsHtml +
                `
                <div class="pl-2 pr-2" style="display:inline-block; align-self: center;">
                    <button class="card mt-3 pl-1 pr-1" style="width:300px; display:inline;" type="submit" onclick="document.getElementById('idInput').value=${users[year][j][2]}">
                        <div class="card-body" style="width:300px">
                            <h6>${users[year][j][1]} ${users[year][j][0]} </h6>
                        </div>
                    </button>
                </div>                 
                `

            }
            yearGroupsHtml += "<hr>"
        }
    return yearGroupsHtml
}