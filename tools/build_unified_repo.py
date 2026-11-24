import pathlib, zipfile, hashlib, urllib.request, xml.etree.ElementTree as ET
root=pathlib.Path('repo')
index=ET.parse(root/'addons.xml').getroot()
upstream='https://raw.githubusercontent.com/jurialmunkey/repository.jurialmunkey/master/omega/zips/'
remote=ET.fromstring(urllib.request.urlopen(upstream+'addons.xml',timeout=40).read())
local={a.get('id'):a for a in index.findall('addon')}
available={a.get('id'):a for a in remote.findall('addon')}
missing=set()
seen=set()
def visit(a):
    aid=a.get('id')
    if aid in seen: return
    seen.add(aid)
    for dep in a.findall('requires/import'):
        d=dep.get('addon')
        if dep.get('optional')=='true' or d.startswith(('xbmc.','kodi.')): continue
        if d in local: visit(local[d])
        elif d in available: visit(available[d])
        else: missing.add((d,dep.get('version')))
visit(local['skin.madnoxnova'])
print('Unresolved locally or upstream (may be in official Kodi repo):',sorted(missing))
out=pathlib.Path('dist')
out.mkdir(exist_ok=True)
rid='repository.titaniumx.unified'
manifest=ET.Element('addon',id=rid,name='Titanium X Unified Repository',version='0.1.0',**{'provider-name':'Titanium X'})
ext=ET.SubElement(manifest,'extension',point='xbmc.addon.repository')
for base in ['https://prestigelandscapegroupswfl.github.io/kaleido-build/repo/',upstream]:
    d=ET.SubElement(ext,'dir',minversion='21.0.0',maxversion='21.9.99')
    for tag,suffix in [('info','addons.xml'),('checksum','addons.xml.md5'),('datadir','')]:
        ET.SubElement(d,tag).text=base+suffix
meta=ET.SubElement(manifest,'extension',point='xbmc.addon.metadata')
ET.SubElement(meta,'summary').text='Unified Kodi 21 skin and upstream dependencies'
ET.SubElement(meta,'platform').text='all'
with zipfile.ZipFile(out/(rid+'-0.1.0.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr(rid+'/addon.xml',ET.tostring(manifest,encoding='utf-8',xml_declaration=True))
(out/'dependency-audit.txt').write_text('\n'.join(f'{d} {v}' for d,v in sorted(missing)))
