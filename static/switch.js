$(document).ready(function() {

    // Iterate over checkboxes
    $("input[type=checkbox].switch").each(function() {

    // Insert mark-up for switch
        $(this).before(
            '<span class="switch">' +
            '<span class="mask" /><span class="background" />' +
            '</span>'
    );
    // Hide checkbox
    $(this).hide();

    // Set inital state
    if (!$(this)[0].checked) {
    $(this).prev().find(".background").css({left: "-56px"});
    }
    }); // End each()

    // Toggle switch when clicked
    $("span.switch").click(function() {
    // If on, slide switch off
    if ($(this).next()[0].checked) {
    $(this).find(".background").animate({left: "-56px"}, 200);
    // Otherwise, slide switch on
    } else {
    $(this).find(".background").animate({left: "0px"}, 200);
    }
    // Toggle state of checkbox
    $(this).next()[0].checked = !$(this).next()[0].checked;
    });
}); // End ready()
