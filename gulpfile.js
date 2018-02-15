'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var babel = require('gulp-babel');
var pump = require('pump');

gulp.task('default', ['scss']);

gulp.task('scss', function(cb) {
    pump([
        gulp.src('src/frontend/scss/application.scss'),
        sass({
            includePaths: [
                'node_modules/foundation-sites/scss',
                'node_modules/foundation-sites/_vendor'
            ]
        }),
        gulp.dest('src/museum_map/static')
    ], cb);
});

// Task to watch the SCSS/JS files and re-build when needed
gulp.task('watch', function() {
});
