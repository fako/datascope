// SHARED VARIABLES
var rad2deg = 180/Math.PI;
var deg = 0;
var componentRadius = 200, topOffset = 220, leftOffset = 150;
var zoomLevel = "small";


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

    var arrowValues = ["left", "top-left", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left"];
    // Place the arrows
    var $arrowsComponent = $('#arrows-component');
    var $arrows = $arrowsComponent.find('.arrow');
    var interval = false;
    $arrows.each(function(i, el) {
        deg = i*45;
        $el = $(el);
        $el.css({
            transform: 'rotate(' + (deg - 90) + 'deg)',
            top: -Math.sin(deg / rad2deg) * (componentRadius - 8) + topOffset - 20,
            left: Math.cos((180 - deg) / rad2deg) * (componentRadius - 8) + leftOffset + 40
        });
        $el.on({
            'mousedown touchstart': function(event) {
                if(interval) {
                    return;
                }
                $this = $(this);
                $this.addClass('active');
                var $self = $this;
                interval = setInterval(function() {
                    wsConnection.send("scrollDocument:" + arrowValues[$arrows.index($self)]);
                }, 100);
            },
            'mouseup touchend touchcancel': function(event){
                if(!interval) {
                    return;
                }
                $(this).removeClass('active');
                clearInterval(interval);
                interval = false;
            },
            'click': function(event){
                wsConnection.send("scrollDocument:" + arrowValues[$arrows.index($(this))]);
            }
        });
    });

});


// ZOOM SLIDER
$(function(){

    // Init the slider
    $("#zoom-component" ).slider({
        orientation: "vertical",
        change: function(event, ui) {
            var zoomLevels = ["small", "large", "xlarge"];
            window.zoomLevel = zoomLevels[ui.value];
            console.log("sending: " + "setDocument:" + $('.knobLabel.active').text() + ',' + zoomLevel);
            wsConnection.send("setDocument:" + $('.knobLabel.active').text() + ',' + zoomLevel);
        },
        max: 2
    });

});


// HELP
$(function() {

    function rotateLabel() {
        var $knobComponent = $('#knob-component');
        var $knobLabels = $knobComponent.find('.knobLabel');
        var $control = $('#control');
        var $currentLabel = $('.knobLabel.active');
        $control.knob('snapTo', ($knobLabels.index($currentLabel)+1) * 60);
    }

    var $helpScreen = $("#help-screen");
    var $helpRotation = setInterval(rotateLabel, 7000);

    $helpScreen.click(function(){
        $helpScreen.removeClass('active');
        wsConnection.send("setHelpScreen:off");
        clearInterval($helpRotation);
    });

    $('#help-button').click(function(){
        $helpScreen.addClass('active');
        wsConnection.send("setHelpScreen:on");
        $helpRotation = setInterval(rotateLabel, 7000);
    });


});

// Reset projection when reloading
$(window).unload(function() {
    wsConnection.send("setDocument:pension,small");

});
