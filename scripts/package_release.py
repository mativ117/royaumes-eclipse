"""Package the current editable project; preserve older releases separately.

The complete repository (including historical ZIPs) is available through GitHub's
generated source archive. Duplicating its history into every new release grows
past GitHub's 100 MiB per-file limit and is unnecessary for playing/editing it.
"""
from pathlib import Path
import base64
import hashlib
import json
import os
import zipfile

from html_security import secure_html

ROOT = Path(__file__).resolve().parents[1]
MAX_PACKAGE_BYTES = 95_000_000  # Leave headroom below GitHub's hard 100 MiB limit.
SOURCE_ARCHIVE = 'https://github.com/mativ117/royaumes-eclipse/archive/refs/heads/main.zip'


def release_path(version):
    return ROOT / 'historique/livraisons-zip' / f'royaumes-eclipse-{version}-projet.zip'


def project_files():
    files = []
    for folder in ['src', 'docs', 'assets', 'vendor', 'scripts', 'tests', 'design']:
        files.extend(f for f in (ROOT / folder).rglob('*')
                     if f.is_file() and '__pycache__' not in f.parts
                     and not f.name.endswith(('.blend1', '.blend2', '.pyc')))
    for name in ['AGENTS.md', 'README.md', 'VERSION', 'index.html',
                 'cathedrale-v03.html', '.nojekyll', '.gitignore']:
        if (ROOT / name).exists():
            files.append(ROOT / name)
    return sorted(set(files))


def write(z, name, data):
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def package_release():
    version = (ROOT / 'VERSION').read_text().strip()
    html = (ROOT / 'docs/index.html').read_text()
    built = json.loads((ROOT / 'docs/version.json').read_text())
    assert built['version'] == version, 'Run scripts/build.py before packaging'
    model_files = sorted((ROOT / 'assets/characters').glob('*.glb'))
    for f in model_files:
        assert hashlib.sha256(f.read_bytes()).hexdigest() == built['models'][f.name], (
            f'{f.name} changed since build; rebuild after all asset exports finish')

    models = {f.stem: base64.b64encode(f.read_bytes()).decode() for f in model_files}
    start = html.index('const ROYAUMES_CHARACTER_DATA=')
    end = html.index(';\n', start) + 1
    snapshot = html[:start] + 'const ROYAUMES_CHARACTER_DATA=' + json.dumps(
        models, separators=(',', ':')) + ';' + html[end:]
    icon = base64.b64encode((ROOT / 'docs/favicon.svg').read_bytes()).decode()
    snapshot = snapshot.replace('href="./favicon.svg"',
                                'href="data:image/svg+xml;base64,' + icon + '"')
    snapshot = secure_html(snapshot)  # Script changed: its original CSP hash is stale.
    history = ROOT / 'historique'
    history.mkdir(exist_ok=True)
    (history / f'royaumes-v{version}.html').write_text(snapshot)

    output = release_path(version)
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix('.zip.tmp')
    files = project_files()
    manifest = {
        'version': version,
        'scope': 'Current playable and editable project; historical snapshots and ZIPs excluded',
        'history': SOURCE_ARCHIVE,
        'launch': 'python -m http.server 8000 --directory docs',
        'files': [
            {'file': f.relative_to(ROOT).as_posix(), 'bytes': f.stat().st_size,
             'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files
        ],
    }
    try:
        with zipfile.ZipFile(temporary, 'w') as z:
            for f in files:
                write(z, f.relative_to(ROOT).as_posix(), f.read_bytes())
            write(z, 'PAQUET.json', (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode())
        if temporary.stat().st_size > MAX_PACKAGE_BYTES:
            raise RuntimeError('Project package exceeds 95 MB; no existing ZIP was overwritten. '
                               'Use GitHub generated source archive for the complete repository.')
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    inventory = [
        {'file': f.relative_to(ROOT).as_posix(), 'bytes': f.stat().st_size,
         'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
        for f in sorted(history.rglob('*'))
        if f.is_file() and f.name != 'INVENTAIRE.json'
    ]
    (history / 'INVENTAIRE.json').write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n')
    print(f'Packaged {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes); '
          f'{len(models)} embedded historical models. Full repository/history: {SOURCE_ARCHIVE}')


if __name__ == '__main__':
    package_release()
