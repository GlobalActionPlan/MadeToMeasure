/* JS that should be present on every page, regardless of its function.*/
var m2m = {};
m2m.translation = {};

/* Translations loader. This must be loaded before all other m2m js! */
$(document).ready(function () {
    $('.js_translation').each(function () {
        $(this).children().each(function() {
            var item = $(this);
            var tkey = item.attr('class').replace('js_trans_', '');
            m2m.translation[tkey] = item.text();
        });
    });
});

/* warn when user click previous */
$(document).ready(function() {
    $("#deformprevious").live('click', function(event) {
        if(!confirm(m2m.translation['confirm_back']))
            event.preventDefault();
    });
});

/* descriptions */
$(document).ready(function() {
    show_descriptions();
});

function show_descriptions() {
    $('label.desc').each(function() {
        var desc = $(this).attr('title');
        if(desc != '')
            $(this).after('<p>'+desc+'</p>');
    });
}
