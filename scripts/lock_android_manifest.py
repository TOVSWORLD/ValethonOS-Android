#!/usr/bin/env python3
"""Resolve every platform project against one captured superproject gitlink tree."""
import argparse,hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path

def resolve(manifest,gitlinks):
    root=ET.fromstring(manifest)
    if root.findall('include') or root.findall('extend-project') or root.findall('remove-project'):raise ValueError('Flatten manifest before resolution')
    default=root.find('default')
    if default is None:raise ValueError('Manifest default missing')
    default.attrib.pop('revision',None)
    for remote in root.findall('remote'):
        if remote.get('name')!='aosp':raise ValueError('Unexpected remote')
        remote.set('fetch','https://android.googlesource.com')
    paths=set()
    for project in root.findall('project'):
        path=project.get('path') or project.get('name')
        if path in paths:raise ValueError('Duplicate checkout path')
        paths.add(path);revision=gitlinks.get(path,'')
        if not re.fullmatch('[a-f0-9]{40}',revision):raise ValueError(f'Missing immutable gitlink: {path}')
        project.set('revision',revision)
        project.attrib.pop('upstream',None);project.attrib.pop('dest-branch',None)
    if paths!=set(gitlinks):raise ValueError('Manifest/superproject project-set mismatch')
    ET.indent(root,space='  ')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--gitlinks',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    capture=json.loads(a.gitlinks.read_text());result=resolve(a.manifest.read_bytes(),capture['gitlinks']);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
    print(json.dumps({'projects':len(capture['gitlinks']),'superproject_commit':capture['commit'],'sha256':hashlib.sha256(result).hexdigest(),'platform_checkout_performed':False},indent=2))
if __name__=='__main__':main()
