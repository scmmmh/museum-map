import re


VERSION = '0.6.0'


def readlines(filename: str) -> list[str]:
    with open(filename) as in_f:
        return in_f.readlines()


def writelines(filename: str, lines: list[str]):
    with open(filename, 'w') as out_f:
        out_f.write(''.join(lines))


def update_version(filename: str, pattern: str, version: str):
    def replace_version(line: str) -> str:
        if re.match(pattern, line):
            return re.sub('[0-9]+\.[0-9]+\.[0-9]+', version, line)
        else:
            return line

    writelines(filename, map(replace_version, readlines(filename)))


update_version('museum_map/server/frontend/package.json', '^  "version": "[0-9]+\.[0-9]+\.[0-9]",$', VERSION)
update_version('pyproject.toml', '^version = "[0-9]+\.[0-9]+\.[0-9]+"$',  VERSION)
update_version('docker/Dockerfile', '^.*museum_map-[0-9]+\.[0-9]+\.[0-9]+-py3.*$', VERSION)
