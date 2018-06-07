(function($) {
    /**
     * The infoblock jQuery plugin handles the overview map
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                component.on('down.zf.accordion', function(ev, panel) {
                    $('#tracking').tracking('track', {'action': 'show-note', 'note': component.find('#' + panel.attr('id') + '-label').html()});
                });
                component.on('up.zf.accordion', function(ev, panel) {
                    $('#tracking').tracking('track', {'action': 'hide-note', 'note': component.find('#' + panel.attr('id') + '-label').html()});
                });
            });
        },
        fetch(url) {
            return this.each(function() {
                var component = $(this);
                $('#app').app('start_busy');
                var promise = $.ajax(url);
                promise.then(function(data) {
                    component.empty();
                    component.append($(data));
                    component.find('.accordion').foundation();
                    $('#app').app('end_busy');
                });
            });
        }
    };

    $.fn.infoblock = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.infoblock');
        }
    };
}(jQuery));
