$(function() {
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                _paq.push(['trackPageView', this.hash]);
                $('#navbar-collapse-main').collapse('hide');
                $('html,body').animate({
                    scrollTop: target.offset().top - parseInt(target.css('padding-top'))
                }, 1000);
                return false;
            }
        }

    });

});