import configparser,hashlib,importlib.util,json,posixpath,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lock_android_manifest',ROOT/'scripts/lock_android_manifest.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ManifestLock(unittest.TestCase):
 def test_recorded_platform_is_fully_pinned_to_superproject(self):
  evidence=ROOT/'evidence/android-integration-source'
  links=json.loads((evidence/'superproject-gitlinks.json').read_text())['gitlinks']
  raw=(ROOT/'projects/firetabs-android/android-integration/platform-locked.xml').read_bytes();root=ET.fromstring(raw)
  projects={p.get('path',p.get('name')):p.get('revision') for p in root.findall('project')}
  self.assertEqual(projects,links);self.assertEqual(len(projects),1087)
  result=json.loads((evidence/'source-readiness-result.json').read_text());self.assertEqual(hashlib.sha256(raw).hexdigest(),result['locked_manifest_sha256'])
  modules=configparser.ConfigParser(interpolation=None);modules.read(evidence/'upstream/superproject/.gitmodules')
  identities={modules.get(section,'path'):posixpath.normpath('platform/superproject/'+modules.get(section,'url')) for section in modules.sections()}
  for project in root.findall('project'):self.assertEqual(project.get('name'),identities[project.get('path',project.get('name'))])
  captures=json.loads((evidence/'critical-source-lock.json').read_text())['projects']
  for project in captures:
   for source in project.get('files',[]):
    if source['status']=='captured':self.assertEqual(hashlib.sha256((evidence/'upstream'/project['path']/source['path']).read_bytes()).hexdigest(),source['sha256'])
  for index in ['additional-source-inputs.json','graphics-build-inputs.json']:
   for source in json.loads((evidence/index).read_text()):
    if source['status']=='captured':self.assertEqual(hashlib.sha256((evidence/'upstream'/source['project_path']/source['path']).read_bytes()).hexdigest(),source['sha256'])

 def test_resolver_rejects_missing_or_extra_gitlinks(self):
  xml=b'<manifest><remote name="aosp" fetch=".."/><default revision="main"/><project name="platform/core" path="system/core"/></manifest>'
  for links in [{},{'system/core':'a'*40,'extra':'b'*40},{'system/core':'main'}]:
   with self.assertRaises(ValueError):module.resolve(xml,links)
 def test_resolver_does_not_leave_a_moving_default_revision(self):
  raw=module.resolve(b'<manifest><remote name="aosp" fetch=".."/><default revision="main"/><project name="platform/core" path="system/core"/></manifest>',{'system/core':'a'*40})
  root=ET.fromstring(raw);self.assertIsNone(root.find('default').get('revision'));self.assertEqual(root.find('remote').get('fetch'),'https://android.googlesource.com')
 def test_unflattened_include_is_not_silently_ignored(self):
  with self.assertRaises(ValueError):module.resolve(b'<manifest><default/><include name="other.xml"/></manifest>',{})
