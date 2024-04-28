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

    $('a.download').click(function(event) {
        gtag('event', 'social_click', {  // "social_click" is a custom event name
            'event_category': 'Download',  // Categorize this event
            'event_label': event.currentTarget.getAttribute('href'),  // Use the href as the label
            'transport_type': 'beacon'  // Ensures the event is sent before the page unloads
        });
    });

    $('.social a').click(function(event) {
        gtag('event', 'social_click', {  // "social_click" is a custom event name
            'event_category': 'Contact',  // Categorize this event
            'event_label': event.currentTarget.getAttribute('href'),  // Use the href as the label
            'transport_type': 'beacon'  // Ensures the event is sent before the page unloads
        });
    });

    /*****************************
     * Animation
     *****************************/

    function animateSvg($parent, count) {

        var parentWidth = $parent.width();
        var parentHeight = $parent.height();
        var sectionWidth = parentWidth / count;
        var sectionHeight = parentHeight / count;
        var numbers = _.map(Array(count), function(value, ix) {
            return ix
        });
        var randomNumbers = _.shuffle(numbers);

        return function(el, ix) {

            // el is expected to be a random element
            // note that the color of an el is fixed
            // we generate random floats to set random x and y
            // these coordinates get offset by non-repeating random integers
            // to spread the el's out

            var random1 = Math.random();
            var random2 = Math.random();

            $el = $(el);
            $el.css('left', sectionWidth * random1 + sectionWidth * ix);
            $el.css('top', sectionHeight * random2 + sectionHeight * randomNumbers[ix]);

        };
    }

    var $home = $("#home");
    var svgs = _.shuffle($home.find('.svg').toArray());
    _.forEach(svgs, animateSvg($home, svgs.length));

    var $information = $("#information");
    svgs = _.shuffle($information.find('.svg').toArray());
    _.forEach(svgs, animateSvg($information, svgs.length));

    /*****************************
     * Form
     *****************************/

    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

    $('#order-form').submit(function(event) {

        var data = {};
        $(this).serializeArray().forEach(function(input) {
            data[input.name] = input.value;
        });
        if(data.privacy !== 'on') {
            return;
        }
        delete data.privacy;
        var campaign = getParameterByName("utm_campaign");
        if(campaign) {
            data.name += " (" + campaign + ")"
        }

        $.post("/api/v1/discourse-search/order/", data, null, "json")
            .done(function() {
                alert("Bedankt voor de aanvraag we nemen spoedig contact met je op :)");
                gtag('event', 'social_click', {  // "social_click" is a custom event name
                    'event_category': 'Order',  // Categorize this event
                    'event_label': 'done',
                    'transport_type': 'beacon'  // Ensures the event is sent before the page unloads
                });
            })
            .fail(function(){
                alert("Er is helaas iets mis gegaan met je aanvraag. Probeer het straks alsjeblieft nog een keer!");
                gtag('event', 'social_click', {  // "social_click" is a custom event name
                    'event_category': 'Order',  // Categorize this event
                    'event_label': 'fail',
                    'transport_type': 'beacon'  // Ensures the event is sent before the page unloads
                });
            });

        event.preventDefault();
    })

});

