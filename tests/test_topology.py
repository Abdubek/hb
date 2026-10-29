import unittest,json,struct
import test_cli
from normalize import revision

class Topology(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_bmesh_adjacency_checker_preserves_element_types(self):
        source=(test_cli.ROOT/'compat/golden/m3_bmesh_adjacency.py').read_text()
        self.hb('check',self.script(source))
        for expression,expected in (
            ('vertex.link_edges[0].unsupported_magic()', 'bmesh.types.BMEdge.unsupported_magic'),
            ('vertex.link_faces[0].unsupported_magic()', 'bmesh.types.BMFace.unsupported_magic'),
            ('edge.link_faces[0].unsupported_magic()', 'bmesh.types.BMFace.unsupported_magic'),
            ('vertex.link_faces.clear()', 'bmesh.types.BMVert.link_faces.clear'),
        ):
            with self.subTest(expression=expression):
                script=self.script('import bmesh\nbm=bmesh.new()\nvertex=bm.verts.new((0,0,0))\nedge=bm.edges.new((vertex,bm.verts.new((1,0,0))))\n'+expression)
                errors=self.hb('check',script,ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors),errors)

    def test_bmesh_adjacency_views_are_readonly_and_invalidate(self):
        self.hb('run',self.script('''import bmesh
bm=bmesh.new();a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0));c=bm.verts.new((0,1,0))
face=bm.faces.new((a,b,c));edge=next(e for e in bm.edges if set(e.verts)=={a,b})
vertex_edges=a.link_edges;vertex_faces=a.link_faces;edge_faces=edge.link_faces
try:vertex_faces[0]=face
except TypeError:pass
else:raise AssertionError('Adjacency item assignment accepted')
assert len(vertex_faces)==1
for view in (vertex_edges,vertex_faces,edge_faces):
    try:view[100]
    except IndexError:pass
    else:raise AssertionError('Invalid adjacency index accepted')
bm.edges.remove(edge)
try:len(edge_faces)
except ReferenceError:pass
else:raise AssertionError('Removed edge view accepted')
bm.verts.remove(a)
for view in (vertex_edges,vertex_faces):
    for read in (lambda:len(view),lambda:list(view),lambda:view[:],lambda:face in view):
        try:read()
        except ReferenceError:pass
        else:raise AssertionError('Removed vertex view accepted')
held=b.link_edges
bm.free()
try:len(held)
except ReferenceError:pass
else:raise AssertionError('Freed BMesh view accepted')
'''))

    def test_stack_evaluation_apply_and_restore(self):
        first=self.hb('run',self.script('''import bpy,bmesh
bm=bmesh.new();result=bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)
bmesh.ops.translate(bm,verts=result['verts'],vec=(1,0,0))
m=bpy.data.meshes.new('Panel');bm.to_mesh(m);bm.free()
o=bpy.data.objects.new('Panel',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
a=o.modifiers.new('Mirror','MIRROR');s=o.modifiers.new('Shell','SOLIDIFY');s.thickness=.5
t=o.modifiers.new('Triangles','TRIANGULATE');t.quad_method='FIXED'
'''))['revision']
        scene=revision(self.path/'scene.hb')['scene']
        self.assertEqual(len(scene['meshes'][0]['vertices']),4)
        self.assertEqual(len(scene['meshes'][0]['faces']),1)
        self.assertEqual(self.hb('query','bbox','Panel')['result']['bbox']['min'],[-2.,-1.,-.5])
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],20)
        self.hb('export','stack.glb');self.hb('import','stack.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],20)
        self.hb('run',self.script("import bpy\nfor name in ('Mirror','Shell','Triangles'):bpy.ops.object.modifier_apply(modifier=name)"))
        applied=revision(self.path/'scene.hb')['scene']
        self.assertEqual(len(applied['meshes'][0]['faces']),20)
        self.assertEqual(applied['objects'][0]['modifiers'],[])
        self.hb('export','applied.glb')
        def chunks(path):
            data=path.read_bytes();size=struct.unpack_from('<I',data,12)[0]
            doc=json.loads(data[20:20+size])
            # Transient evaluated meshes receive a unique datablock name.
            for mesh in doc['meshes']:mesh.pop('name',None)
            return doc,data[20+size:]
        self.assertEqual(chunks(self.path/'stack.glb'),chunks(self.path/'applied.glb'))
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['faces']),1)
    def test_unsupported_topology_is_transactional(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_plane_add()'))
        before=(self.path/'scene.hb').read_bytes()
        cases=["m=bpy.context.object.modifiers.new('m','TRIANGULATE');m.quad_method='UNKNOWN'",
               "bpy.context.object.data.from_pydata([(0,0,0),(2,0,0),(3,1,1),(1,2,0),(0,1,0)],[],[(0,1,2,3,4)]);m=bpy.context.object.modifiers.new('m','TRIANGULATE');m.ngon_method='CLIP';bpy.ops.object.modifier_apply(modifier='m')",
               "bpy.context.object.data.normals_split_custom_set([(0,0,1)]*4);m=bpy.context.object.modifiers.new('m','SOLIDIFY');bpy.ops.object.modifier_apply(modifier='m')"]
        for source in cases:
            with self.subTest(source=source):
                self.hb('run',self.script('import bpy\n'+source),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
    def test_primitive_options_and_handles(self):
        self.hb('run',self.script('''import bmesh
bm=bmesh.new();v=bm.verts.new((9,9,9));result=bmesh.ops.create_cube(bm,size=2)
assert len(result['verts'])==8 and v not in result['verts']
for action,expected in ((lambda:bmesh.ops.create_grid(bm,calc_uvs=True),'UnsupportedError'),(lambda:bmesh.ops.create_cube(bm,matrix=None),'TypeError')):
 try:action()
 except Exception as error:assert type(error).__name__==expected
 else:raise AssertionError('unsupported option accepted')
assert len(bm.verts)==9
bm.free()
try:bmesh.ops.create_cube(bm)
except ReferenceError:pass
else:raise AssertionError('freed BMesh accepted')
'''))

if __name__=='__main__':unittest.main()
