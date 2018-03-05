(function($) {
    /**
     * The overview jQuery plugin handles the overview map
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                var promise = $.ajax(component.data('src'), {
                    data: {width: this.getBoundingClientRect().width - 35}
                });
                $('#app').app('start_busy');
                promise.then(function(data) {
                    component.empty();
                    component.append($(data).children());
                    var path = document.location.href.split('/');
                    component.find('a#room-' + path[path.length - 1]).addClass('is-active');
                    component.find('.room-container a').each(function() {
                        var room = $(this);
                        var bbox = this.getBoundingClientRect();
                        var horiz = Math.floor((bbox.width - 12) / 60);
                        var vert = Math.floor((bbox.height - 42) / 60);
                        if(vert * 60 + 42 + 50 <= bbox.height) {
                            vert = vert + 1;
                        }
                        var max_samples = 0;
                        if(horiz > 1 && vert > 1) {
                            max_samples = Math.min(Math.floor((horiz * vert) / 2) * 2, Math.floor(10 / horiz) * horiz);
                        } else if((horiz == 1 && vert >= 1) || (horiz >= 1 && vert == 1)) {
                            max_samples = Math.min(horiz * vert, 10);
                        }
                        var samples = room.data('samples');
                        var sample_container = $('<span class="image-samples"></span>');
                        for(var idx = 0; idx < max_samples; idx++) {
                            sample_container.append('<span class="image-sample"><img src="' + samples[idx] + '"/></span>')
                        }
                        room.append(sample_container);
                    });
                    $('#app').app('end_busy');
                });
                component.on('click', 'a', function(ev) {
                    ev.preventDefault();
                    $('#app').app('load', $(this).attr('href'));
                })
            });
        },
        highlight(iid) {
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
