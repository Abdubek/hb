import unittest,json,base64,struct,copy
import test_cli
from normalize import revision

class Meshopt(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def fixtures(self):return test_cli.ROOT/'compat/fixtures/meshopt'
    def test_compressed_and_reference_twins(self):
        for source in sorted(self.fixtures().glob('*-reference.gltf')):
            compressed=source.with_name(source.name.replace('-reference',''));stem=compressed.stem
            self.hb('import',source,'--scene',stem+'-reference.hb');self.hb('import',compressed,'--scene',stem+'.hb')
            self.assertEqual(revision(self.path/(stem+'.hb'))['scene'],revision(self.path/(stem+'-reference.hb'))['scene'],stem)
            self.hb('export',stem+'.glb','--scene',stem+'.hb')
    def test_glb_external_optional_and_untagged_fallbacks(self):
        template=json.loads((self.fixtures()/'none-triangles.gltf').read_text())
        for mode in ('glb','external','untagged','optional','ignored-uri'):
            doc=copy.deepcopy(template);buffer=base64.b64decode(doc['buffers'][0]['uri'].split(',')[1])
            if mode=='untagged':doc['buffers'][1].pop('extensions')
            if mode=='optional':
                doc['extensionsRequired']=['KHR_mesh_quantization'];doc['buffers'][1]['uri']='unused-fallback.bin'
            if mode=='ignored-uri':doc['buffers'][1]['uri']='missing-but-ignored.bin'
            if mode=='external':
                doc['buffers'][0]['uri']='compressed.bin';(self.path/'compressed.bin').write_bytes(buffer)
            if mode=='glb':
                doc['buffers'][0].pop('uri');header=json.dumps(doc).encode();header+=b' '*((-len(header))%4);buffer+=bytes((-len(buffer))%4)
                data=struct.pack('<III',0x46546c67,2,28+len(header)+len(buffer))+struct.pack('<II',len(header),0x4e4f534a)+header+struct.pack('<II',len(buffer),0x004e4942)+buffer
                source=self.path/'input.glb';source.write_bytes(data)
            else:source=self.path/'input.gltf';source.write_text(json.dumps(doc))
            self.hb('run',self.script('import bpy\nbpy.ops.import_scene.gltf(filepath='+repr(str(source))+')'),'--scene',mode+'.hb')
            self.assertEqual(len(revision(self.path/(mode+'.hb'))['scene']['meshes']),1)
    def test_invalid_streams_and_layouts_rollback(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'));before=(self.path/'scene.hb').read_bytes()
        template=json.loads((self.fixtures()/'none-triangles.gltf').read_text());cases=[]
        for key,value in (('mode','BAD'),('filter','COLOR'),('byteStride',3),('count',0),('count',2**63),('byteOffset',2**63),('byteLength',1),('buffer',100)):
            doc=copy.deepcopy(template);doc['bufferViews'][0]['extensions']['EXT_meshopt_compression'][key]=value;cases.append(doc)
        for change in ('oversize','parent-short','source-fallback','uncompressed-fallback','not-required','version'):
            doc=copy.deepcopy(template)
            if change=='oversize':
                view=doc['bufferViews'][0];view['extensions']['EXT_meshopt_compression']['count']=3000000;view['byteLength']=36000000;doc['buffers'][1]['byteLength']=36000012
            if change=='parent-short':doc['buffers'][1]['byteLength']=1
            if change=='source-fallback':doc['bufferViews'][0]['extensions']['EXT_meshopt_compression']['buffer']=1
            if change=='uncompressed-fallback':doc['bufferViews'][0].pop('extensions')
            if change=='not-required':doc['extensionsRequired']=['KHR_mesh_quantization']
            if change=='version':
                data=bytearray(base64.b64decode(doc['buffers'][0]['uri'].split(',')[1]));data[0]=0xa1;doc['buffers'][0]['uri']='data:application/octet-stream;base64,'+base64.b64encode(data).decode()
            cases.append(doc)
        for i,doc in enumerate(cases):
            source=self.path/'bad.gltf';source.write_text(json.dumps(doc));self.hb('import',source,ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before,i)
