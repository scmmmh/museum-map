'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var babel = require('gulp-babel');
var pump = require('pump');
var concat = require('gulp-concat');

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

gulp.task('js', function(cb) {
    pump([
        gulp.src([
            'node_modules/jquery/dist/jquery.js',
            'node_modules/foundation-sites/dist/js/foundation.js',
            'node_modules/easeljs/lib/easeljs.js',
            'src/frontend/js/*.js'
        ]),
        concat('application.js'),
        gulp.dest('src/museum_map/static')
    ], cb);
});

// Task to watch the SCSS/JS files and re-build when needed
gulp.task('watch', ['scss', 'js'], function() {
    gulp.watch('src/frontend/scss/**/*.scss', ['scss']);
    gulp.watch('src/frontend/js/**/*.js', ['js']);
});
