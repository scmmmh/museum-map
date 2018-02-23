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
            });
        },
        load: function(url) {
            var promise = $.ajax(url);
            promise.then(function(data) {
                data = $(data);
                var gallery = data.find('#gallery');
                $('#gallery').replaceWith(gallery);
                var infoblock = data.find('#infoblock');
                $('#infoblock').replaceWith(infoblock);
                infoblock.foundation();
                var breadcrumbs = data.find('#breadcrumbs');
                $('#breadcrumbs').replaceWith(breadcrumbs);
                setTimeout(function() { gallery.gallery(); }, 50);
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
