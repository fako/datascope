   var scrollDelta = 20;
        $(document).on('keydown', function(event){
        switch(event.which) {
            case 49:
                var top = $(document).scrollTop();
                var left = $(document).scrollLeft();
                $(document).scrollTop(top + scrollDelta);
                $(document).scrollLeft(left + scrollDelta);
                console.log("One pressed");
                break;
        }

});
