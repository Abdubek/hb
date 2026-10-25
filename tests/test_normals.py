import unittest,json,zlib
from pathlib import Path
import test_cli
from normalize import revision

class NormalRepair(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_repair_mesh_roundtrip_and_determinism(self):
        script=self.script('''import bpy,bmesh
points=((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))
faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
mesh=bpy.data.meshes.new('Repaired');mesh.from_pydata(points,[],[tuple(reversed(f)) for f in faces])
bm=bmesh.new();bm.from_mesh(mesh)
assert bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)) is None
bm.to_mesh(mesh);bm.free()
obj=bpy.data.objects.new('Repaired',mesh);bpy.context.collection.objects.link(obj)
''')
        self.hb('check',script)
        first=self.hb('run',script,'--out','a.glb')
        second=self.hb('run',script,'--scene','again.hb','--out','b.glb')
        self.assertEqual(first['revision'],second['revision'])
        self.assertEqual((self.path/'a.glb').read_bytes(),(self.path/'b.glb').read_bytes())
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],12)
        self.hb('import','a.glb','--scene','import.hb')
        self.assertEqual(self.hb('query','stats','--scene','import.hb')['result']['triangles'],12)

    def test_invalid_regions_leave_handles_and_scene_unchanged(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add(calc_uvs=False)'))
        before=(self.path/'scene.hb').read_bytes()
        cases=(
            "list(bm.verts)[0].co.z+=.4;faces=list(bm.faces)",  # Non-planar quad.
            "for v in bm.verts:v.co.z=0\nfaces=list(bm.faces)",
            "f=list(bm.faces)[0];bm.faces.new((f.verts[0],f.verts[1],bm.verts.new((3,3,3))));faces=list(bm.faces)",
        )
        for setup in cases:
            with self.subTest(setup=setup):
                prefix='import bpy,bmesh\nbm=bmesh.new();bm.from_mesh(bpy.context.object.data)\n'+setup+'\n'
                script=self.script(prefix+'bmesh.ops.recalc_face_normals(bm,faces=faces)\nbm.to_mesh(bpy.context.object.data)')
                result=self.hb('run',script,ok=False)
                self.assertEqual(result['error']['code'],'UNSUPPORTED_API')
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
                standalone='import bmesh\nbm=bmesh.new();bmesh.ops.create_cube(bm,size=2)\n'+setup+'\n'
                self.hb('run',self.script(standalone+'''saved=[(tuple(f.verts),tuple(f.edges),tuple(f.normal)) for f in bm.faces]
try:bmesh.ops.recalc_face_normals(bm,faces=faces)
except Exception:pass
else:raise AssertionError('Unsupported input accepted')
assert saved==[(tuple(f.verts),tuple(f.edges),tuple(f.normal)) for f in bm.faces]
bm.free()
'''),'--scene','handles.hb')

    def test_duplicate_foreign_freed_and_operator_disabled(self):
        self.hb('run',self.script('''import bmesh
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2);faces=list(bm.faces)
other=bmesh.new();bmesh.ops.create_cube(other,size=2)
for values in (faces+faces[:1],list(other.faces),list(bm.verts)):
    try:bmesh.ops.recalc_face_normals(bm,faces=values)
    except ValueError:pass
    else:raise AssertionError('Invalid handles accepted')
bm.faces.remove(faces[0])
try:bmesh.ops.recalc_face_normals(bm,faces=faces)
except ReferenceError:pass
else:raise AssertionError('Removed handle accepted')
bm.free()
try:bmesh.ops.recalc_face_normals(bm)
except ReferenceError:pass
else:raise AssertionError('Freed BMesh accepted')
disabled=bmesh.new(use_operators=False)
try:bmesh.ops.recalc_face_normals(disabled)
except ValueError:pass
else:raise AssertionError('Disabled operators accepted')
disabled.free();other.free()
'''))

    def test_checker_validates_call_shape(self):
        self.hb('check',self.script('import bmesh\nbm=bmesh.new();bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))'))
        for call in ('bm,faces=[],use_flip=True','bm,[]','bm,geom=[]',''):
            result=self.hb('check',self.script('import bmesh\nbm=bmesh.new();bmesh.ops.recalc_face_normals('+call+')'),ok=False)
            self.assertTrue(result['errors'])

    def test_translated_face_normals_and_empty_selection(self):
        self.hb('run',self.script('''import bmesh
bm=bmesh.new();v=[bm.verts.new(p) for p in ((10000,10000,10000),(10001,10000,10000),(10000,10001,10000))]
f=bm.faces.new(v)
assert tuple(f.normal)==(0,0,0)
assert bmesh.ops.recalc_face_normals(bm) is None
assert tuple(f.normal)==(0,0,1)
for vertex in v:vertex.co.z=vertex.co.x
bm.normal_update()
assert abs(f.normal.x+2**-.5)<1e-5 and abs(f.normal.z-2**-.5)<1e-5
bm.free()
'''))

    def test_non_orientable_topology_and_vertex_junctions(self):
        self.hb('run',self.script('''import bmesh
# Minimal triangulation of the projective plane: every edge has two faces,
# but no globally consistent winding exists.
bm=bmesh.new();v=[bm.verts.new((i,i*i,i*i*i)) for i in range(6)]
triangles=((0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,1),(1,2,4),(2,3,5),(3,4,1),(4,5,2),(5,1,3))
for f in triangles:bm.faces.new([v[i] for i in f])
saved=[tuple(f.verts) for f in bm.faces]
try:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
except Exception as e:assert 'Non-orientable' in str(e)
else:raise AssertionError('Non-orientable topology accepted')
assert saved==[tuple(f.verts) for f in bm.faces]
bm.free()
# Two otherwise closed solids share a single vertex.
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
v=[list(bm.verts)[0]]+[bm.verts.new(p) for p in ((-3,-1,-1),(-1,-3,-1),(-1,-1,-3))]
for f in ((0,2,1),(0,1,3),(1,2,3),(2,0,3)):bm.faces.new([v[i] for i in f])
saved=[tuple(f.verts) for f in bm.faces]
try:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
except Exception as e:assert 'sharing only a vertex' in str(e)
else:raise AssertionError('Shared-vertex junction accepted')
assert saved==[tuple(f.verts) for f in bm.faces]
bm.free()
'''))

    def test_open_partial_and_rotated_blender_references(self):
        refs=json.loads(zlib.decompress((Path(test_cli.ROOT)/'compat/fixtures/normal-repair-reference.json.zlib').read_bytes()))
        code=['import bpy,bmesh\n']
        for name,row in refs.items():
            src=row['source']
            code.append(f"m=bpy.data.meshes.new({name!r});m.from_pydata({src['vertices']!r},{src['edges']!r},{src['faces']!r})\no=bpy.data.objects.new({name!r},m);bpy.context.collection.objects.link(o)\nbm=bmesh.new();bm.from_mesh(m);bm.faces.ensure_lookup_table()\nbmesh.ops.recalc_face_normals(bm,faces=[bm.faces[i] for i in {src['selected']!r}])\n")
            code.append(f"for f,n in zip(bm.faces,{row['normals']!r}):assert max(abs(a-b) for a,b in zip(f.normal,n))<=1e-5,({name!r},tuple(f.normal),n)\nbm.to_mesh(m);bm.free()\n")
        self.hb('run',self.script(''.join(code)))
        scene=revision(self.path/'scene.hb')['scene'];meshes={m['id']:m for m in scene['meshes']}
        def cycle(f):return min(tuple(f[i:]+f[:i]) for i in range(len(f)))
        self.assertEqual(len(scene['objects']),140)
        for obj in scene['objects']:
            mesh=meshes[obj['data']['id']];row=refs[obj['name']]
            self.assertEqual(mesh['vertices'],row['source']['vertices'])
            self.assertEqual([cycle(f) for f in mesh['faces']],[cycle(f) for f in row['faces']],obj['name'])
