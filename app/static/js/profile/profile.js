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

    let $backToTop = $(".back-to-top");
    $backToTop.hide();
    $(window).on('scroll', function() {
    if ($(this).scrollTop() > 500) {
        $backToTop.fadeIn(150);
    } else {
        $backToTop.fadeOut(150);
    }
    });

    $backToTop.on('click', function(e) {
        $("html, body").animate({scrollTop: 0}, 300);
    });
})