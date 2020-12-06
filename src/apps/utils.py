import os


def load_webpack_configurations(base_dir, debug=False):

    configs = {}
    builds_dir = os.path.join(base_dir, "apps", "static", "builds")

    for package in os.scandir(builds_dir):
        if not package.is_dir():
            continue
        package_dir = os.path.join(builds_dir, package.name)
        for version in os.scandir(package_dir):
            if not version.is_dir():
                continue
            configs["{}-{}".format(package.name.upper(), version.name.upper())] = {
                'CACHE': not debug,
                'BUNDLE_DIR_NAME': '/apps/app/',  # must end with slash
                'STATS_FILE': os.path.join(
                    package_dir,
                    version.name,
                    "{}-{}.webpack-stats.json".format(package.name, version.name)
                ),
            }

    return configs
