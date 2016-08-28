var WORDS = ['pension', 'women', 'peace', 'cowshed', 'immigrants', 'leave'];
var index = 0;
setInterval(function() {
    $('#word-highlight').text(WORDS[index]);
    index = ++index % WORDS.length;
}, 3000);