$(function(){

	var rad2deg = 180/Math.PI;
	var deg = 0;
	var bars = $('#bars');

	// Place the colorbars
    $('.knobLabel').each(function(i, el) {
        deg = i*60;
        $(el).css({
            transform: 'rotate(' + (deg - 90) + 'deg)',
            top: -Math.sin(deg / rad2deg) * 80 + 100,
            left: Math.cos((180 - deg) / rad2deg) * 80 + 75
        });
    });

	var colorBars = bars.find('.knobLabel');
	var numBars = 0, lastNum = -1;

	$('#control').knob({
		value: 154,
		turn : function(ratio) {

			numBars = Math.round(ratio/(1/6));

			// Update the dom only when the number of active bars
			// changes, instead of on every move
			if(numBars == lastNum){
				return false;
			}
			lastNum = numBars;

            $('.knobLabel').each(function (i, el) {
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
