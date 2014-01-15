 (function($, window) {

  $(function() {
    var $type = $('#job_type')
      , $locationId = $('#location__id')
      , $city = $('#location__city')
      , $country = $('#location__country_code')
      , $remote = $('#remote_work')
      , $contact = $('#contact_method')
      , $contactUrl = $('#contact_url')
      , $contactEmail = $('#contact_email')
      , $tags = $('#tags');

    /*
     * HELPERS
     * -------
     */

    var findLocation = function(cityName) {
      return _.find(LOCATIONS, function(location) {
        return location.city == cityName;
      });
    };

    var updateCities = function(countryCode) {
      var selectize = $city.selectize()[0].selectize
        , existingCity = $city.val();

      selectize.clearOptions();

      _.each(LOCATIONS, function(location) {
        if (location.country_code !== countryCode) return;
        selectize.addOption(location);
      });

      selectize.refreshOptions(false);

      // If $city already has a *correct* value set (i.e we're in edit mode)
      // we restore it.
      var location = findLocation(existingCity);
      if (location != null && location.country_code === countryCode) {
        selectize.setValue(existingCity);
      }
    };

    var onLocationChange = function(cityName) {
      var location = findLocation(cityName);
      $locationId.val(location != null ? location.id : null);
      return location;
    };

    /*
     * SELECTIZE
     * ---------
     */

    $type.selectize();
    $remote.selectize();

    $city.selectize({
      maxItems: 1,
      valueField: 'city',
      labelField: 'city',
      searchField: ['city'],
      openOnFocus: true,
      create: true,
      onChange: function(value) {
        this.$input.attr('value', value);
        onLocationChange(value);
      }
    });

    $country.selectize({
      onInitialize: function(a) {
        updateCities(this.getValue());
      },
      onChange: function(value) {
        updateCities(value);
        onLocationChange();
      }
    });

    $contact.selectize({
      onInitialize: function(a) {
        if (!_.isEmpty($contactEmail.val())) {
          $contactUrl.toggle();
          $contactEmail.toggle();
        }
      },
      onChange: function(value) {
        $contactUrl.toggle();
        $contactEmail.toggle();
      }
    });

    $tags.selectize({
      delimiter: ',',
      valueField: 'slug',
      labelField: 'tag',
      searchField: ['tag', 'slug'],
      create: true,
      options: TAGS
    });

    /*
     * WYSIHTML5
     * ---------
     */
    var editor = new wysihtml5.Editor('description', {
      toolbar: 'description-toolbar',
      parserRules:  wysihtml5ParserRules,
      stylesheets: [
        'https://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,700italic,300,400,700',
        '/static/css/editor.css'
      ]

    });

    /*
     * Sheet
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
        $el.removeClass('hidden');
      }

      this.hide = function() {
        $el.addClass('hidden');
      };

      setup();
    };

    /*
     * Preview button
     * --------------
     */
    var sheet = new Sheet('#preview-sheet');

    $('#preview-btn').click(function(e) {
      var $el = $(e.target)
        , href = $el.attr('href')
        , $form = $('#create-job form')
        , data = $form.serialize();

      e.preventDefault();
      e.stopPropagation();

      $.post(href, data, function(html) {
        sheet.show(html);
      });
    });

  });
}(jQuery, window));