/* Drag-drop questions to survey sections */
var unsaved = false;
var edit_variant = "";


$('#deformsave').on('click', function() {
    unsaved = false;
});
$(window).on('beforeunload', function() {
    if (unsaved) {
        return "You have unsaved changes";
    }
});

$(document).ready(function(){
    /* Attach sort function */
    $('.pickable_questions').sortable({
        connectWith: '.pickable_questions',
        receive: function(event, ui) {
            var name = ui.item.parents('ul').attr('name');
            ui.item.children('input').attr('name', name);
        },
        update: function(event, ui) {
          if (! unsaved) {
            unsaved = true;
          }
        }
    });

    /* Attach functions for add all/remove all-buttons */
    var processed_tags = [];

    /* Collect tags from question pool */
    $('.pickable_questions .question input').each(function() {
        var tags = $(this).attr('class').split(' ');
        for (i = 0; i < tags.length; ++i) {
            tag = tags[i].substring(4);
            if ((tags[i].substring(0, 4) == 'tag_') && (processed_tags.indexOf(tag) == -1)) {
                processed_tags.push(tag);
            }
        }
    });

    /* Insert option tag */
    processed_tags.sort();
    for (i = 0; i < processed_tags.length; ++i) {
      $('.add_from_tag').append('<option>' + processed_tags[i] + '</option>');
    }

    /* Click handler for add-from-tag-button */
    $('.add_questions').click(function() {
        var tag = $(this).siblings('.add_from_tag').val();
        var name = $(this).parent().siblings('ul').attr('name');
        if (tag != '(tags)') {
            $('#tag_listing .tag_' + tag).attr('name', name);
            $('#tag_listing .tag_' + tag).parent().appendTo($(this).parents('li').find('ul'));
        }
    });

    /* Click handler for del-from-tag-button */
    $('.del_questions').click(function() {
        var tag = $(this).siblings('.add_from_tag').val();
        if (tag != '(tags)') {
            $(this).parents('li').find('.question .tag_' + tag).attr('name', '');
            $(this).parents('li').find('.question .tag_' + tag).parent().appendTo($('#tag_listing'));
        }
    });
    
    /* Click handler for edit pen / variants */
    $('.edit_variant').click(function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        var fullscreen = $('#fullscreen');
        edit_variant = $(this).parents('li');
        fullscreen.load(url, function() {
            fullscreen.fadeIn();
            $('#fullscreen form').on('submit', ajax_save_variant);
            $('#deformcancel').on('click', function(event) {
                event.preventDefault();
                fullscreen.empty().fadeOut();
            });
            show_descriptions();
        });
    });
});

function ajax_save_variant(event) {
    event.preventDefault();
    var url = $(this).attr('action');
    var fullscreen = $('#fullscreen');
    var formdata = $(this).serialize();
    formdata += "&save=save";
    $.post(url, formdata, function(data) {
        var data = $.parseJSON(data);
        edit_variant.children('.question_text').html(data['question_text']);
        if (data['is_variant']) {
            edit_variant.addClass('variant');
        } else {
            edit_variant.removeClass('variant');
        }
        fullscreen.empty().fadeOut();
    })
    .fail(function() {
        alert("Save failed!");
    });
}
