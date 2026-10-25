import unittest
import test_cli
from normalize import revision
class RoundPrimitives(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_sphere_index_contract_and_render(self):
        source='''import bpy
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1)
o=bpy.context.object;o.name='Globe'
assert tuple(o.data.vertices[0].co)==(0,0,1)
assert tuple(o.data.vertices[-1].co)==(0,0,-1)
bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.5,radius2=0,depth=1,location=(0,0,-1.5))
'''
        p=self.script(source);self.hb('check',p);a=self.hb('run',p,'--out','round.glb')
        b=self.hb('run',p,'--scene','duplicate.hb')
        self.assertEqual(a['revision'],b['revision'])
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],58)
        self.hb('import','round.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],58)
        bbox=self.hb('query','bbox','Globe')['result']['bbox']
        # Blender 4.5's iterative float32 spin does not produce exact unit X/Y bounds.
        self.assertEqual(bbox['min'],[-0.9999998807907104,-0.9999998807907104,-1.0])
        self.assertEqual(bbox['max'],[0.9999999403953552,0.9999998807907104,1.0])
    def test_bmesh_new_vertex_scope(self):
        self.hb('run',self.script('''import bpy,bmesh
bm=bmesh.new();sentinel=bm.verts.new((9,9,9))
sphere=bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=4,radius=1)
bmesh.ops.translate(bm,verts=sphere['verts'],vec=(0,0,2))
assert tuple(sentinel.co)==(9,9,9)
assert len(sphere['verts'])==26
bm.normal_update();mesh=bpy.data.meshes.new('Globe');bm.to_mesh(mesh)
obj=bpy.data.objects.new('Globe',mesh);bpy.context.collection.objects.link(obj)
bm.free()
assert not sphere['verts'][0].is_valid
'''))
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),27)
    def test_invalid_construction_rolls_back(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        cases=["bpy.ops.mesh.primitive_uv_sphere_add(radius=0)","bpy.ops.mesh.primitive_uv_sphere_add(segments=1000,ring_count=1000)","bpy.ops.mesh.primitive_cone_add(radius1=float('nan'))","bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=True)","bmesh.ops.create_uvsphere(bmesh.new(),u_segments=8,v_segments=4,radius=1,calc_uvs=True)","bmesh.ops.create_circle(bmesh.new(),segments=8,radius=1,matrix=None)"]
        for source in cases:
            with self.subTest(source=source):
                self.hb('run',self.script('import bpy,bmesh\n'+source),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
