(function($, global) {

  /*
   * SHEET
   * -----
   */
  var Sheet = function(selector) {

    var $el = $(selector)
      , $content = $el.find('.content')
      , $notice = $el.find('.notice')
      , $hideBtn = $notice.find('.hide-btn')
      , self = this;

    var setup = function() {
      $hideBtn.on('click', self.hide);
    };

    this.show = function(html) {
      $content.html(html);
      $el.removeClass('hide');
    }

    this.hide = function() {
      $el.addClass('hide');
    };

    setup();
  };

  /*
   * PREVIEW BUTTON
   * --------------
   */
  var sheet = new Sheet('#preview-sheet');

  $('#preview-btn').click(function(e) {
    var $el = $(this)
      , href = $el.attr('href')
      , $form = $('#create-job form')
      , $spinner = $el.find('#preview-spinner')
      , $text = $el.find('#preview-text')
      , data = $form.serialize();

    e.preventDefault();
    e.stopPropagation();

    $spinner.removeClass('hidden');
    $text.hide();

    $.post(href, data, function(html) {
      $spinner.addClass('hidden');
      $text.show();
      sheet.show(html);
    });
  });

}(jQuery, window));