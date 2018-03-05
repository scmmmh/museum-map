(function($) {
    /**
     * The app jQuery plugin handles the main interaction
     */
    var methods = {
        init: function(options) {
            return this.each(function() {
                var component = $(this);
                component.data('busy-counter', 0);

                component.find('#infoblock').infoblock();
                component.find('#overview').overview();
                component.find('#items').items();

                component.on('click', '#breadcrumbs a', function(ev) {
                    ev.preventDefault();
                    component.app('load', $(this).attr('href'));
                });

                $(window).on('popstate', function(ev) {
                    component.app('fetch', window.location.href, false);
                });
            });
        },
        start_busy: function() {
            return this.each(function() {
                var component = $(this);
                var overlay = component.find('#overlay');
                component.data('busy-counter', component.data('busy-counter') + 1);
                overlay.show();
                setTimeout(function() { overlay.addClass('is-active'); }, 50);
            });
        },
        end_busy: function() {
            return this.each(function() {
                var component = $(this);
                component.data('busy-counter', component.data('busy-counter') - 1);
                if(component.data('busy-counter') == 0) {
                    var overlay = component.find('#overlay');
                    overlay.removeClass('is-active');
                    setTimeout(function() {overlay.hide();}, 500);
                }
            });
        },
        load: function(url) {
            return this.each(function() {
                var component = $(this);
                component.find('#infoblock').infoblock('fetch', url + '/infoblock');
                component.find('#items').items('fetch', url + '/items');
            });
        }
    };

    $.fn.app = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.app');
        }
    };
}(jQuery));
