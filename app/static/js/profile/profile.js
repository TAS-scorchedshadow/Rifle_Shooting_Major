$(document).ready(function() {
    $(".show-details-btn").click(function() {
        $(".profile-details").slideToggle("slow");
        let $this = $(this);
        $this.toggleClass("hide-details");
        if ($this.hasClass("hide-details")) {
            $this.text("Hide details");
        } else {
            $this.text("Show details");
        }
    });
})