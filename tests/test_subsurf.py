import unittest,json,zlib
import test_cli
from subsurf_check import compare
from normalize import revision

class Subsurf(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_viewport_render_and_limit_surface(self):
        self.hb('check',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nm=bpy.context.object.modifiers.new('Subdivide','SUBSURF');m.levels=6;m.render_levels=6"))
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nm=bpy.context.object.modifiers.new('Refine','SUBSURF');m.levels=1;m.render_levels=2"),'--out','surface.glb')
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],192)
        self.hb('import','surface.glb','--scene','viewport.hb')
        self.assertEqual(self.hb('query','stats','--scene','viewport.hb')['result']['triangles'],48)
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Refine')"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),26)
        self.assertTrue(any(all(abs(abs(x)-.5)<1e-5 for x in v) for v in mesh['vertices']))
    def test_level_three_uv_materials_and_revision_restore(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
mat=bpy.data.materials.new('Clay');o.data.materials.append(mat)
m=o.modifiers.new('Refine','SUBSURF');m.levels=3;m.use_limit_surface=False
'''))['revision']
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Refine')\nassert len(bpy.context.object.modifiers)==0"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),386);self.assertEqual(len(mesh['faces']),384)
        self.assertEqual(len(mesh['uv_layers'][0]['data']),1536)
        self.assertEqual(set(mesh['material_indices']),{0})
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),8)
    def test_disabled_modifier_and_invalid_options_rollback(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.context.object.modifiers.new('Refine','SUBSURF')"))
        before=(self.path/'scene.hb').read_bytes()
        for source in ("m.levels=7", "m.render_levels=9", "m.quality=6", "m.uv_smooth='NONE'", "m.levels=0;bpy.ops.object.modifier_apply(modifier='Refine')"):
            with self.subTest(source=source):
                self.hb('run',self.script("import bpy\no=bpy.context.object;m=o.modifiers['Refine']\n"+source),ok=False)
                self.assertEqual(before,(self.path/'scene.hb').read_bytes())
    def test_refinement_resource_limit_before_allocation(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
a=o.modifiers.new('Copies','ARRAY');a.count=6000
s=o.modifiers.new('Refine','SUBSURF');s.levels=3
'''),ok=False)
        self.assertFalse((self.path/'scene.hb').exists())

    def test_extended_subdivision_matches_blender_attributes(self):
        self.hb('run',test_cli.ROOT/'compat/subsurf_probe.py')
        reference=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/subsurf-reference.json.zlib').read_bytes()))
        self.assertLessEqual(compare(reference,revision(self.path/'scene.hb')['scene']),1e-4)

    def test_crease_attribute_validation_and_normal_rejections_are_atomic(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
crease=o.data.attributes.new(name='crease_edge',type='FLOAT',domain='EDGE')
crease.data[0].value=.5
for invalid in (-.1,1.1,float('nan')):
    try:crease.data[0].value=invalid
    except ValueError:pass
    else:raise AssertionError('Invalid crease accepted')
    assert crease.data[0].value==.5
try:o.data.attributes.new(name='unlisted',type='FLOAT',domain='POINT')
except Exception:pass
else:raise AssertionError('Unlisted attribute accepted')
assert len(o.data.attributes)==1
for level,smooth,simple in ((4,False,False),(4,False,True),(2,True,False)):
    for face in o.data.polygons:face.use_smooth=smooth
    o.data.normals_split_custom_set([(0,.2,1)]*24)
    m=o.modifiers.new('Refine','SUBSURF');m.levels=level;m.use_custom_normals=True;m.subdivision_type='SIMPLE' if simple else 'CATMULL_CLARK'
    before=[tuple(v.co) for v in o.data.vertices]
    try:bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception as error:assert 'levels 1..2' in str(error)
    else:raise AssertionError('Unverified packed-normal combination accepted')
    assert len(o.data.vertices)==8 and before==[tuple(v.co) for v in o.data.vertices]
    assert len(o.modifiers)==1
    o.modifiers.remove(m)
"""))

    def test_disconnected_wire_boundary_and_groups_fail_without_mutation(self):
        for case in ('junction','group'):
            setup="""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
"""
            setup += ("o.data.from_pydata([(0,0,0),(1,0,0),(0,1,0),(2,0,0)],[(1,3)],[(0,1,2)])\n" if case=='junction' else "g=o.vertex_groups.new(name='Mask');g.add([0],1,'REPLACE')\n")
            self.hb('run',self.script(setup+"""
m=o.modifiers.new('Refine','SUBSURF')
before=[tuple(v.co) for v in o.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception:pass
else:raise AssertionError('Unsupported combination accepted')
assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
o.modifiers.remove(m)
"""),'--scene',case+'.hb')
