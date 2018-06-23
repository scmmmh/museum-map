(function($) {
    function setLastMarkers(component) {
        var y = undefined;
        var previous = undefined;
        component.find('li.item').each(function() {
            var top = this.getBoundingClientRect().top;
            if (y !== top) {
                if (previous) {
                    $(previous).addClass('last');
                }
                y = top;
            } else {
                $(previous).removeClass('last');
            }
            previous = this;
        }).last().addClass('last');
    }

    function dynamicLoad(component) {
        if (component.parent().length > 0) {
            var top = component[0].scrollTop;
            var bottom = top + component[0].offsetHeight + 200;
            component.find('li.item picture.pre-load').each(function() {
                var picture = $(this);
                var itemTop = picture.parents('li.item')[0].offsetTop;
                if (top <= itemTop + 200 && itemTop <= bottom) {
                    picture.prepend('<source srcset="' + picture.data('src') + '"/>').removeClass('pre-load');
                }
            });
        }
    }
    /**
     * The items jQuery plugin handles interaction with the items interface
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                $(window).on('resize', function() {
                    dynamicLoad(component);
                });
                component.on('scroll', function() {
                    dynamicLoad(component);
                });
                component.on('click', 'li.room > h2 > a', function(ev) {
                    ev.preventDefault();
                    $('#app').app('load', $(this).attr('href'));
                })
                var currentDetails = null;
                var currentMarker = null;
                component.on('click', '.close a', function(ev) {
                    ev.preventDefault();
                    component.find('.selected').removeClass('selected');
                    $(this).parents('.details').slideUp();
                    currentDetails = null;
                    currentMarker = null;
                });
                // Track mouse movement
                component.on('mouseover', 'li.item', function(ev) {
                    $('#tracking').gdpr_tracking('track', {'action': 'item-hover-in', 'iid': $(this).attr('id')});
                });
                component.on('mouseout', 'li.item', function(ev) {
                    $('#tracking').gdpr_tracking('track', {'action': 'item-hover-out', 'iid': $(this).attr('id')});
                });
                component.on('mouseover', 'li.item > a > span', function(ev) {
                    $('#tracking').gdpr_tracking('track', {'action': 'item-hover-in', 'iid': $(this).parent().parent().attr('id')});
                });
                component.on('mouseout', 'li.item > a > span', function(ev) {
                    $('#tracking').gdpr_tracking('track', {'action': 'item-hover-out', 'iid': $(this).parent().parent().attr('id')});
                });
                component.on('click', 'li.item a', function(ev) {
                    ev.preventDefault();
                    var item = $(this).parent();
                    var details = component.find('#' + item.data('details'));
                    if (currentDetails == details.attr('id')) {
                        item.removeClass('selected');
                        details.slideUp({done: function() {dynamicLoad(component);}});
                        currentDetails = null;
                        currentMarker = null;
                        $('#tracking').gdpr_tracking('track', {'action': 'hide-item', 'iid': details.attr('id')});
                    } else {
                        var picture = details.find('picture.pre-load');
                        picture.prepend('<source srcset="' + picture.data('src') + '"/>').removeClass('pre-load');
                        component.find('.selected').removeClass('selected');
                        item.addClass('selected');
                        var left = item[0].offsetLeft + item[0].offsetWidth / 2 - 15;
                        if (item.hasClass('last')) {
                            var marker = item;
                        } else {
                            var marker = item.nextAll('.last').first();
                        }
                        details.children('.marker').css('padding-left', left + 'px');
                        details.insertAfter(marker);
                        if (currentMarker == marker.attr('id')) {
                            $('#' + currentDetails).slideUp(0);
                            details.slideDown(0);
                        } else {
                            if (currentDetails) {
                                $('#' + currentDetails).slideUp({done: function() {dynamicLoad(component);}});
                            }
                            details.slideDown();
                            var markerTop = marker[0].offsetTop
                            if(marker.parents('.room').length > 0) {
                                markerTop = markerTop + marker.parents('.room')[0].offsetTop;
                            }
                            if (markerTop < component[0].scrollTop) {
                                component.animate({scrollTop: markerTop - 50});
                            } else if (markerTop > component[0].scrollTop + component[0].offsetHeight / 2 - 200) {
                                if (currentDetails) {
                                    component.animate({scrollTop: markerTop - component[0].offsetHeight / 2 - 50});
                                } else {
                                    component.animate({scrollTop: markerTop - 50});
                                }
                            }
                        }
                        currentDetails = details.attr('id');
                        currentMarker = marker.attr('id');
                        $('#tracking').gdpr_tracking('track', {'action': 'show-item', 'iid': details.attr('id')});
                    }
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
                    component.find('li.item img').on('load', function() {
                        setLastMarkers(component);
                    });
                    dynamicLoad(component);
                    component.parent().on('scroll', function() {
                        dynamicLoad(component);
                    });
                    $('#app').app('end_busy');
                });
            });
        }
    };

    $.fn.items = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.items');
        }
    };
}(jQuery));
