(function($) {
    /**
     * The breadcrumbs jQuery plugin handles the breadcrumbs list and page title
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                component.on('click', 'a', function(ev) {
                    ev.preventDefault();
                    $('#app').app('load', $(this).attr('href'));
                });
            });
        },
        fetch(url) {
            return this.each(function() {
                var component = $(this);
                $('#app').app('start_busy');
                var promise = $.ajax(url);
                promise.then(function(data) {
                    data = $(data);
                    component.empty();
                    component.append(data);
                    document.title = data.find('li:last-child').attr('title');
                    $('#app').app('end_busy');
                });
            });
        }
    };

    $.fn.breadcrumbs = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.breadcrumbs');
        }
    };
}(jQuery));
