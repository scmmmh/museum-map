(function($) {
    /**
     * The app jQuery plugin handles the main interaction
     */
    var methods = {
        init: function(options) {
            return this.each(function() {
                var component = $(this);
                component.data('busy-counter', 0);

                component.find('#overview').overview();
                component.find('#infoblock').infoblock().infoblock('fetch', document.location.href + '/infoblock');
                component.find('#items').items().items('fetch', document.location.href + '/items');
                component.find('#breadcrumbs').breadcrumbs().breadcrumbs('fetch', document.location.href + '/breadcrumbs');

                $(window).on('popstate', function(ev) {
                    component.app('load', window.location.href, false);
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
        load: function(url, add_history) {
            if(add_history === undefined) {
                add_history = true;
            }
            return this.each(function() {
                var component = $(this);
                var path = url.split('/');
                component.find('#overview').overview('highlight', path[path.length - 1]);
                component.find('#infoblock').infoblock('fetch', url + '/infoblock');
                component.find('#items').items('fetch', url + '/items');
                component.find('#breadcrumbs').breadcrumbs('fetch', url + '/breadcrumbs');
                if(add_history) {
                    history.pushState(null, '', url);
                }
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
