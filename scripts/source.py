from datetime import datetime, timezone
import csv
import gzip
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from urllib.request import Request, urlopen
from zipfile import ZipFile
import sys

ROOT = Path(__file__).resolve().parents[1]
TABLE = 'https://www150.statcan.gc.ca/n1/tbl/csv/{code}-eng.zip'
def rows(code, url=None, profile=False):
    url = url or TABLE.format(code=code)
    # A local copy is useful when validating a new table layout.
    if len(sys.argv) == 3 and sys.argv[1] == '--source-dir':
        source = Path(sys.argv[2]) / code
    else:
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers={'User-Agent': 'CoolCode source verification contact coolcode.ca'}), timeout=160) as response:
                    source = io.BytesIO(response.read())
                break
            except OSError:
                if attempt == 2:
                    raise
                sleep(2 ** attempt)
    with ZipFile(source) as archive:
        name = next(n for n in archive.namelist() if n.endswith('_data.csv')) if profile else code + '.csv'
        with archive.open(name) as data, io.TextIOWrapper(data, encoding='utf-8-sig', errors='strict' if not profile else 'replace') as text:
            yield from csv.reader(text)

def publish(data, status):
    target = ROOT / 'web/data'
    target.mkdir(exist_ok=True)
    status['retrieved'] = datetime.now(timezone.utc).date().isoformat()
    body = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
    with TemporaryDirectory(dir=target) as tmp:
        snap = Path(tmp) / 'edition.json.gz'
        snap.write_bytes(gzip.compress(body, compresslevel=9, mtime=0))
        meta = Path(tmp) / 'status.json'
        meta.write_text(json.dumps(status, ensure_ascii=False, indent=2)+'\n')
        snap.replace(target / snap.name)
        meta.replace(target / meta.name)
    print(json.dumps(status, ensure_ascii=False))
