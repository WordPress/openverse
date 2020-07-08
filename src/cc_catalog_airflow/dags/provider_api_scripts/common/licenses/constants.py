_SIMPLE_LICENSE_PATHS = [
    # This list holds valid license URL path snippets that split
    # correctly into license_ and license_version
    'licenses/by/1.0',
    'licenses/by/2.0',
    'licenses/by/2.5',
    'licenses/by/3.0',
    'licenses/by/4.0',

    'licenses/by-nc/1.0',
    'licenses/by-nc/2.0',
    'licenses/by-nc/2.5',
    'licenses/by-nc/3.0',
    'licenses/by-nc/4.0',

    'licenses/by-nc-nd/1.0',
    'licenses/by-nc-nd/2.0',
    'licenses/by-nc-nd/2.5',
    'licenses/by-nc-nd/3.0',
    'licenses/by-nc-nd/4.0',

    'licenses/by-nc-sa/1.0',
    'licenses/by-nc-sa/2.0',
    'licenses/by-nc-sa/2.5',
    'licenses/by-nc-sa/3.0',
    'licenses/by-nc-sa/4.0',

    'licenses/by-nd/1.0',
    'licenses/by-nd/2.0',
    'licenses/by-nd/2.5',
    'licenses/by-nd/3.0',
    'licenses/by-nd/4.0',

    'licenses/by-sa/1.0',
    'licenses/by-sa/2.0',
    'licenses/by-sa/2.5',
    'licenses/by-sa/3.0',
    'licenses/by-sa/4.0',

    'licenses/sa/1.0',
]

_SPECIAL_CASE_LICENSE_PATHS = {
    # For these paths, we must set the license and/or version manually
    'licenses/by-nd-nc/1.0': {
        # Note the change in order of license tags.
        'license': 'by-nc-nd', 'version': '1.0'
    },
    'publicdomain/zero/1.0': {'license': 'cc0', 'version': '1.0'},
    'publicdomain/mark/1.0': {'license': 'pdm', 'version': '1.0'},
    'licenses/mark/1.0': {'license': 'pdm', 'version': '1.0'},
}


def _get_license_path_map():
    license_path_map = {
        path: {'license': path.split('/')[1], 'version': path.split('/')[2]}
        for path in _SIMPLE_LICENSE_PATHS
    }
    license_path_map.update(_SPECIAL_CASE_LICENSE_PATHS)
    return license_path_map


LICENSE_PATH_MAP = _get_license_path_map()
