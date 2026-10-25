import unittest
import test_cli
from normalize import revision
class ObjectOps(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_creation_and_persistent_display(self):
        self.hb('run',self.script('''import bpy
bpy.ops.object.camera_add(location=(4,-6,4),rotation=(1.1,0,.6))
cam=bpy.context.object;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',radius=3,location=(2,-2,4))
assert bpy.context.object.data.size==3
bpy.ops.object.empty_add(type='ARROWS',radius=2)
o=bpy.context.object;o.name='Rig';o.empty_display_size=5
copy=o.copy();bpy.context.collection.objects.link(copy);copy.name='Copy'
assert copy.empty_display_size==5 and copy.empty_display_type=='ARROWS'
assert len(bpy.context.selected_objects)==2
'''))
        self.hb('run',self.script("import bpy\nassert bpy.data.objects['Rig'].empty_display_size==5\nassert bpy.data.objects['Copy'].empty_display_type=='ARROWS'"))
        self.assertEqual(self.hb('render','--views','camera','--size','32')['render']['views'],['camera'])
    def test_dimensions_evaluated_and_parented(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;mod=o.modifiers.new('Array','ARRAY');mod.count=3
assert tuple(o.dimensions)==(6,2,2)
o.dimensions=(12,4,6)
assert tuple(o.scale)==(2,2,3) and tuple(o.dimensions)==(12,4,6)
bpy.ops.object.empty_add();p=bpy.context.object;p.scale=(2,3,4);o.parent=p
assert tuple(o.dimensions)==(24,12,24)
o.dimensions=(6,2,2)
assert tuple(o.scale)==(1,1,1) and tuple(o.dimensions)==(12,6,8)
o.dimensions.x=24
assert tuple(o.dimensions)==(48,18,32)
'''))
    def test_invalid_creation_is_atomic(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        for source in ("bpy.ops.object.camera_add(enter_editmode=True)","bpy.ops.object.light_add(type='HEMI')","bpy.ops.object.empty_add(type='IMAGE')","bpy.ops.object.camera_add(align='VIEW')","bpy.context.object.dimensions=(1,float('inf'),2)"):
            self.hb('run',self.script('import bpy\n'+source),ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        for source in ("bpy.ops.object.empty_add(type='IMAGE')","bpy.ops.object.camera_add(align='VIEW')","bpy.ops.object.light_add(enter_editmode=True)"):
            self.hb('check',self.script('import bpy\n'+source),ok=False)
