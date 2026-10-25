import unittest,json,zlib
import test_cli
from normalize import revision
from bevel_extensions_check import compare
class Bevel(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_evaluation_application_and_undo(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(size=2,calc_uvs=False)
o=bpy.context.object;o.scale=(1.5,1,.5)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=o.modifiers.new('Round','BEVEL');m.width=.15;m.segments=3
'''))['revision']
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),8)
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],188)
        self.hb('export','bevel.glb');self.hb('import','bevel.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],188)
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Round')"))
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),96)
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),8)
    def test_unsupported_meshes_and_settings_roll_back(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add(calc_uvs=False)'))
        before=(self.path/'scene.hb').read_bytes()
        for change in ("o.data.uv_layers.new(name='UV');o.modifiers.new('b','BEVEL')", "m=o.modifiers.new('b','BEVEL');m.segments=9", "m=o.modifiers.new('b','BEVEL');m.use_clamp_overlap=False;m.width=2", "m=o.modifiers.new('b','BEVEL');m.profile=.7", "m=o.modifiers.new('b','BEVEL');o.data.vertices[0].co.x+=.2", "m=o.modifiers.new('b','BEVEL');o.data.polygons[0].use_smooth=True"):
            with self.subTest(change=change):
                self.hb('run',self.script('import bpy\no=bpy.context.object\n'+change),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
    def test_transform_application_preserves_world_geometry(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(location=(2,3,4),rotation=(.2,.3,.4))
bpy.context.object.scale=(2,.7,1.4)
'''))
        before=self.hb('query','bbox','Cube')['result']['bbox']
        self.hb('run',self.script('import bpy\nbpy.ops.object.transform_apply()'))
        after=self.hb('query','bbox','Cube')['result']['bbox']
        for field in ('min','max'):
            for x,y in zip(before[field],after[field]):self.assertAlmostEqual(x,y,places=5)
        scene=revision(self.path/'scene.hb')['scene'];o=scene['objects'][0]
        self.assertEqual(o['location'],[0,0,0]);self.assertEqual(o['rotation_euler'],[0,0,0]);self.assertEqual(o['scale'],[1,1,1])
        self.assertEqual(len(scene['meshes'][0]['uv_layers'][0]['data']),24)
    def test_shared_mesh_transform_rejection(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\no=bpy.context.object;p=o.copy();bpy.context.collection.objects.link(p);p.select_set(False)"))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script('import bpy\nbpy.ops.object.transform_apply()'),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_preflight_accepts_textured_cubes(self):
        self.hb('check',self.script("import bpy\ndef box():\n bpy.ops.mesh.primitive_cube_add()\nbox()\no=bpy.context.object\no.modifiers.new('b','BEVEL')"))
        self.hb('check',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\ntextured=bpy.context.object\nbpy.ops.mesh.primitive_cube_add(calc_uvs=False)\nplain=bpy.context.object\nplain.modifiers.new('b','BEVEL')"))

    def test_uv_evaluation_application_and_undo(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
uv=o.data.uv_layers.new(name='Second')
for loop in uv.data:loop.uv=(loop.uv.x*.5+.1,loop.uv.y*.75)
m=o.modifiers.new('Round','BEVEL');m.segments=3;m.width=.005
'''))['revision']
        self.hb('export','uv.glb')
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Round')"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),96)
        self.assertEqual([len(layer['data']) for layer in mesh['uv_layers']],[384,384])
        self.assertTrue(all(len(uv)==2 for layer in mesh['uv_layers'] for uv in layer['data']))
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['uv_layers'][0]['data']),24)

    def test_unsupported_uv_layout_rolls_back(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\no=bpy.context.object\no.data.uv_layers.active.data[0].uv.x+=.1\no.modifiers.new('Round','BEVEL')"),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_vertex_modes_and_clamping_match_blender(self):
        self.hb('run',test_cli.ROOT/'compat/bevel_extensions_probe.py')
        reference=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/bevel-reference.json.zlib').read_bytes()))
        compare(reference,revision(self.path/'scene.hb')['scene'])

    def test_clamped_bevel_renders_and_unclamped_failure_is_atomic(self):
        for affect in ('EDGES','VERTICES'):
            source="import bpy\nbpy.ops.mesh.primitive_cube_add()\no=bpy.context.object\nm=o.modifiers.new('Bevel','BEVEL')\n"
            source+=f"m.affect={affect!r};m.width=3;m.use_clamp_overlap=False\n"
            source+="""
before=[tuple(v.co) for v in o.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:assert 'use_clamp_overlap' in str(error)
else:raise AssertionError('Overlapping bevel accepted without clamping')
assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
m.use_clamp_overlap=True
# A clamp may still produce numerically degenerate faces at f32 precision.
# Such geometry must be rejected atomically instead of failing later in review.
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:
    assert 'degenerate' in str(error) or 'triangulate' in str(error)
    assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
    m.width=.4
else:pass
"""
            self.hb('run',self.script(source),'--scene',affect+'.hb','--out',affect+'.glb')
            self.hb('render','--scene',affect+'.hb','--size','64','--views','iso')
            self.hb('run',self.script("import bpy\nif bpy.context.object.modifiers:bpy.ops.object.modifier_apply(modifier='Bevel')"),'--scene',affect+'.hb','--out',affect+'-applied.glb')

    def test_odd_vertex_bevel_texture_rejection_preserves_mesh(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
m=o.modifiers.new('Bevel','BEVEL');m.affect='VERTICES';m.segments=3
before=[tuple(v.co) for v in o.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:assert 'one or even segments' in str(error)
else:raise AssertionError('Unverified odd vertex-bevel UV interpolation accepted')
assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
o.modifiers.remove(m)
"""))
