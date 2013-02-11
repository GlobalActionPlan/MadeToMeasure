/* Drag-drop questions to survey sections */

/* Attach sort function */
$(document).ready(function(){
    $('.pickable_questions').sortable({
        connectWith: '.pickable_questions',
        receive: function(event, ui) {
            var name = ui.item.parents('ul').attr('name');
            ui.item.children('input').attr('name', name);
        }
    });
});

/* Attach functions for add all/remove all-buttons */
$(document).ready(function() {
    var processed_tags = {};
    $('.pickable_questions .question input').each(function() {
        var tags = $(this).attr('class').split(' ');
        for (i = 0; i < tags.length; ++i) {
            tag = tags[i].substring(4);
            if ((tags[i].substring(0, 4) == 'tag_') && (! (tag in processed_tags))) {
                processed_tags[tag] = 0;
                $('.add_from_tag').append('<option>' + tag + '</option>');
            }
        }
    });
    $('.add_questions').click(function() {
        var tag = $(this).siblings('.add_from_tag').val();
        var name = $(this).parent().siblings('ul').attr('name');
        if (tag != '(tags)') {
            $('#tag_listing .tag_' + tag).attr('name', name);
            $('#tag_listing .tag_' + tag).parent().appendTo($(this).parents('li').find('ul'));
        }
    });
    $('.del_questions').click(function() {
        var tag = $(this).siblings('.add_from_tag').val();
        if (tag != '(tags)') {
            $(this).parents('li').find('.question .tag_' + tag).attr('name', '');
            $(this).parents('li').find('.question .tag_' + tag).parent().appendTo($('#tag_listing'));
        }
    });
});
