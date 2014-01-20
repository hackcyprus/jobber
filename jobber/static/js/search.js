(function($, global) {
    console.log("Asdgasdgasdg")
    var $search = $('#search');
    console.log($search)
    $search.keydown(function(e) {
        console.log("asfasf")
        if (e.which != 13) return;
        window.location = '/search/' + $search.val();
    });

}(jQuery, window));