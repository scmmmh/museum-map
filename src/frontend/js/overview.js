(function($) {
    /**
     * The overview jQuery plugin handles the overview map
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                component.find('a').on('click', function(ev) {
                    ev.preventDefault();
                    $('#app').app('load', $(this).attr('href'));
                });
                var path = document.location.href.split('/');
                component.find('a#room-' + path[path.length - 1]).addClass('is-active');
            });
        }, highlight(iid) {
            return this.each(function() {
                var component = $(this);
                component.find('a.is-active').removeClass('is-active');
                component.find('a#room-' + iid).addClass('is-active');
            });
        }
    };

    $.fn.overview = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.overview');
        }
    };
}(jQuery));
