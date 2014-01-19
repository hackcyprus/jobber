(function($, global) {

  var $form = $('#create-job form');

  var fields = [
    '#title',
    '#job_type',
    '#remote_work',
    '#location__city',
    '#location__country_code',
    '#description',
    '#company__name',
    '#company__website',
    '#recruiter_name',
    '#recruiter_email',
    '#contact_method',
    '#contact_url',
    '#contact_email'
  ];

  /*
   * CALLBACKS
   * ---------
   */
  var getErrorContainer = function(el) {
    var $el = $(el)
      , $field = $el.parent('.field')
      , $container = $field.find('.parsley-error-container');

    if ($container.length == 0) {
      $container = $("<div class='parsley-error-container'></div>");

      if ($el.hasClass('selectized')) {
        $el = $field.find('.selectize-control');
      } else if ($el.hasClass('wysiwyged')) {
        $el = $field.find('.wysihtml5-sandbox');
      }

      $container.insertAfter($el);
    }

    return $container;
  };

  var onFieldValidate = function(el) {
    var $el = $(el);
    if ($el.hasClass('selectized') || $el.hasClass('wysiwyged')) return false;
    return !$el.is(':visible');
  };

  /*
   * PARSLEY CONFIG
   * --------------
   */
  var config = {
    inputs: fields.join(', '),
    useHtml5Constraints: false,
    focus: 'none',
    errors: {
      container: getErrorContainer
    },
    listeners: {
      onFieldValidate: onFieldValidate
    },
    messages: {
      required: 'This is required.'
    }
  };

  $form.parsley(config);

}(jQuery, window));
