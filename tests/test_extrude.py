import unittest,json,zlib
import test_cli
from normalize import revision
from extrude_mixed_check import compare

class Extrusion(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_returned_geometry_cap_winding_and_roundtrip(self):
        script=self.script('''import bpy,bmesh
bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)
base=list(bm.faces)[0]
result=bmesh.ops.extrude_face_region(bm,geom=[base])
vertices=[g for g in result['geom'] if isinstance(g,bmesh.types.BMVert)]
faces=[g for g in result['geom'] if isinstance(g,bmesh.types.BMFace)]
assert len(vertices)==4 and len(faces)==1 and len(result['geom'])==9
assert all(v.co.z==0 for v in vertices)
bmesh.ops.translate(bm,verts=vertices,vec=(0,0,2))
bm.normal_update()
assert tuple(base.normal)==(0,0,-1) and tuple(faces[0].normal)==(0,0,1)
mesh=bpy.data.meshes.new('Box');bm.to_mesh(mesh)
obj=bpy.data.objects.new('Box',mesh);bpy.context.collection.objects.link(obj)
bm.free()
''')
        self.hb('check',script)
        a=self.hb('run',script,'--out','box.glb')
        b=self.hb('run',script,'--scene','again.hb')
        self.assertEqual(a['revision'],b['revision'])
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(mesh['faces'],[[0,2,3,1],[4,5,6,7],[0,1,5,4],[1,3,6,5],[3,2,7,6],[2,0,4,7]])
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],12)
        self.hb('import','box.glb','--scene','import.hb')
        self.assertEqual(self.hb('query','stats','--scene','import.hb')['result']['triangles'],12)

    def test_extrusion_and_rollback(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add(calc_uvs=False)'))
        before=(self.path/'scene.hb').read_bytes()
        for call in ("geom=list(bm.faces),use_normal_from_adjacent=True", "geom=list(bm.faces),use_normal_flip=True", "geom=list(bm.faces),use_dissolve_ortho_edges=True", "geom=list(bm.faces),use_select_history=True", "geom=list(bm.faces),edges_exclude=set(bm.edges)"):
            with self.subTest(call=call):
                script=self.script("import bpy,bmesh\nbm=bmesh.new();bm.from_mesh(bpy.context.object.data)\nbmesh.ops.extrude_face_region(bm,"+call+")\nbm.to_mesh(bpy.context.object.data)")
                self.hb('run',script,ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_invalid_region_does_not_mutate_bmesh(self):
        self.hb('run',self.script('''import bmesh
bm=bmesh.new()
v=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(0,1,0),(0,-1,0))]
a=bm.faces.new((v[0],v[1],v[2]));b=bm.faces.new((v[0],v[1],v[3]))
try:bmesh.ops.extrude_face_region(bm,geom=[a,b])
except Exception:pass
else:raise AssertionError('Inconsistent winding must fail')
assert len(bm.verts)==4 and len(bm.faces)==2
other=bmesh.new();bmesh.ops.create_grid(other,x_segments=1,y_segments=1,size=1)
try:bmesh.ops.extrude_face_region(bm,geom=list(other.faces))
except ValueError:pass
else:raise AssertionError('Foreign handles must fail')
assert len(bm.verts)==4
bm.free();other.free()
'''))

    def test_checker_tracks_geometry_return(self):
        self.hb('check',self.script('''import bmesh
bm=bmesh.new();result=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
verts=[g for g in result['geom'] if isinstance(g,bmesh.types.BMVert)]
for v in verts:v.co.z+=1
'''))
        self.hb('check',self.script('''import bmesh
bm=bmesh.new();result=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
for g in result['geom']:g.unsupported_surface
'''),ok=False)
        self.hb('check',self.script('import bmesh\nbmesh.ops.extrude_face_region(bmesh.new(),skip_input_flip=True)'),ok=False)

    def test_102_mixed_geometry_cases_match_blender(self):
        self.hb('check',test_cli.ROOT/'compat/golden/m3_extrude_mixed.py')
        self.hb('run',test_cli.ROOT/'compat/extrude_mixed_probe.py')
        refs=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/extrude-mixed-reference.json.zlib').read_bytes()))
        compare(refs,revision(self.path/'scene.hb')['scene'])

    def test_mixed_invalid_geometry_is_atomic(self):
        self.hb('run',self.script("""import bmesh
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
other=bmesh.new();foreign=other.verts.new((0,0,0))
before=(len(bm.verts),len(bm.edges),len(bm.faces))
try:bmesh.ops.extrude_face_region(bm,geom=list(bm.faces)+[foreign])
except ValueError:pass
else:raise AssertionError('Foreign mixed geometry accepted')
assert before==(len(bm.verts),len(bm.edges),len(bm.faces))
bm.free();other.free()
"""))

    def test_smooth_retained_attached_cap_rejection_preserves_geometry(self):
        self.hb('run',self.script("""import bmesh
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
face=list(bm.faces)[0];face.smooth=True
before=(len(bm.verts),len(bm.edges),len(bm.faces))
try:bmesh.ops.extrude_face_region(bm,geom=[face]+list(face.edges),use_keep_orig=True)
except Exception as e:assert 'flat incident faces' in str(e)
else:raise AssertionError('Unverified smooth retained cap accepted')
assert before==(len(bm.verts),len(bm.edges),len(bm.faces)) and face.is_valid
"""))
