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

    var noop = function(e) {
      e.preventDefault();
      e.stopPropagation();
    };

    this.show = function(html) {
      $content.html(html);
      $el.removeClass('hide');
      return this;
    }

    this.hide = function() {
      $el.addClass('hide');
      return this;
    };

    this.hijackAnchors = function() {
      $content.find('a').on('click', noop);
      return this;
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

    // Validate form before submitting for preview. Expects the form to be
    // already decorated with Parsley.
    if (!$form.parsley('validate')) return false;

    $spinner.removeClass('hidden');
    $text.hide();

    $.post(href, data, function(html) {
      $spinner.addClass('hidden');
      $text.show();
      sheet.show(html).hijackAnchors();
    });

    return false;
  });

}(jQuery, window));