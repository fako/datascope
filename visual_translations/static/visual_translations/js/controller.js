$(function(){

	var rad2deg = 180/Math.PI;
	var deg = 0;

	var $knobComponent = $('#knob-component');
    var $knobLabels = $knobComponent.find('.knobLabel');
    var $control = $('#control');

	// Place the knob labels
    $knobLabels.each(function(i, el) {
        deg = i*60;
        $el = $(el);
        var orientationDeg = (deg > 180) ? deg + 90: deg - 90;
        $el.css({
            transform: 'rotate(' + orientationDeg + 'deg)',
            top: -Math.sin(deg / rad2deg) * 80 + 100,
            left: Math.cos((180 - deg) / rad2deg) * 80 + 75
        });
        $el.click(function(e) {
            $control.knob('snapTo', $knobLabels.index($(this)) * 60);
        })
    });

    // Place the arrows
    var $arrowsComponent = $('#arrows-component');
    var $arrows = $arrowsComponent.find('.arrow');
    $arrows.each(function(i, el) {
        deg = i*45;
        $el = $(el);
        $el.css({
            transform: 'rotate(' + (deg - 90) + 'deg)',
            top: -Math.sin(deg / rad2deg) * 80 + 100,
            left: Math.cos((180 - deg) / rad2deg) * 80 + 75
        });
        $el.click(function(e) {
            console.log("clicked: ", $arrows.index($(this)));
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
