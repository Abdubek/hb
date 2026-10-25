import unittest,json,zlib
import test_cli
from normalize import revision

class Curves(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_poly_geometry_reference(self):
        refs=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/curves-reference.json.zlib').read_bytes()))
        refs=[r for r in refs if not r['caps'] and not (r['cyclic'] and r['path']==6)]
        refs+=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/curves-varied-reference.json.zlib').read_bytes()))
        code='cases='+repr(refs)+'\n'+(test_cli.ROOT/'compat/curves_probe.py').read_text()
        script=self.script(code);self.hb('check',script);self.hb('run',script)
        meshes=sorted(revision(self.path/'scene.hb')['scene']['meshes'],key=lambda m:m['name'])
        self.assertEqual(len(meshes),134)
        for i,(m,r) in enumerate(zip(meshes,refs)):
            with self.subTest(i=i):
                self.assertEqual(len(m['vertices']),len(r['vertices']))
                self.assertLessEqual(max([abs(a-b) for av,bv in zip(m['vertices'],r['vertices']) for a,b in zip(av,bv)]+[0]),1e-5)
                self.assertEqual(m['faces'],r['faces'])
                self.assertEqual(sorted(sorted(e) for e in m['edges']),sorted(sorted(e) for e in r['edges']))
                self.assertEqual(m['smooth'],r['smooth'])
                uv=m['uv_layers'][0]['data'] if m['uv_layers'] else []
                self.assertEqual(len(uv),len(r['uv']))
                self.assertLessEqual(max([abs(a-b) for av,bv in zip(uv,r['uv']) for a,b in zip(av,bv)]+[0]),1e-5)
    def test_curve_persistence_materials_and_exports(self):
        self.hb('run',test_cli.ROOT/'compat/golden/m3_curves.py')
        self.hb('run',self.script('''import bpy
c=bpy.data.curves['Curve_0'];assert c.users==1
assert bpy.data.objects['Pipe_0'].type=='CURVE'
assert bpy.data.objects['Pipe_0'].data==c
m=bpy.data.meshes.new('Curve_0');assert m.name==c.name
clone=c.copy();assert clone.name=='Curve_0.001' and clone.users==0
clone.splines[0].points[0].co=(.5,.2,.3,1)
o=bpy.data.objects.new('Clone',clone);bpy.context.collection.objects.link(o)
clone.materials.append(bpy.data.materials.new('Extra'));clone.splines[0].material_index=1
assert clone.materials.pop().name=='Extra' and clone.splines[0].material_index==0
bpy.context.view_layer.update()
assert len(o.dimensions)==3
bpy.ops.export_scene.gltf(filepath='curves.glb')
'''))
        self.assertTrue((self.path/'curves.glb').is_file())
        for extension in ('glb','obj','usdz'):self.hb('export','curve.'+extension)
        self.hb('run',self.script("import bpy\nc=bpy.data.curves['Curve_0.001'];c.materials.clear();c.splines.clear();bpy.context.view_layer.update();assert len(c.splines)==0\nbpy.data.curves.remove(c);assert bpy.data.objects['Clone'].type=='EMPTY'"))
    def test_curve_boundaries_are_atomic(self):
        self.hb('run',test_cli.ROOT/'compat/golden/m3_curves.py');before=(self.path/'scene.hb').read_bytes()
        for body in ("c.splines.new('NURBS')","c.bevel_resolution=9","c.dimensions='2D'","c.splines[0].points.add(5000)","c.splines[0].points[1].co=c.splines[0].points[0].co","c.twist_mode='Z_UP'","c.bevel_depth=float('nan')"):
            result=self.hb('run',self.script("import bpy\nc=bpy.data.curves['Curve_0']\n"+body),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API');self.assertEqual((self.path/'scene.hb').read_bytes(),before)
