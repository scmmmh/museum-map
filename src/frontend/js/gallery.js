(function($) {
    function setLastMarkers(component) {
        var y = undefined;
        var previous = undefined;
        component.children('li.item').each(function() {
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
            var top = component.parent()[0].scrollTop;
            var bottom = top + component.parent()[0].offsetHeight + 200;
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
     * The gallery jQuery plugin handles interaction with the gallery interface
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                setLastMarkers(component);
                component.find('li.item img').on('load', function() {
                    setLastMarkers(component);
                });
                dynamicLoad(component);
                component.parent().on('scroll', function() {
                    dynamicLoad(component);
                });
                $(window).on('resize', function() {
                    dynamicLoad(component);
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
                component.on('click', 'li.item a', function(ev) {
                    ev.preventDefault();
                    var item = $(this).parent();
                    var details = component.find('#' + item.data('details'));
                    if (currentDetails == details.attr('id')) {
                        item.removeClass('selected');
                        details.slideUp({done: function() {dynamicLoad(component);}});
                        currentDetails = null;
                        currentMarker = null;
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
                            if (marker[0].offsetTop < component.parent()[0].scrollTop) {
                                component.parent().animate({scrollTop: marker[0].offsetTop - 50});
                            } else if (marker[0].offsetTop > component.parent()[0].scrollTop + component.parent()[0].offsetHeight / 2 - 200) {
                                if (currentDetails) {
                                    component.parent().animate({scrollTop: marker[0].offsetTop - component.parent()[0].offsetHeight / 2 - 50});
                                } else {
                                    component.parent().animate({scrollTop: marker[0].offsetTop - 50});
                                }
                            }
                        }
                        currentDetails = details.attr('id');
                        currentMarker = marker.attr('id');
                    }
                });
            });
        }
    };

    $.fn.gallery = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.gallery');
        }
    };
}(jQuery));
