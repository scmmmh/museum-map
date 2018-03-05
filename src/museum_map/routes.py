def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')
    config.add_route('explore', '/explore/{gid}')
    config.add_route('infoblock', '/explore/{gid}/infoblock')
    config.add_route('items', '/explore/{gid}/items')
    config.add_route('breadcrumbs', '/explore/{gid}/breadcrumbs')
    config.add_route('overview', '/overview')
    config.add_route('image', '/images/{iid}')
