var WORDS = ['pension', 'women', 'peace', 'cowshed', 'immigrants', 'leave'];
var index = 0;
$('#word-highlight').text(WORDS[index++]);
setInterval(function() {
    $('#word-highlight').text(WORDS[index]);
    index = ++index % WORDS.length;
}, 10000);
