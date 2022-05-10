$(document).ready(function() {
    let users = $('#profile-list').data("users");
    console.log(users);
    let yearGroupDiv = document.getElementById('yearGroups')
    let yearGroupsHtml = ''
    for (let i = 12; i > 6; i--) {
        yearGroupsHtml = yearGroupsHtml +
        `
        <div id="${users[i][0]}" class="mt-3">
            <h4>${users[i][0]}</h4>
        </div>
        `
        if (users[i].length > 1) {
            for (let j = 1; j<users[i].length; j++){
                yearGroupsHtml = yearGroupsHtml +
                `
                <div class="pl-2 pr-2" style="display:inline-block; align-self: center;">
                    <button class="card mt-3 pl-1 pr-1" style="width:300px; display:inline;" type="submit" onclick="document.getElementById('idInput').value=${users[i][j][2]}">
                        <div class="card-body" style="width:300px">
                            <h6>${users[i][j][1]} ${users[i][j][0]} </h6>
                        </div>
                    </button>
                </div>                 
                `

            }
        }
        else {
            yearGroupsHtml = yearGroupsHtml +
                `
                No shooters
                `
        }
        yearGroupsHtml = yearGroupsHtml + "<hr>"
    }
    console.log(yearGroupsHtml)
    $('#yearGroups').append(yearGroupsHtml)
})