import unittest,json
import test_cli
from normalize import revision
from boolean_check import compare,actual_mesh

SETUP="""import bpy
bpy.ops.mesh.primitive_cube_add(size=2)
a=bpy.context.object;a.name='Body'
bpy.ops.mesh.primitive_cube_add(size=2,location=(1,0,0))
b=bpy.context.object;b.name='Cutter'
m=a.modifiers.new('Cut','BOOLEAN');m.solver='MANIFOLD';m.object=b
bpy.context.view_layer.objects.active=a
"""
class Boolean(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_blender_solver_boundaries_and_corner_attributes(self):
        for prefix in ('','attributes_'):
            self.hb('run',test_cli.ROOT/('compat/boolean_'+prefix+'probe.py'),'--scene',prefix+'probe.hb')
            scene=revision(self.path/(prefix+'probe.hb'))['scene']
            file='boolean-attributes-reference.json' if prefix else 'boolean-reference.json'
            reference=json.loads((test_cli.ROOT/'compat/fixtures'/file).read_text())
            for name,expected in reference.items():
                if not prefix and name.startswith('MANIFOLD_') and name.endswith('_True'):continue
                if prefix and name.startswith(('collection_FAST_INTERSECT','empty_collection_FAST_INTERSECT')):continue
                with self.subTest(name=name):compare(expected,actual_mesh(scene,name))

    def test_collection_references_and_color_validation_are_atomic(self):
        self.hb('run',self.script(SETUP+"""
collection=bpy.data.collections.new('Operands');bpy.context.scene.collection.children.link(collection);collection.objects.link(b)
m.operand_type='COLLECTION';m.collection=collection;m.solver='EXACT'
assert collection.users==2
colors=a.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
for entry in colors.data:entry.color=(.1,.2,.3,1)
try:colors.data[0].color=(1,2,3,float('nan'))
except ValueError:pass
else:raise AssertionError('Nonfinite color accepted')
assert abs(colors.data[0].color[0]-.1)<1e-6
try:a.data.color_attributes.new(name='Another',type='FLOAT_COLOR',domain='CORNER')
except Exception:pass
else:raise AssertionError('Second color layer accepted')
assert len(a.data.color_attributes)==1
bpy.data.collections.remove(collection,do_unlink=True)
assert m.collection is None
"""))

    def test_fast_collection_intersection_failure_preserves_input(self):
        for populated in (False,True):
            source=SETUP+"""
collection=bpy.data.collections.new('Operands');bpy.context.scene.collection.children.link(collection)
m.operand_type='COLLECTION';m.collection=collection;m.solver='FAST';m.operation='INTERSECT'
"""+('collection.objects.link(b)\n' if populated else '')+"""
vertices=[tuple(v.co) for v in a.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:assert 'EXACT' in str(error)
else:raise AssertionError('Unsupported FAST collection intersection accepted')
assert vertices==[tuple(v.co) for v in a.data.vertices] and len(a.modifiers)==1
a.modifiers.remove(m)
"""
            self.hb('run',self.script(source),'--scene',str(populated)+'.hb')

    def test_apply_query_export_revision_and_operand_users(self):
        first=self.hb('run',self.script(SETUP+"assert b.users==2\n"),'--out','cut.glb')['revision']
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Cut')\nassert bpy.data.objects['Cutter'].users==1"),'--out','applied.glb')
        scene=revision(self.path/'scene.hb')['scene'];mesh=scene['meshes'][0]
        self.assertEqual(len(mesh['vertices']),8);self.assertEqual(len(mesh['faces']),6)
        self.assertTrue(all(v[0]<=0 for v in mesh['vertices']))
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],24)
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['objects'][0]['modifiers']),1)
    def test_operand_removal_clears_reference(self):
        self.hb('run',self.script(SETUP+"bpy.data.objects.remove(b,do_unlink=True)\nassert m.object is None"))
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],12)
    def test_rejected_geometry_cycles_and_settings_are_atomic(self):
        self.hb('run',self.script(SETUP));before=(self.path/'scene.hb').read_bytes()
        for tail in ("b.scale=(-1,1,1)", "b.scale=(0,1,1)", "a.modifiers['Cut'].object=a", "n=b.modifiers.new('Cycle','BOOLEAN');n.solver='MANIFOLD';n.object=a", "b.data.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])", "a.modifiers['Cut'].material_mode='TRANSFER'", "a.modifiers['Cut'].use_self=True", "a.modifiers['Cut'].double_threshold=.1"):
            with self.subTest(tail=tail):
                result=self.hb('run',self.script("import bpy\na=bpy.data.objects['Body'];b=bpy.data.objects['Cutter']\n"+tail),ok=False)
                self.assertIn('BOOLEAN',result['error']['message'].upper())
                self.assertEqual(before,(self.path/'scene.hb').read_bytes())
    def test_no_operand_apply_is_disabled(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.context.object.modifiers.new('Cut','BOOLEAN')"))
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Cut')"),ok=False)
    def test_empty_disjoint_and_identical_results(self):
        for operation,location,count in (('INTERSECT',4,0),('DIFFERENCE',0,0),('UNION',4,16),('UNION',0,8)):
            with self.subTest(operation=operation,location=location):
                self.hb('run',self.script("import bpy\nbpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\n"+SETUP+f"b.location=( {location},0,0);m.operation='{operation}'\nbpy.ops.object.modifier_apply(modifier='Cut')\nassert len(a.data.vertices)=={count}"))

    def test_through_hole_is_closed_and_has_correct_volume(self):
        self.hb('run',self.script(SETUP+"b.location=(0,0,0);b.scale=(.5,.5,2)\nbpy.ops.object.modifier_apply(modifier='Cut')"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        vertices=mesh['vertices'];edges={};volume=0.
        for f in mesh['faces']:
            for i,a in enumerate(f):
                b=f[(i+1)%len(f)];edges[(a,b)]=edges.get((a,b),0)+1
            a=vertices[f[0]]
            for i in range(1,len(f)-1):
                b=vertices[f[i]];c=vertices[f[i+1]]
                volume+=sum(a[k]*(b[(k+1)%3]*c[(k+2)%3]-b[(k+2)%3]*c[(k+1)%3]) for k in range(3))/6
        self.assertAlmostEqual(volume,6.,places=5)
        self.assertTrue(all(count==1 and edges.get((b,a))==1 for (a,b),count in edges.items()))
    def test_all_uv_layers_survive_gltf_roundtrip(self):
        self.hb('run',self.script(SETUP+"layer=a.data.uv_layers.new(name='Second')\nfor i,loop in enumerate(layer.data):loop.uv=(i/32,i/64)"),'--out','layers.glb')
        self.hb('import','layers.glb','--scene','imported.hb')
        scene=revision(self.path/'imported.hb')['scene']
        owner=next(o for o in scene['objects'] if o['name']=='Body')
        mesh=next(m for m in scene['meshes'] if m['id']==owner['data']['id'])
        self.assertEqual(len(mesh['uv_layers']),2)
        self.assertNotEqual(mesh['uv_layers'][0]['data'],mesh['uv_layers'][1]['data'])
