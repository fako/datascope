// SHARED VARIABLES
var rad2deg = 180/Math.PI;
var deg = 0;
var componentRadius = 200, topOffset = 220, leftOffset = 150;


// THE WORDS POINTER
$(function(){

	// Place the knob labels
    var $knobComponent = $('#knob-component');
    var $knobLabels = $knobComponent.find('.knobLabel');
    var $control = $('#control');
    $knobLabels.each(function(i, el) {
        deg = i*60;
        $el = $(el);
        var orientationDeg = (deg > 180) ? deg + 90: deg - 90;
        $el.css({
            transform: 'rotate(' + orientationDeg + 'deg)',
            top: -Math.sin(deg / rad2deg) * componentRadius + topOffset,
            left: Math.cos((180 - deg) / rad2deg) * componentRadius + leftOffset
        });
        $el.click(function(e) {
            $control.knob('snapTo', $knobLabels.index($(this)) * 60);
        })
    });

	var numBars = 0, lastNum = -1;

	$control.knob({
		value: 154,
		turn : function(ratio) {

			numBars = Math.round(ratio/(1/6));

			// Update the dom only when the number of active bars
			// changes, instead of on every move
			if(numBars == lastNum){
				return false;
			}
			lastNum = numBars;

            $knobLabels.each(function (i, el) {
                var $el = $(el);
                if(i === numBars || (numBars === 6 && i === 0)) {
                    $el.addClass('active');
                } else {
                    $el.removeClass('active');
                }
            });
		}
	});

    $control.knob('snapTo', 0);

});


// THE ARROWS
$(function() {

    // Place the arrows
    var $arrowsComponent = $('#arrows-component');
    var $arrows = $arrowsComponent.find('.arrow');
    $arrows.each(function(i, el) {
        deg = i*45;
        $el = $(el);
        $el.css({
            transform: 'rotate(' + (deg - 90) + 'deg)',
            top: -Math.sin(deg / rad2deg) * (componentRadius - 48) + topOffset,
            left: Math.cos((180 - deg) / rad2deg) * (componentRadius - 48) + leftOffset
        });
        $el.click(function(e) {
            console.log("clicked: ", $arrows.index($(this)));
        })
    });

    $broadcast = $('.arrow');
    $broadcast.on({'mousedown touchstart': function(event){
        wsConnection.send("top-left bingo!");
    }});
    $broadcast.on({'mouseup touchend': function(event){  // naive, put this on document!
        wsConnection.send("top-left bingo 2!");
    }});

});


// ZOOM SLIDER
$(function(){

    // Init the slider
    $("#zoom-component" ).slider({
        orientation: "vertical",
        change: function(event, ui) {
            console.log(ui.value);
        },
        max: 100
    });

});
