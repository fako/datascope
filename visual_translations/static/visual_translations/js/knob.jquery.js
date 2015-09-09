/**
 * @name		jQuery KnobKnob plugin
 * @author		Martin Angelov
 * @version 	1.0
 * @url			http://tutorialzine.com/2011/11/pretty-switches-css3-jquery/
 * @license		MIT License
 */

(function($) {

    self = this;

    function init(props){

		self.options = $.extend({
			value: 0,
			turn: function(){}
		}, props || {});
        self.startDeg = -1;
        self.rotation = 0;

		var tpl = '<div class="knob">\
				<div class="top"></div>\
			</div>';

		return this.each(function(){

			var el = $(this);
			el.append(tpl);

			var knob = $('.knob',el),
                currentDeg = 0,
				lastDeg = 0,
				doc = $(document);

            self.knobTop = knob.find('.top');

			if(self.options.value > 0 && self.options.value <= 359){
				self.rotation = currentDeg = self.options.value;
				self.knobTop.css('transform','rotate('+(currentDeg)+'deg)');
				self.options.turn(currentDeg/359);
			}

			knob.on('mousedown touchstart', function(e) {

				e.preventDefault();

				var offset = knob.offset();
				var center = {
					y : offset.top + knob.height()/2,
					x: offset.left + knob.width()/2
				};

				var a, b, deg, tmp,
					rad2deg = 180/Math.PI;

				knob.on('mousemove.rem touchmove.rem',function(e) {

                    var xPos = (e.type === "touchmove") ? e.originalEvent.touches[0].pageX : e.pageX;
                    var yPos = (e.type === "touchmove") ? e.originalEvent.touches[0].pageY : e.pageY;

					a = center.y - yPos;
					b = center.x - xPos;
					deg = Math.atan2(a,b)*rad2deg;

					// we have to make sure that negative
					// angles are turned into positive:
					if(deg<0){
						deg = 360 + deg;
					}

					// Save the starting position of the drag
					if(self.startDeg == -1){
						self.startDeg = deg;
					}

					// Calculating the current rotation
					tmp = Math.floor((deg-self.startDeg) + self.rotation);

					// Making sure the current rotation
					// stays between 0 and 359
					if(tmp < 0){
						tmp = 360 + tmp;
					}
					else if(tmp > 359){
						tmp = tmp % 360;
					}

					currentDeg = tmp;
					lastDeg = tmp;

					self.knobTop.css('transform','rotate('+(currentDeg)+'deg)');
					self.options.turn(currentDeg/359);
				});

				doc.on('mouseup.rem touchend.rem',function(){
					knob.off('.rem');
					doc.off('.rem');

					// Saving the current rotation
					self.rotation = currentDeg;

					// Marking the starting degree as invalid
					self.startDeg = -1;
				});

			});
		});
	}

    function snapTo(degrees) {
        self.knobTop.css('transform','rotate('+degrees+'deg)');
        options.turn(degrees/359);
        self.rotation = degrees;
        self.startDeg = -1;

    }

    var methods = {
        init : init,
        snapTo : snapTo
    };

    $.fn.knob = function(methodOrOptions) {
        if ( methods[methodOrOptions] ) {
            return methods[ methodOrOptions ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof methodOrOptions === 'object' || ! methodOrOptions ) {
            // Default to "init"
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  methodOrOptions + ' does not exist on jQuery.knob' );
        }
    };

})(jQuery);