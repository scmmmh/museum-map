(function($) {
    var CORRIDOR_SIZE = 5;
    var COLOURS = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd'];

    function click(ev) {
        $('article').app('load', ev.target._url);
    }

    function cmpItems(a, b) {
        return b.data('size') - a.data('size');
    }

    function shuffleArray(array) {
        for (var i = array.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = array[i];
            array[i] = array[j];
            array[j] = temp;
        }
    }

    function addShape(stage, x, y, width, height, item, colour) {
        var shape = new createjs.Shape();
        shape.graphics.beginStroke('black').beginFill(colour).drawRect(0, 0, width, height);
        shape.x = x;
        shape.y = y;
        shape.cursor = 'pointer';
        shape._url = item.children('a').attr('href');
        stage.addChild(shape);
        shape.addEventListener('click', click);
    }

    function addLabel(stage, x, y, width, height, item, fontSize, fontColour) {
        var text = new createjs.Text(item.children('a').html(), fontSize + "px 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif", fontColour);
        if (text.getMetrics().width >= width - 20) {
            var tokens = item.children('a').html().split(' ');
            var splitText = tokens[0];
            for (var idx = 1; idx < tokens.length; idx++) {
                text = new createjs.Text(splitText + ' ' + tokens[idx], fontSize + "px 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif", fontColour);
                if (text.getMetrics().width >= width - 20) {
                    splitText = splitText + '\n' + tokens[idx];
                } else {
                    splitText = splitText + ' ' + tokens[idx];
                }
            }
            text = new createjs.Text(splitText, fontSize + "px 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif", fontColour);
        }
        text.x = x + width / 2 - text.getMetrics().width / 2;
        text.y = y + height / 2 - text.getMetrics().height / 2;
        stage.addChild(text);
    }

    function renderRoom(stage, item, x, y, width, height, colour) {
        var items = item.children('ul').children('li').get().map(function(item) { return $(item); });
        items.sort(cmpItems);
        var rect = {x: x, y: y, width: width, height: height};
        var split_direction = 1;
        while (items.length > 1) {
            var head = items[0].data('size');
            var rest = items.slice(1).reduce(function(accumulator, current) {
                if (typeof accumulator === 'number') {
                    return accumulator + current.data('size');
                } else {
                    return accumulator.data('size') + current.data('size');
                }});
            if (typeof rest !== 'number') {
                rest = rest.data('size');
            }
            if (split_direction === 1) {
                addShape(stage, rect.x, rect.y, rect.width / (head + rest) * head, rect.height, items[0], colour);
                addLabel(stage, rect.x, rect.y, rect.width / (head + rest) * head, rect.height, items[0], 12, '#222');
                rect = {x: rect.x + rect.width / (head + rest) * head, y: rect.y, width: rect.width / (head + rest) * rest, height: rect.height}
                split_direction = 2;
            } else {
                addShape(stage, rect.x, rect.y, rect.width, rect.height / (head + rest) * head, items[0], colour);
                addLabel(stage, rect.x, rect.y, rect.width, rect.height / (head + rest) * head, items[0], 12, '#222');
                rect = {x: rect.x, y: rect.y + rect.height / (head + rest) * head, width: rect.width, height: rect.height / (head + rest) * rest}
                split_direction = 1;
            }
            items = items.slice(1);
        }
        addShape(stage, rect.x, rect.y, rect.width, rect.height, items[0], colour);
        addLabel(stage, rect.x, rect.y, rect.width, rect.height, items[0], 12, '#222');
    }

    function renderFloor(stage, item, y, width) {
        var title = new createjs.Text(item.children('a').html(), "16px 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif");
        title.x = 20;
        title.y = y;
        stage.addChild(title);
        y = y + title.getMetrics().height + 5;
        var floor = new createjs.Shape();
        floor.graphics.beginStroke("black").drawRect(0, 0, width, width / 3);
        floor.x = 20;
        floor.y = y;
        stage.addChild(floor);
        var items = item.children('ul').children('li').get().map(function(item) { return $(item); });
        items.sort(cmpItems);
        var rect = {x: 20, y: y, width: width, height: width / 3};
        var split_direction = 1;
        var colours = COLOURS.slice(0);
        shuffleArray(colours);
        while (items.length > 1) {
            var head = items[0].data('size');
            var rest = items.slice(1).reduce(function(accumulator, current) {
                if (typeof accumulator === 'number') {
                    return accumulator + current.data('size');
                } else {
                    return accumulator.data('size') + current.data('size');
                }});
            if (typeof rest !== 'number') {
                rest = rest.data('size');
            }
            if (split_direction === 1) {
                addShape(stage, rect.x, rect.y, rect.width / (head + rest) * head - CORRIDOR_SIZE, rect.height, items[0], colours[0]);
                if (items[0].find('> ul > li').length > 0) {
                    renderRoom(stage, items[0], rect.x, rect.y, rect.width / (head + rest) * head - CORRIDOR_SIZE, rect.height, colours[0]);
                }
                addLabel(stage, rect.x, rect.y, rect.width / (head + rest) * head - CORRIDOR_SIZE, rect.height, items[0], 14, '#222');
                rect = {x: rect.x + rect.width / (head + rest) * head + CORRIDOR_SIZE, y: rect.y, width: rect.width / (head + rest) * rest - CORRIDOR_SIZE, height: rect.height}
                split_direction = 2;
            } else {
                addShape(stage, rect.x, rect.y, rect.width, rect.height / (head + rest) * head - CORRIDOR_SIZE, items[0], colours[0]);
                if (items[0].find('> ul > li').length > 0) {
                    renderRoom(stage, items[0], rect.x, rect.y, rect.width, rect.height / (head + rest) * head - CORRIDOR_SIZE, colours[0]);
                }
                addLabel(stage, rect.x, rect.y, rect.width, rect.height / (head + rest) * head - CORRIDOR_SIZE, items[0], 14, '#222');
                rect = {x: rect.x, y: rect.y + rect.height / (head + rest) * head + CORRIDOR_SIZE, width: rect.width, height: rect.height / (head + rest) * rest - CORRIDOR_SIZE}
                split_direction = 1;
            }
            items = items.slice(1);
            colours = colours.slice(1);
        }
        addShape(stage, rect.x, rect.y, rect.width, rect.height, items[0], colours[0]);
        if (items[0].find('> ul > li').length > 0) {
            renderRoom(stage, items[0], rect.x, rect.y, rect.width, rect.height, colours[0]);
        }
        addLabel(stage, rect.x, rect.y, rect.width, rect.height, items[0], 14, '#222');
        return y + width / 3;
    }
    /**
     * The overview jQuery plugin handles the overview map
     */
    var methods = {
        init : function(options) {
            return this.each(function() {
                var component = $(this);
                component.find('ul').hide();
                var clientWidth = component[0].clientWidth - 30;
                var clientHeight = component[0].clientHeight;
                var stage = new createjs.Stage(component.children('canvas')[0]);
                stage.enableMouseOver(10);
                stage.canvas.width = clientWidth;
                var y = 10;
                component.children('ul').children('li').each(function(idx) {
                    y = renderFloor(stage, $(this), y, clientWidth - 100) + 20;
                });
                stage.canvas.height = y;
                /*var floor = new createjs.Shape();
                floor.graphics.beginStroke("black").drawRect(0, 0, clientWidth - 100, (clientWidth - 100) / 3);
                floor.x = 50;
                floor.y = 100;
                stage.addChild(floor);
                var sizes = [88, 90, 12, 6];
                var rect = {x: 50, y: 100, width: clientWidth - 100, height: (clientWidth - 100) / 3};
                var split_direction = 1;
                var CORRIDOR_SIZE = 5;
                while (sizes.length > 1) {
                    var head = sizes[0];
                    var rest = sizes.slice(1).reduce(function(accumulator, current) { return accumulator + current });
                    console.log(head + ' / ' + rest);
                    if (split_direction === 1) {
                        var sector = new createjs.Shape();
                        sector.graphics.beginStroke('black').drawRect(0, 0, rect.width / (head + rest) * head - CORRIDOR_SIZE, rect.height);
                        sector.x = rect.x;
                        sector.y = rect.y;
                        stage.addChild(sector);
                        rect = {x: rect.x + rect.width / (head + rest) * head + CORRIDOR_SIZE, y: rect.y, width: rect.width / (head + rest) * rest - CORRIDOR_SIZE, height: rect.height}
                        split_direction = 2;
                    } else {
                        var sector = new createjs.Shape();
                        sector.graphics.beginStroke('black').drawRect(0, 0, rect.width, rect.height / (head + rest) * head - 5);
                        sector.x = rect.x;
                        sector.y = rect.y;
                        stage.addChild(sector);
                        rect = {x: rect.x, y: rect.y + rect.height / (head + rest) * head + CORRIDOR_SIZE, width: rect.width, height: rect.height / (head + rest) * rest - CORRIDOR_SIZE}
                        split_direction = 1;
                    }
                    sizes = sizes.slice(1);
                }
                var sector = new createjs.Shape();
                sector.graphics.beginStroke('black').drawRect(0, 0, rect.width, rect.height);
                sector.x = rect.x;
                sector.y = rect.y;
                stage.addChild(sector);*/
                stage.update();
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
