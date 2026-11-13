#!/usr/bin/env python3
"""Extract a downloaded package into a fresh directory, with traversal/link rejection."""
import argparse,pathlib,tarfile,zipfile,shutil,stat

def main():
    ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('destination');a=ap.parse_args()
    dest=pathlib.Path(a.destination).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):raise ValueError('Destination is not empty; use a fresh source-revision folder')
    archive=pathlib.Path(a.archive).expanduser().resolve()
    def target(name):
        p=pathlib.PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('Unsafe archive path: '+name)
        return dest.joinpath(*p.parts)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():
                target(m.filename)
                if stat.S_ISLNK(m.external_attr>>16):raise ValueError('Archive symlink: '+m.filename)
            dest.mkdir(parents=True,exist_ok=True)
            for m in z.infolist():
                p=target(m.filename)
                if m.is_dir():p.mkdir(parents=True,exist_ok=True)
                else:
                    p.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(m) as src,p.open('wb') as out:shutil.copyfileobj(src,out)
    else:
        with tarfile.open(archive) as t:
            members=t.getmembers()
            for m in members:
                target(m.name)
                if not (m.isdir() or m.isfile()):raise ValueError('Archive links/devices are not supported: '+m.name)
            dest.mkdir(parents=True,exist_ok=True)
            for m in members:
                p=target(m.name)
                if m.isdir():p.mkdir(parents=True,exist_ok=True)
                else:
                    p.parent.mkdir(parents=True,exist_ok=True)
                    with t.extractfile(m) as src,p.open('wb') as out:shutil.copyfileobj(src,out)
    print(dest)
if __name__=='__main__':main()
