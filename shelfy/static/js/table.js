


// Total updating function

$(document).ready(function() {
    console.log('Trying to do something');
    $('input[type=checkbox][name=sell-checkbox]').change(function() {
        console.log($(this).value());
    });
});
