import unittest,json,subprocess
import test_cli
from test_cli import HB,ROOT
from normalize import revision

class Modeling(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_golden_preflight(self):
        for script in sorted((ROOT/'compat/golden').glob('*.py')):
            with self.subTest(script=script.name):self.hb('check',script)
    def test_scoped_names_and_function_returns(self):
        script=self.script('''import bpy
from mathutils import Vector
def material():
 m=bpy.data.materials.new('paint');m.diffuse_color=(1,0,0,1);return m
def triangle():
 m=bpy.data.meshes.new('triangle');m.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)]);return m
m=triangle();m.materials.append(material())
o=bpy.data.objects.new('piece',m);bpy.context.collection.objects.link(o)
o.location=Vector((1,2,3))
''')
        self.hb('check',script);self.hb('run',script)
    def test_checker_follows_hidden_api_values(self):
        cases=[
            "def use(obj):\n obj.constraints.new('COPY_LOCATION')\nuse(bpy.context.object)",
            "def make():\n return bpy.context.object\nmake().constraints.new('COPY_LOCATION')",
            "objects=[bpy.context.object]\nobjects[0].constraints.new('COPY_LOCATION')",
            "objects={}\nobjects['x']=bpy.context.object\nobjects['x'].constraints.new('COPY_LOCATION')",
            "objects=[]\nobjects.append(bpy.context.object)\nobjects[0].constraints.new('COPY_LOCATION')",
            "obj=bpy.context.object\nobj=bpy.data.meshes.new('m')\nobj.constraints.new('COPY_LOCATION')",
            "bpy.context.object.modifiers.new('Bevel','SHRINKWRAP')",
        ]
        for source in cases:
            with self.subTest(source=source):
                result=self.hb('check',self.script('import bpy\n'+source),ok=False)
                self.assertTrue(result['errors'])
    def test_array_evaluation_persistence_and_modes(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(size=1)
o=bpy.context.object
a=o.modifiers.new('columns','ARRAY');a.count=3;a.relative_offset_displace=(1.5,0,0)
b=o.modifiers.new('expand','ARRAY');b.count=2
'''))['revision']
        s=revision(self.path/'scene.hb')['scene']
        self.assertEqual(len(s['meshes'][0]['vertices']),8)
        self.assertEqual(self.hb('query','bbox','Cube')['result']['bbox']['max'],[7.5,.5,.5])
        render=self.hb('render','--views','iso','--size','64','--out','array.png')
        self.assertEqual(render['render']['triangles'],72)
        self.hb('export','array.glb');self.hb('import','array.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],72)
        self.hb('run',self.script("import bpy\nbpy.data.objects['Cube'].modifiers['expand'].show_viewport=False"))
        self.assertEqual(self.hb('query','bbox','Cube')['result']['bbox']['max'],[3.5,.5,.5])
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],72)
        self.hb('run',self.script("import bpy\nbpy.data.objects['Cube'].modifiers['expand'].show_render=False"))
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],36)
        self.hb('checkout',first)
        self.assertEqual(self.hb('query','bbox','Cube')['result']['bbox']['max'],[7.5,.5,.5])
    def test_modifier_handles_and_shared_mesh_safety(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;a=o.modifiers.new('a','ARRAY');o.modifiers.remove(a);b=o.modifiers.new('a','ARRAY')
try:a.count=5
except ReferenceError:pass
else:raise AssertionError('Stale handle changed a new modifier')
p=o.copy();bpy.context.collection.objects.link(p)
'''))
        before=(self.path/'scene.hb').read_bytes()
        r=self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='a')"),ok=False)
        self.assertEqual(r['error']['code'],'UNSUPPORTED_API')
        self.assertEqual(before,(self.path/'scene.hb').read_bytes())
    def test_bmesh_invalid_handles_and_custom_layers(self):
        self.hb('run',self.script('''import bpy,bmesh
bm=bmesh.new();v=bm.verts.new((1,2,3));co=v.co;bm.free()
for read in (lambda:v.co,lambda:co.x):
 try:read()
 except ReferenceError:pass
 else:raise AssertionError('Freed vertex is still accessible')
bpy.ops.mesh.primitive_cube_add()
'''))
        self.hb('run',self.script('import bpy,bmesh\nbm=bmesh.new();bm.from_mesh(bpy.context.object.data)\nassert bm.loops.layers.uv.active.name=="UVMap"\nbm.to_mesh(bpy.context.object.data)'))
    def test_vector_views_and_rejected_shape_changes(self):
        self.hb('run',self.script('''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;o.location=Vector((1,2,3));p=o.location;p.yx=(7,8)
assert tuple(o.location)==(8,7,3)
q=p.copy();q.x=0;assert p.x==8
for action in (lambda:p.__setitem__(slice(None),[1,2]),lambda:p.__setattr__('xx',(1,2))):
 try:action()
 except (ValueError,AttributeError):pass
 else:raise AssertionError('invalid vector mutation')
assert tuple(o.location)==(8,7,3)
v=Vector((1,2,3,4)).normalized();assert v.w==4 and abs(v.to_3d().length-1)<1e-6
'''))
    def test_unsupported_modifier_rolls_back(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\nm=bpy.context.object.modifiers.new('a','ARRAY');m.fit_type='FIT_CURVE'"),ok=False)
        self.assertEqual(before,(self.path/'scene.hb').read_bytes())

if __name__=='__main__':unittest.main()
