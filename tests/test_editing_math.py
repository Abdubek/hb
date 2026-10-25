import unittest
import test_cli

class EditingMath(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_space_transform_and_validation_before_mutation(self):
        self.hb('run',self.script('''import bmesh
from mathutils import Matrix
bm=bmesh.new();v=bm.verts.new((2,3,4));untouched=bm.verts.new((7,8,9))
assert bmesh.ops.scale(bm,verts=[v],vec=(2,3,4),space=Matrix.Translation((10,20,30))) is None
assert tuple(v.co)==(14,49,106) and tuple(untouched.co)==(7,8,9)
for matrix in (Matrix.Identity(2),):
    try:bmesh.ops.transform(bm,verts=[v],matrix=matrix)
    except TypeError:pass
    else:raise AssertionError('Invalid matrix accepted')
    assert tuple(v.co)==(14,49,106)
try:bmesh.ops.rotate(bm,verts=[v],space=Matrix.Scale(0,4))
except Exception:pass
else:raise AssertionError('Singular transform space accepted')
assert tuple(v.co)==(14,49,106)
try:bmesh.ops.translate(bm,verts=[v,v],vec=(1,2,3))
except ValueError:pass
else:raise AssertionError('Duplicate vertex accepted')
assert tuple(v.co)==(14,49,106)
other=bmesh.new();foreign=other.verts.new((1,2,3))
try:bmesh.ops.translate(bm,verts=[v,foreign],vec=(1,2,3))
except ValueError:pass
else:raise AssertionError('Foreign vertex accepted')
assert tuple(v.co)==(14,49,106)
bm.free();other.free()
'''))

    def test_color_hdr_hsv_freezing_and_conversions(self):
        self.hb('run',self.script('''from mathutils import Color
c=Color((-1,2,3));c.v=1
assert max(abs(x-y) for x,y in zip(c,(-1/3,2/3,1)))<1e-5
c.hsv=(-.2,2,3);assert tuple(c)==(1,0,0)
a=Color((.2,.5,.8));b=a.copy();b.r=2;assert a.r<.3
f=a.copy().freeze()
try:f[:]=(1,2,3)
except TypeError:pass
else:raise AssertionError('Frozen mutation accepted')
assert tuple(f)==tuple(a) and hash(f)==hash(a.copy().freeze())
assert not f.copy().is_frozen
for x,y in zip(Color((-.5,.1,2)).from_scene_linear_to_srgb(),(0,.349176377,1.353277802)):
    assert abs(x-y)<1e-5
try:a/0
except ZeroDivisionError:pass
else:raise AssertionError('Division by zero accepted')
'''))

    def test_node_identity_and_whole_image_pixels(self):
        self.hb('run',self.script('''import bpy
m=bpy.data.materials.new('Finish');m.use_nodes=True
nodes={n.type:n for n in m.node_tree.nodes}
assert nodes['BSDF_PRINCIPLED'].bl_idname=='ShaderNodeBsdfPrincipled'
i=bpy.data.images.new('Paint',width=1,height=1,float_buffer=True)
assert i.colorspace_settings.name=='Linear Rec.709'
i.pixels=(.25,.5,.75,1);assert tuple(i.pixels)==(.25,.5,.75,1)
try:i.pixels=(1,2,3)
except ValueError:pass
else:raise AssertionError('Incomplete pixel data accepted')
assert tuple(i.pixels)==(.25,.5,.75,1)
'''))
