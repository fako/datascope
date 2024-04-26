$(function() {

    /*****************************
    * Navigation
    *****************************/

    $('a[href*=\\#]:not([href=\\#])').click(function() {

        if (location.pathname.replace(/^\//,'') === this.pathname.replace(/^\//,'') &&
            location.hostname === this.hostname)
        {

            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                gtag('event', 'page_view', { 'page_path': this.hash });
                $('#navbar-collapse-main').collapse('hide');
                $('html,body').animate({
                    scrollTop: target.offset().top - parseInt(target.css('padding-top'))
                }, 1000);
                return false;
            }
        }

    });

    $('.social a').click(function(event) {
        gtag('event', 'social_click', {  // "social_click" is a custom event name
            'event_category': 'Contact',  // Categorize this event
            'event_label': event.currentTarget.getAttribute('href'),  // Use the href as the label
            'transport_type': 'beacon'  // Ensures the event is sent before the page unloads
        });
    });

});
