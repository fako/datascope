$(function(){

	var rad2deg = 180/Math.PI;
	var deg = 0;

	var $bars = $('#bars');
    var $knobLabels = $bars.find('.knobLabel');
    var $control = $('#control');

	// Place the colorbars
    $knobLabels.each(function(i, el) {
        deg = i*60;
        $el = $(el);
        $el.css({
            transform: 'rotate(' + (deg - 90) + 'deg)',
            top: -Math.sin(deg / rad2deg) * 80 + 100,
            left: Math.cos((180 - deg) / rad2deg) * 80 + 75
        });
        $el.click(function(e) {
            console.log("click");
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

});
