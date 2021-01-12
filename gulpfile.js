'use strict';

const gulp = require('gulp'),
      { spawn } = require('child_process');

gulp.task('develop', (cb) => {
    const builder = spawn('yarn', ['build', '--mode', 'development', '--watch', '--dest', '../museum_map/static'], {
        cwd: 'src/frontend',
        stdio: 'inherit',
    });
    builder.on('exit', cb);
});

gulp.task('default', (cb) => {
    const builder = spawn('yarn', ['build', '--mode', 'production', '--dest', '../museum_map/static'], {
        cwd: 'src/frontend',
        stdio: 'inherit',
    });
    builder.on('exit', cb);
});
