import unittest
import test_cli
from normalize import revision
from png import rgba
class WorldLights(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_world_persistence_users_and_undo(self):
        first=self.hb('run',self.script('''import bpy
w=bpy.data.worlds.new('Studio');w.color=(.2,.3,.4);bpy.context.scene.world=w
assert w.users==1 and bpy.data.worlds['World'].users==0
'''))
        changed=self.hb('run',self.script("import bpy\nbpy.data.worlds.remove(bpy.context.scene.world)\nassert bpy.context.scene.world is None"))
        self.assertEqual(changed['changes']['worlds']['deleted'],['Studio'])
        self.assertEqual(first['revision'],self.hb('undo')['revision'])
        self.hb('run',self.script("import bpy\nassert bpy.context.scene.world.name=='Studio'\nassert bpy.context.scene.world.users==1"))
    def test_constant_world_changes_background(self):
        self.hb('run',self.script("import bpy\nw=bpy.context.scene.world\nw.use_nodes=False\nw.color=(.3,0,0)"))
        self.hb('render','--views','front','--size','32','--out','red.png')
        _,_,pixels=rgba((self.path/'red.png').read_bytes());r,g,b,a=pixels[0][0]
        self.assertGreater(r,20);self.assertEqual((g,b,a),(0,0,255))
        self.hb('run',self.script("import bpy\nbpy.context.scene.world.color=(0,0,.3)"))
        self.hb('render','--views','front','--size','32','--out','blue.png')
        _,_,pixels=rgba((self.path/'blue.png').read_bytes());r,g,b,a=pixels[0][0]
        self.assertGreater(b,20);self.assertEqual((r,g,a),(0,0,255))
    def test_area_shapes_and_shadow_toggle(self):
        self.hb('run',self.script('''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_plane_add(size=8)
bpy.ops.mesh.primitive_cube_add(location=(0,0,1))
bpy.ops.object.light_add(type='AREA',radius=2,location=(2,-3,5))
o=bpy.context.object;o.name='Softbox';o.data.shape='RECTANGLE';o.data.size_y=4
assert o.data.size_y==4
o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
'''))
        self.hb('render','--views','iso','--size','64','--out','shadow.png')
        self.hb('run',self.script("import bpy\nbpy.data.objects['Softbox'].data.use_shadow=False"))
        self.hb('render','--views','iso','--size','64','--out','plain.png')
        self.assertNotEqual((self.path/'shadow.png').read_bytes(),(self.path/'plain.png').read_bytes())
        self.hb('run',self.script("import bpy\nbpy.data.objects['Softbox'].data.shape='ELLIPSE'"))
        self.hb('render','--views','iso','--size','64','--out','ellipse.png')
        self.assertNotEqual((self.path/'plain.png').read_bytes(),(self.path/'ellipse.png').read_bytes())
    def test_excluded_graphs_and_wrong_light_fields_rollback(self):
        self.hb('run',self.script("import bpy\nbpy.ops.object.light_add(type='POINT')"))
        before=(self.path/'scene.hb').read_bytes()
        for source in ("bpy.context.scene.world.node_tree.nodes.new('ShaderNodeTexSky')","bpy.context.object.data.shape='DISK'","bpy.context.scene.world.color=(1,2)"):
            self.hb('run',self.script('import bpy\n'+source),ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
