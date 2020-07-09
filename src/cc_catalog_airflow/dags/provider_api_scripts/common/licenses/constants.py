_SIMPLE_LICENSE_PATHS = [
    # This list holds recognized license URL path snippets that split
    # correctly into license_ and license_version
    'licenses/by/1.0',
    'licenses/by/2.0',
    'licenses/by/2.1/au',
    'licenses/by/2.1/es',
    'licenses/by/2.1/jp',
    'licenses/by/2.5',
    'licenses/by/3.0',
    'licenses/by/4.0',

    'licenses/by-nc/1.0',
    'licenses/by-nc/2.0',
    'licenses/by-nc/2.1/au',
    'licenses/by-nc/2.1/es',
    'licenses/by-nc/2.1/jp',
    'licenses/by-nc/2.5',
    'licenses/by-nc/3.0',
    'licenses/by-nc/4.0',

    'licenses/by-nc-nd/2.0',
    'licenses/by-nc-nd/2.1/au',
    'licenses/by-nc-nd/2.1/es',
    'licenses/by-nc-nd/2.1/jp',
    'licenses/by-nc-nd/2.5',
    'licenses/by-nc-nd/3.0',
    'licenses/by-nc-nd/4.0',

    'licenses/by-nc-sa/1.0',
    'licenses/by-nc-sa/2.0',
    'licenses/by-nc-sa/2.1/au',
    'licenses/by-nc-sa/2.1/es',
    'licenses/by-nc-sa/2.1/jp',
    'licenses/by-nc-sa/2.5',
    'licenses/by-nc-sa/3.0',
    'licenses/by-nc-sa/4.0',

    'licenses/by-nd/1.0',
    'licenses/by-nd/2.0',
    'licenses/by-nd/2.1/au',
    'licenses/by-nd/2.1/es',
    'licenses/by-nd/2.1/jp',
    'licenses/by-nd/2.5',
    'licenses/by-nd/3.0',
    'licenses/by-nd/4.0',

    'licenses/by-sa/1.0',
    'licenses/by-sa/2.0',
    'licenses/by-sa/2.1/au',
    'licenses/by-sa/2.1/es',
    'licenses/by-sa/2.1/jp',
    'licenses/by-sa/2.5',
    'licenses/by-sa/3.0',
    'licenses/by-sa/4.0',

    'licenses/devnations/2.0',

    'licenses/nc/1.0',
    'licenses/nc/2.0/jp',

    'licenses/nc-sa/1.0',
    'licenses/nc-sa/2.0/jp',

    'licenses/nc-sampling+/1.0',

    'licenses/nd/1.0',
    'licenses/nd/2.0/jp',

    'licenses/nd-nc/1.0',
    'licenses/nd-nc/2.0/jp',

    'licenses/sa/1.0',
    'licenses/sa/2.0/jp',

    'licenses/sampling+/1.0',
    'licenses/sampling/1.0',
]

LICENSE = 'license'
VERSION = 'version'
NO_VERSION = 'N/A'


_SPECIAL_CASE_LICENSE_PATHS = {
    # This dictionary holds recognized path snippets for which we must
    # set the license and/or version manually
    'licenses/by-nd-nc/1.0': {LICENSE: 'by-nc-nd', VERSION: '1.0'},
    'licenses/by-nd-nc/2.0/jp': {LICENSE: 'by-nc-nd', VERSION: '2.0'},
    'licenses/publicdomain': {LICENSE: 'publicdomain', VERSION: NO_VERSION},

    'licenses/mark/1.0': {LICENSE: 'pdm', VERSION: '1.0'},
    'publicdomain/mark/1.0': {LICENSE: 'pdm', VERSION: '1.0'},

    'publicdomain/zero/1.0': {LICENSE: 'cc0', VERSION: '1.0'},
}


def _get_license_path_map():
    license_path_map = {
        path: {LICENSE: path.split('/')[1], VERSION: path.split('/')[2]}
        for path in _SIMPLE_LICENSE_PATHS
    }
    license_path_map.update(_SPECIAL_CASE_LICENSE_PATHS)
    return license_path_map


LICENSE_PATH_MAP = _get_license_path_map()
