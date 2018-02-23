(function($) {
    /**
     * The app jQuery plugin handles the main interaction
     */
    var methods = {
        init: function(options) {
            return this.each(function() {
                var component = $(this);
                component.find('#infoblock .accordion').foundation()
                component.find('#overview').overview();
                component.find('#gallery').gallery();
                component.on('click', '#breadcrumbs a', function(ev) {
                    ev.preventDefault();
                    component.app('load', $(this).attr('href'));
                });
                $(window).on('popstate', function(ev) {
                    component.app('fetch', window.location.href, false);
                });
            });
        },
        load: function(url) {
            this.app('fetch', url, true);
        },
        fetch: function(url, updateHistory) {
            return this.each(function() {
                var component = $(this);
                var overlay = component.find('#overlay');
                overlay.show();
                setTimeout(function() { overlay.addClass('is-active'); }, 50);
                var promise = $.ajax(url);
                promise.then(function(data) {
                    data = $(data);
                    var gallery = data.find('#gallery');
                    component.find('#gallery').replaceWith(gallery);
                    var infoblock = data.find('#infoblock');
                    component.find('#infoblock').replaceWith(infoblock);
                    infoblock.foundation();
                    var breadcrumbs = data.find('#breadcrumbs');
                    component.find('#breadcrumbs').replaceWith(breadcrumbs);
                    document.title = data.filter('title').html();
                    overlay.removeClass('is-active');
                    setTimeout(function() { gallery.gallery(); }, 50);
                    setTimeout(function() { overlay.hide(); }, 500);
                    if (updateHistory) {
                        history.pushState(null, document.title, url);
                    }
                });
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
