import json


def get_project_version(package_path):
    with open(package_path) as package_file:
        package = json.load(package_file)
        return package["version"]
