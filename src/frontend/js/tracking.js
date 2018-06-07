(function($) {
    /**
     * The tracking jQuery plugin handles the GDPR-compliant tracking system
     */
    var methods = {
        init: function(options) {
            return this.each(function() {
                var component = $(this);

                if(localStorage.getItem('museum-map-tracking') !== null) {
                    component.hide();
                }
                if(localStorage.getItem('museum-map-tracking') === 'true') {
                    $('footer label span').html('Thank you for contributing');
                } else {
                    $('footer label span').html('Your interactions are not being tracked');
                }
                $('*[name=tracking-switch]').prop('checked', localStorage.getItem('museum-map-tracking') === 'true');
                $('input[name=tracking-switch]').on('change', function() {
                    component.hide();
                    var consented = $(this).filter(':checked').length > 0;
                    localStorage.setItem('museum-map-tracking', consented);
                    $('*[name=tracking-switch]').prop('checked', consented);
                    if(consented) {
                        $('footer label span').html('Thank you for contributing');
                    } else {
                        $('footer label span').html('Your interactions are not being tracked');
                    }
                });
            });
        },
        track: function(data) {
            return this.each(function() {
                var component = $(this);
                if(localStorage.getItem('museum-map-tracking') === 'true') {
                    if(localStorage.getItem('musem-map-tracking-id') !== null) {
                        data['uuid'] = localStorage.getItem('musem-map-tracking-id');
                    }
                    var promise = fetch(component.data('tracking-url'), {
                        body: JSON.stringify(data),
                        credentials: 'same-origin',
                        headers: {
                            'content-type': 'application/json'
                        },
                        method: 'POST',
                        referrer: 'no-referrer'
                    });
                    promise.then(function(response) {
                        response.json().then(function(data) {
                            localStorage.setItem('musem-map-tracking-id', data.uuid);
                        });
                    });
                }
            });
        }
    };

    $.fn.tracking = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.tracking');
        }
    };
}(jQuery));
