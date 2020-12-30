$(function() {

    /*****************************
     * Navigation
     *****************************/

    $('a[href*=\\#]:not([href=\\#])').click(function() {

        if (location.pathname.replace(/^\//,'') === this.pathname.replace(/^\//,'') &&
            location.hostname === this.hostname)
        {

            var target = $(this.hash);
            var windowOffset = document.documentElement.scrollTop || document.body.scrollTop;
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                ga('send', 'pageview', this.hash);
                $('html,body').animate({
                    scrollTop: windowOffset + target.offset().top - 2*parseInt(target.css('padding-top'))
                }, 1000);
                return false;
            }
        }

    });

    $('a.team-member').click(function(event) {
        ga('send', 'event', 'Team', event.currentTarget.attributes.href.value)
    });

    $('.social a').click(function(event) {
        ga('send', 'event', 'Contact', event.currentTarget.attributes.href.value)
    });


    /*****************************
     * Form
     *****************************/

    $('#subscribe-form').submit(function() {
        ga('send', 'event', 'Subscribe')
    })

});
