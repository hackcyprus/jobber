 (function($, window) {

  var domReady = function() {
    var $title = $('#title')
      , $type = $('#job_type')
      , $locationId = $('#location__id')
      , $city = $('#location__city')
      , $country = $('#location__country_code')
      , $remote = $('#remote_work')
      , $contact = $('#contact_method')
      , $contactUrl = $('#contact_url')
      , $contactEmail = $('#contact_email')
      , $companyName = $('#company__name')
      , $companyWebsite = $('#company__website')
      , $recruiterName = $('#recruiter_name')
      , $recruiterEmail = $('#recruiter_email')
      , $tags = $('#tags');

    /*
     * HELPERS
     * -------
     */
    var findLocation = function(city, country) {
      var len = LOCATIONS.length
        , i, loc;

      for (i = 0; i < len; i++) {
        loc = LOCATIONS[i];
        if (loc.city === city && loc.country_code === country) return loc;
      }
    };

    var updateCities = function(country) {
      var selectize = $city.selectize()[0].selectize
        , city = $city.val();

      selectize.clearOptions();

      $.each(LOCATIONS, function(index, location) {
        if (location.country_code !== country) return;
        selectize.addOption(location);
      });

      selectize.refreshOptions(false);

      // If $city already has a *correct* value set (i.e we're in edit mode)
      // then we restore it.
      var location = findLocation(city, country);
      if (location && location.country_code == country) {
        selectize.setValue(city);
      }
    };

    var onLocationChange = function(city, country) {
      var location = findLocation(city, country);
      $locationId.val(location != null ? location.id : null);
      return location;
    };

    /*
     * JQUERY-PLACEHOLDER
     * ------------------
     */
    var placeholders = [
      $title,
      $companyName,
      $companyWebsite,
      $recruiterName,
      $recruiterEmail,
      $contactUrl,
      $contactEmail
    ];

    $.each(placeholders, function(i, $el) {
      $el.placeholder();
    });

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
      create: true,
      onChange: function(value) {
        var city = value
          , country = $country.selectize()[0].selectize.getValue();
        this.$input.attr('val', city);
        onLocationChange(city, country);
      }
    });

    $country.selectize({
      onInitialize: function(a) {
        updateCities(this.getValue());
      },
      onChange: function(value) {
        // Cleanup the currently selected location.
        $locationId.val(null);
        updateCities(value);
      }
    });

    $contact.selectize({
      onInitialize: function(a) {
        if ($contactEmail.val()) {
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
  };

  $(domReady);

}(jQuery, window));