//by Henry Guo (line 13-46 by Rishi)
$(document).ready(function() {
    const userID = $('#my-data').data("userid");
    getShotData(userID)
    function getShotData(userID) {
        $('#attendanceSpinner').show();
        $.ajax({
            type: 'GET',
            url: "/api/num_shots_season",
            data: {userID: userID},
            success: (function (data) {
               console.log(data)
                $('#attendanceSpinner').hide()
                let htmlContent = `
                    <table class="table table-sm table-bordered">
                      <tbody>
                        <tr>
                          <th scope="row">Sessions</th>
                          <td>${data["num_sessions"]}</td>
                        </tr>
                        <tr>
                          <th scope="row">Stages</th>
                          <td>${data["num_stages"]}</td>
                        </tr>
                        <tr>
                          <th scope="row">Shots</th>
                          <td>${data["num_shots"]}</td>
                        </tr>
                        <tr>
                          <th scope="row">Avr. Shots per Session</th>
                          <td>${data["num_shots_per_session"]}</td>
                        </tr>
                      </tbody>`
                $("#attendanceContent").html(htmlContent)
            })
        })
    }
})