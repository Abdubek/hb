import unittest,json,zlib
import test_cli
from normalize import revision

class WeightedNormals(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_evaluation_application_rendering_and_undo(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.scale=(3,2,1)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
'''))
        self.hb('render','--views','iso','--size','64','--out','flat.png')
        first=self.hb('run',self.script("import bpy\nbpy.context.object.modifiers.new('Weight','WEIGHTED_NORMAL')"))['revision']
        self.hb('render','--views','iso','--size','64','--out','weighted.png')
        self.assertNotEqual((self.path/'flat.png').read_bytes(),(self.path/'weighted.png').read_bytes())
        self.assertEqual(revision(self.path/'scene.hb')['scene']['meshes'][0]['loop_normals'],[])
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Weight')"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),8);self.assertEqual(len(mesh['loop_normals']),24)
        for got,expected in zip(mesh['loop_normals'][0],(-2/7,-3/7,-6/7)):self.assertAlmostEqual(got,expected,delta=1e-4)
        self.hb('render','--views','iso','--size','64','--out','applied.png')
        self.assertEqual((self.path/'weighted.png').read_bytes(),(self.path/'applied.png').read_bytes())
        self.hb('checkout',first)
        self.assertEqual(revision(self.path/'scene.hb')['scene']['meshes'][0]['loop_normals'],[])

    def test_keep_sharp_and_parameter_rollback(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nm=bpy.context.object.modifiers.new('Weight','WEIGHTED_NORMAL');m.keep_sharp=True"))
        before=(self.path/'scene.hb').read_bytes()
        for setting in ("weight='bad'","thresh='bad'","vertex_group='"+'x'*64+"'"):
            with self.subTest(setting=setting):
                self.hb('run',self.script('import bpy\nm=bpy.context.object.modifiers[0]\nm.'+setting),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Weight')"))
        normals=revision(self.path/'scene.hb')['scene']['meshes'][0]['loop_normals']
        self.assertEqual(normals[:4],[[-1,0,0]]*4)

    def test_checker_limits_and_numeric_failure_rollback(self):
        for value,valid in ((50,True),(75,True),(101,False)):
            script=self.script("import bpy\nm=bpy.context.object.modifiers.new('Weight','WEIGHTED_NORMAL')\nm.weight="+str(value))
            self.hb('check',script,ok=valid)
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script('''import bpy
o=bpy.context.object;o.scale=(1e20,1e20,1e20)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
w=o.modifiers.new('Weight','WEIGHTED_NORMAL')
bpy.ops.object.modifier_apply(modifier=w.name)
'''),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_444_parameter_cases_match_blender(self):
        self.hb('check',test_cli.ROOT/'compat/golden/m3_weighted_normals.py')
        self.hb('run',test_cli.ROOT/'compat/weighted_normal_extensions_probe.py')
        self.compare_fixture('weighted-normal-reference.json.zlib')

    def test_18_degenerate_cases_match_blender(self):
        self.hb('run',test_cli.ROOT/'compat/weighted_normal_degenerate_probe.py')
        self.compare_fixture('weighted-normal-degenerate-reference.json.zlib')

    def compare_fixture(self,name):
        refs=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures'/name).read_bytes()))
        scene=revision(self.path/'scene.hb')['scene'];meshes={m['id']:m for m in scene['meshes']}
        for obj in scene['objects']:
            with self.subTest(case=obj['name']):
                mesh=meshes[obj['data']['id']];ref=refs[obj['name']]
                self.assertEqual(mesh['vertices'],ref['source']['vertices']);self.assertEqual(mesh['faces'],ref['source']['faces'])
                self.assertEqual(len(mesh['loop_normals']),len(ref['normals']))
                for a,b in zip(mesh['loop_normals'],ref['normals']):
                    for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=1e-4)

    def test_face_strength_edits_and_memberships_survive_apply(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;g=o.vertex_groups.new(name='Mask');g.add([0,1],0,'REPLACE')
a=o.data.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')
a.data[0].value=2
for invalid in (-1,3):
    try:a.data[0].value=invalid
    except Exception:pass
    else:raise AssertionError('Invalid strength accepted')
    assert a.data[0].value==2
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.vertex_group='Mask';w.use_face_influence=True
"""),'--out','stack.glb')
        before=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Weight')"),'--out','applied.glb')
        after=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(before['deform_weights'],after['deform_weights']);self.assertEqual(before['face_strength'],after['face_strength'])
        self.assertTrue(after['loop_normals'])

    def test_discontinuous_smooth_custom_normals_reject_atomically(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
for f in o.data.polygons:f.use_smooth=True
o.data.normals_split_custom_set([(1,0,0)]*12+[(0,1,0)]*12)
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True
try:bpy.ops.object.modifier_apply(modifier=w.name)
except Exception as e:assert 'consistent values' in str(e)
else:raise AssertionError('Discontinuous custom normal fan accepted')
assert len(o.modifiers)==1 and len(o.data.vertices)==8
o.modifiers.remove(w)
"""))
