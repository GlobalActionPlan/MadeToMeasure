/* Scripts only needed for authenticated users */
$(document).ready(function() {
    $('#tag_select [name="tag"]').change(function(event) {
        var tag = $(this).val();
        //Show all
        if (tag == '') {
            $('#tag_listing .question').show();
        }
        //Tag selected, only show tag
        else {
            $('#tag_listing .question').hide();
            $("#tag_listing a.tag_" + tag).parents('.question').show();
        }
        $('#tag_select [name="query"]').val('');
    })
});
$('#tag_listing .tag').live('click', function(event) {
    var tag_select = $('#tag_select [name="tag"]');
    var tag = $(this).text();
    tag_select.find('option:selected').removeAttr('selected');
    tag_select.find('option[value="' + tag +'"]').attr('selected', 'selected').change();
})
$(document).ready(function() {
    $('#tag_select [name="query"]').change(function(event) {
        $('#tag_listing .question').hide();
        $("#tag_listing .question_text:contains('" + $(this).val() + "')").parents('.question').show();
        var tag_select = $('#tag_select [name="tag"]');
        tag_select.find('option:selected').removeAttr('selected');
        tag_select.find("option[value='']").attr('selected', 'selected'); //Don't trigger event
    })
});
