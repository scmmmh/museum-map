(function($) {
    /**
     * The overview jQuery plugin handles the overview map
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                component.on('click', 'a', function(ev) {
                    ev.preventDefault();
                    $('#app').app('load', $(this).attr('href'));
                });
                component.on('mouseover', 'a', function(ev) {
                    var link = $(this);
                    if(link.attr('id')) {
                        component.find("a[data-room='" + link.attr('id') + "'], ul[data-room='" + link.attr('id') + "']").addClass('is-hovering');
                        $('#tracking').gdpr_tracking('track', {'action': 'overview-hover-in', 'rid': link.attr('id')});
                    } else if(link.data('room')) {
                        component.find("a#" + link.data('room') + ", ul[data-room='" + link.data('room') + "']").addClass('is-hovering');
                        $('#tracking').gdpr_tracking('track', {'action': 'overview-hover-in', 'rid': link.data('room')});
                    }
                });
                component.on('mouseout', 'a', function(ev) {
                    var link = $(this);
                    if(link.attr('id')) {
                        component.find("a[data-room='" + link.attr('id') + "'], ul[data-room='" + link.attr('id') + "']").removeClass('is-hovering');
                        $('#tracking').gdpr_tracking('track', {'action': 'overview-hover-out', 'rid': link.attr('id')});
                    } else if(link.data('room')) {
                        component.find("a#" + link.data('room') + ", ul[data-room='" + link.data('room') + "']").removeClass('is-hovering');
                        $('#tracking').gdpr_tracking('track', {'action': 'overview-hover-out', 'rid': link.data('room')});
                    }
                });
                $(window).on('resize', function() {
                    component.overview('load');
                });
            }).overview('load');
        },
        load() {
            return this.each(function() {
                var component = $(this);
                var promise = $.ajax(component.data('src'), {
                    data: {width: this.getBoundingClientRect().width / (window.innerWidth >= 1024 ? 3 : 2) - 30}
                });
                $('#app').app('start_busy');
                promise.then(function(data) {
                    component.empty();
                    component.append($(data).children());
                    var path = document.location.href.split('/');
                    component.overview('highlight', path[path.length - 1]);
                    $('#app').app('end_busy');
                });
            });
        },
        highlight(iid) {
            return this.each(function() {
                var component = $(this);
                component.find('a.is-active').removeClass('is-active');
                component.find('a#room-' + iid).addClass('is-active');
                component.find("a[data-room='room-" + iid + "']").addClass('is-active');
                component.find("a[data-room='room-" + iid + "']").parents('.floor').find('h3 a').addClass('is-active');
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
