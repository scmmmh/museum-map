import re


VERSION = '0.2.3'


def readlines(filename: str) -> list[str]:
    with open(filename) as in_f:
        return in_f.readlines()


def writelines(filename: str, lines: list[str]):
    with open(filename, 'w') as out_f:
        out_f.write(''.join(lines))


def update_version(filename: str, version: str):
    def replace_version(line: str) -> str:
        if 'version' in line:
            return re.sub('[0-9]+\.[0-9]+\.[0-9]+', version, line)
        elif 'museum_map-' in line:
            return re.sub('[0-9]+\.[0-9]+\.[0-9]+', version, line)
        else:
            return line

    writelines(filename, map(replace_version, readlines(filename)))


update_version('package.json', VERSION)
update_version('src/frontend/package.json', VERSION)
update_version('pyproject.toml', VERSION)
update_version('docker/Dockerfile', VERSION)
