/* warn when user click previous */
$(document).ready(function() {
    $("#deformprevious").live('click', function(event) {
        if(!confirm(m2m.trans['confirm_back']))
            event.preventDefault();
    });
});

/* descriptions */
$(document).ready(function() {
    $('label.desc').each(function() {
        var desc = $(this).attr('title');
        if(desc != '')
            $(this).after('<p>'+desc+'</p>');
    });
});