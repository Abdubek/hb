import unittest,json,zlib,shutil
import test_cli
from normalize import revision
from text_check import compare

class Text(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def font(self):return str(test_cli.ROOT/'compat/fixtures/fonts/DejaVuSans.ttf')
    def test_true_type_glyphs_layout_and_uvs(self):
        refs=[]
        for name in ('reference','layout-reference'):refs+=json.loads(zlib.decompress((test_cli.ROOT/('compat/fixtures/text-'+name+'.json.zlib')).read_bytes()))
        cases=[{k:v for k,v in case.items() if k not in ('vertices','faces','uv','smooth')} for case in refs]
        source='font_path='+repr(self.font())+'\ncases='+repr(cases)+'\n'+(test_cli.ROOT/'compat/text_probe.py').read_text()
        script=self.script(source);self.hb('check',script);self.hb('run',script)
        scene=revision(self.path/'scene.hb')['scene'];meshes=sorted(scene['meshes'],key=lambda m:m['name'])
        self.assertEqual(len(meshes),351);self.assertEqual(len(scene['fonts']),1)
        self.assertFalse(compare(meshes,refs))
    def test_font_persistence_and_text_exports(self):
        shutil.copyfile(self.font(),self.path/'font.ttf')
        self.hb('run',self.script("""import bpy
font=bpy.data.fonts.load('font.ttf');assert font.name=='DejaVu Sans Book'
bpy.ops.object.text_add();obj=bpy.context.object;obj.name='Label';obj.data.font=font;obj.data.body='Hello';obj.data.align_x='CENTER'
assert font.users==1
mat=bpy.data.materials.new('Ink');obj.data.materials.append(mat)
bpy.context.view_layer.update()
assert obj.type=='FONT' and obj.dimensions.x>0
obj.data.size=.0001;bpy.context.view_layer.update();obj.data.size=1.
"""))
        (self.path/'font.ttf').unlink()
        self.hb('run',self.script("""import bpy
obj=bpy.data.objects['Label'];assert obj.data.font.name=='DejaVu Sans Book';obj.data.body='next\nline'
copy=obj.data.copy();assert copy.font.users==2
other=bpy.data.objects.new('Copy',copy);bpy.context.collection.objects.link(other);other.location=(2,0,0)
copy.materials.clear();copy.materials.append(bpy.data.materials['Ink']);assert copy.materials.pop().name=='Ink'
bpy.ops.export_scene.gltf(filepath='text.glb')
""".replace("'next\nline'","'next\\nline'")))
        self.assertTrue((self.path/'text.glb').is_file())
        for extension in ('glb','obj','usdz'):self.hb('export','text.'+extension)
        self.hb('query','bbox')
    def test_text_boundaries_rollback(self):
        self.hb('run',test_cli.ROOT/'compat/golden/m3_text.py');before=(self.path/'scene.hb').read_bytes()
        for body in ("bpy.ops.object.text_add()","text.body='é'","text.body='x'*257","text.extrude=-.1","text.bevel_depth=.1","text.align_y='CENTER'","text.resolution_u=33","text.splines.new('POLY')"):
            result=self.hb('run',self.script("import bpy\ntext=bpy.data.objects['Label_0'].data\n"+body),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API');self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        for data in (b'not a font',b'OTTO'+bytes(100),bytes(4*1024*1024+1)):
            (self.path/'bad.ttf').write_bytes(data)
            result=self.hb('run',self.script("import bpy\nbpy.data.fonts.load('bad.ttf')"),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API');self.assertEqual((self.path/'scene.hb').read_bytes(),before)
    def test_text_export_comparator_rejects_geometry_and_normal_changes(self):
        import struct
        from text_glb_check import verify
        self.hb('run',test_cli.ROOT/'compat/golden/m3_text.py','--out','reference.glb')
        reference=self.path/'reference.glb';original=reference.read_bytes();length=struct.unpack_from('<I',original,12)[0];doc=json.loads(original[20:20+length]);binary=28+length
        primitive=doc['meshes'][doc['nodes'][0]['mesh']]['primitives'][0]
        names=tuple('Label_'+str(i) for i in range(5));verify(reference,reference,names)
        for attribute,component,value in (('POSITION',0,100.),('NORMAL',1,-1.)):
            accessor=doc['accessors'][primitive['attributes'][attribute]];view=doc['bufferViews'][accessor['bufferView']];offset=binary+view.get('byteOffset',0)+accessor.get('byteOffset',0)+4*component
            damaged=bytearray(original);struct.pack_into('<f',damaged,offset,value);candidate=self.path/'damaged.glb';candidate.write_bytes(damaged)
            with self.assertRaises(AssertionError):verify(reference,candidate,names)
