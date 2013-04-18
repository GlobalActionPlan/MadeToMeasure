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
/* Minimize
 * Structure to make minimize work. elem can be most html tags
 * <elem id="something_unique" class="toggle_area toggle_closed"> <!--or toggle_opened -->
 *   <elem class="toggle_minimize">Something clickable</elem> <!-- if this allso has the class reload the page is reloaded after maximizing
 *   <elem class="minimizable_area">Stuff that will be hidden</elem>
 *   <elem class="minimizable_inverted">Stuff that will only be visible when it's minimized</elem>
 * </elem>
 */
$('.toggle_minimize').live('click', function(event) {
    try { event.preventDefault(); } catch(e) {}
    min_parent = $(this).parents('.toggle_area');
    // set cookie for opened or closed
    var cookie_id = min_parent.attr('id');
    if($(this).hasClass('reload')) {
        if (min_parent.hasClass('toggle_opened')) {
            $.cookie(cookie_id, 1, { expires: 7, path: '/'});
        } else {
            $.cookie(cookie_id, null, { expires: 7, path: '/'});
            location.reload();
        }
    }
    // Set parent class as opened or closed
    min_parent.toggleClass('toggle_opened').toggleClass('toggle_closed');
})

