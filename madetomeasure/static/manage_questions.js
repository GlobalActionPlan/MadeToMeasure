/* Drag-drop questions to survey sections */

/* Attach sort function */
$(document).ready(function(){
    $('.pickable_questions').sortable({
        connectWith: '.pickable_questions',
        receive: function(event, ui) {
            console.log(ui.item);
            var name = ui.item.parents('ul').attr('name');
            console.log(name);
            ui.item.children('input').attr('name', name);
        }
    });
});

