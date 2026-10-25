import json,unittest
import test_cli
from normalize import revision

class BMeshData(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_29_blender_layer_and_shape_cases(self):
        self.hb('check',test_cli.ROOT/'compat/golden/m3_bmesh_data.py')
        for kind in ('layers','shape','transform'):
            self.hb('run',test_cli.ROOT/f'compat/bmesh_{kind}_probe.py','--scene',kind+'.hb')
            ref=json.loads((test_cli.ROOT/f'compat/fixtures/bmesh-{kind}-reference.json').read_text())
            scene=revision(self.path/(kind+'.hb'))['scene'];meshes={m['id']:m for m in scene['meshes']}
            for o in scene['objects']:
                with self.subTest(kind=kind,case=o['name']):
                    m=meshes[o['data']['id']];got=dict(vertices=m['vertices'],keys={k['name']:k['points'] for k in m.get('shape_keys',[])})
                    if kind=='layers':got.update(faces=m['faces'],uv=m['uv_layers'],colors=[dict(name=m['color_attribute_name'],data=m['colors'])] if m['colors'] else [],normals=m['loop_normals'])
                    self.close(ref[o['name']],got)
    def close(self,a,b,path=''):
        if isinstance(a,dict):
            self.assertEqual(a.keys(),b.keys(),path)
            for k in a:self.close(a[k],b[k],path+'.'+k)
        elif isinstance(a,list):
            self.assertEqual(len(a),len(b),path)
            for i,(x,y) in enumerate(zip(a,b)):self.close(x,y,path+f'[{i}]')
        elif isinstance(a,(float,int)):self.assertAlmostEqual(a,b,delta=1e-4 if '.normals' in path else 1e-5,msg=path)
        else:self.assertEqual(a,b,path)
    def test_layer_views_invalidate_and_topology_operations_reject(self):
        self.hb('run',self.script('''import bpy,bmesh
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
uv=bm.loops.layers.uv.new('UV')
face=next(iter(bm.faces));view=face.loops[0][uv].uv;view.x=.4
before=(len(bm.verts),len(bm.faces))
try:bmesh.ops.triangulate(bm,faces=list(bm.faces))
except Exception as e:assert 'Topology-changing' in str(e)
else:raise AssertionError('Unverified interpolation accepted')
assert before==(len(bm.verts),len(bm.faces))
bm.loops.layers.uv.remove(uv)
try:x=view.x
except ReferenceError:pass
else:raise AssertionError('Removed layer view survived')
uv=bm.loops.layers.uv.new('New');view=face.loops[0][uv].uv
bm.free()
try:x=view.x
except ReferenceError:pass
else:raise AssertionError('Freed layer view survived')
'''))
    def test_custom_normals_and_invalid_publish_leave_target_unchanged(self):
        self.hb('run',self.script('''import bpy,bmesh
bpy.ops.mesh.primitive_cube_add();m=bpy.context.object.data
m.normals_split_custom_set([(.2,.3,1)]*24)
bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table();bm.verts[0].co.z+=1
before=[tuple(v.co) for v in m.vertices]
try:bm.to_mesh(m)
except Exception as e:assert 'unchanged geometry' in str(e)
else:raise AssertionError('Unverified packed-normal remapping accepted')
assert before==[tuple(v.co) for v in m.vertices] and m.has_custom_normals
bm.free()
plain=bpy.data.meshes.new('Plain');plain.from_pydata([(0,0,0)],[],[])
bm=bmesh.new();bm.verts.new((float('nan'),0,0))
try:bm.to_mesh(plain)
except Exception:pass
else:raise AssertionError('Nonfinite data published')
assert tuple(plain.vertices[0].co)==(0,0,0)
'''))

    def test_unverified_shape_and_strength_modifier_stacks_reject(self):
        for setup in ("o.shape_key_add(name='Basis')", "o.data.attributes.new(name='__mod_weightednormals_faceweight',type='INT',domain='FACE')"):
            self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\no=bpy.context.object\n"+setup), '--scene','guard.hb')
            before=(self.path/'guard.hb').read_bytes()
            self.hb('run',self.script("import bpy\no=bpy.context.object\no.modifiers.new('Array','ARRAY')\no.modifiers.new('Normals','WEIGHTED_NORMAL')"),'--scene','guard.hb','--out','invalid.glb',ok=False)
            self.assertEqual(before,(self.path/'guard.hb').read_bytes())
            (self.path/'guard.hb').unlink()
