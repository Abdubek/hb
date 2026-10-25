import json,struct,unittest
import test_cli
from normalize import revision
from weld_check import compare,random_script,face_script

class Weld(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_closing_edges_and_pinched_face_uv_interpolation(self):
        reference=json.loads((test_cli.ROOT/'compat/fixtures/weld-face-reference.json').read_text())
        self.hb('run',self.script(face_script(reference)))
        compare(reference,revision(self.path/'scene.hb')['scene'])

    def test_56_blender_modes_collapse_uv_and_weight_cases(self):
        self.hb('run',test_cli.ROOT/'compat/weld_probe.py')
        compare(json.loads((test_cli.ROOT/'compat/fixtures/weld-reference.json').read_text()),revision(self.path/'scene.hb')['scene'])

    def test_160_random_blender_chain_and_mask_cases(self):
        reference=json.loads((test_cli.ROOT/'compat/fixtures/weld-random-reference.json').read_text())
        self.hb('run',self.script(random_script(reference)))
        compare(reference,revision(self.path/'scene.hb')['scene'])

    def test_stack_apply_export_and_revision_restore(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add(size=2)
o=bpy.context.object;o.name='Strip'
a=o.modifiers.new('Tiles','ARRAY');a.count=4
w=o.modifiers.new('Seams','WELD')
s=o.modifiers.new('Shell','SOLIDIFY');s.thickness=.2
'''),'--out','stack.glb')['revision']
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),4)
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],36)
        self.hb('run',self.script("import bpy\nfor name in ('Tiles','Seams','Shell'):bpy.ops.object.modifier_apply(modifier=name)"),'--out','applied.glb')
        scene=revision(self.path/'scene.hb')['scene']
        self.assertEqual(len(scene['meshes'][0]['vertices']),20)
        self.assertEqual(len(scene['meshes'][0]['faces']),18)
        self.assertEqual(scene['objects'][0]['modifiers'],[])
        def chunks(path):
            data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n])
            for mesh in doc['meshes']:mesh.pop('name',None)
            return doc,data[20+n:]
        self.assertEqual(chunks(self.path/'stack.glb'),chunks(self.path/'applied.glb'))
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),4)

    def test_visibility_export_uses_viewport_and_preview_uses_render(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add(size=2)
o=bpy.context.object;a=o.modifiers.new('Tiles','ARRAY');a.count=2
w=o.modifiers.new('Seams','WELD');w.show_viewport=False
s=o.modifiers.new('Shell','SOLIDIFY');s.thickness=.2
'''))
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],20)
        self.hb('export','viewport.glb');self.hb('import','viewport.glb','--scene','view.hb')
        self.assertEqual(self.hb('query','stats','--scene','view.hb')['result']['triangles'],24)
        self.hb('run',self.script("import bpy\nw=bpy.context.object.modifiers['Seams'];w.show_viewport=True;w.show_render=False"))
        self.assertEqual(self.hb('render','--size','64','--views','iso')['render']['triangles'],24)
        self.hb('export','welded.glb');self.hb('import','welded.glb','--scene','welded.hb')
        self.assertEqual(self.hb('query','stats','--scene','welded.hb')['result']['triangles'],20)

    def test_unsupported_topology_and_settings_rollback(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_plane_add()'))
        before=(self.path/'scene.hb').read_bytes()
        cases=[
            "m=bpy.context.object.modifiers.new('W','WELD');m.mode='UNKNOWN'",
            "m=bpy.context.object.modifiers.new('W','WELD');m.merge_threshold=1e30;bpy.ops.object.modifier_apply(modifier='W')",
            "bpy.context.object.data.normals_split_custom_set([(0,0,1)]*4);m=bpy.context.object.modifiers.new('W','WELD');m.merge_threshold=4;bpy.ops.object.modifier_apply(modifier='W')",
        ]
        for source in cases:
            with self.subTest(source=source):
                result=self.hb('run',self.script('import bpy\n'+source),ok=False)
                self.assertIn('WELD',result['error']['message'].upper())
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_checker_and_stale_handles(self):
        for assignment in ("mode='CONNECTED'","vertex_group='Mask'","invert_vertex_group=True","loose_edges=True"):
            self.hb('check',self.script("import bpy\nw=bpy.context.object.modifiers.new('W','WELD');w."+assignment))
        script=self.script('''import bpy
bpy.ops.mesh.primitive_plane_add()
o=bpy.context.object;w=o.modifiers.new('W','WELD');w.merge_threshold=.002
o.modifiers.remove(w)
try:w.merge_threshold=.1
except ReferenceError:pass
else:raise AssertionError('Removed modifier must be invalid')
o.modifiers.new('W','WELD')
''')
        self.hb('check',script);self.hb('run',script)

    def test_shared_mesh_rejection_and_copy_isolation(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add()
o=bpy.context.object;a=o.modifiers.new('Tiles','ARRAY');a.count=2
o.modifiers.new('W','WELD')
other=o.copy();bpy.context.collection.objects.link(other)
'''))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Tiles')"),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script("import bpy\nbpy.context.object.data=bpy.context.object.data.copy()\nfor name in ('Tiles','W'):bpy.ops.object.modifier_apply(modifier=name)"))
        meshes=revision(self.path/'scene.hb')['scene']['meshes']
        self.assertEqual(sorted(len(m['vertices']) for m in meshes),[4,6])

    def test_hash_determinism_and_loose_edge_remap(self):
        script=self.script('''import bpy
m=bpy.data.meshes.new('Wires');m.from_pydata([(0,0,0),(.1,0,0),(1,0,0),(1.1,0,0)],[(0,1),(0,2),(1,3),(2,3)],[])
o=bpy.data.objects.new('Wires',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('W','WELD');w.merge_threshold=.15
bpy.ops.object.modifier_apply(modifier='W')
assert len(m.vertices)==2 and len(m.edges)==1
''')
        a=self.hb('run',script);b=self.hb('run',script,'--scene','again.hb')
        self.assertEqual(a['revision'],b['revision'])

    def test_threshold_equality_and_zero_are_noops(self):
        self.hb('run',self.script('''import bpy
for threshold in (0,.125):
 m=bpy.data.meshes.new('Points');m.from_pydata([(0,0,0),(.125,0,0)],[],[])
 o=bpy.data.objects.new('Points',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
 w=o.modifiers.new('W','WELD');w.merge_threshold=threshold
 bpy.ops.object.modifier_apply(modifier='W');assert len(m.vertices)==2
'''))
