(function($, global) {

    var $search = $('#search');

    $search.placeholder();

    $search.keydown(function(e) {
        if (e.which != 13) return;
        window.location = '/search/' + $search.val();
    });

}(jQuery, window));