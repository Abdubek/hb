import unittest
import test_cli

class ObjectEuler(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_all_mode_transitions_against_blender(self):
        self.hb('check',test_cli.ROOT/'compat/object_euler_probe.py')
        self.hb('run',test_cli.ROOT/'compat/object_euler_probe.py')

    def test_live_order_and_atomic_rejection(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object;view=o.rotation_euler
o.rotation_mode='ZYX';assert view.order=='ZYX'
view.x=.3;assert abs(o.rotation_euler.x-.3)<1e-6
copy=view.copy();assert copy.order=='ZYX'
o.rotation_mode='XZY';assert view.order=='XZY' and copy.order=='ZYX'
before=tuple(o.rotation_euler)
try:o.rotation_mode='AXIS_ANGLE'
except Exception:pass
else:raise AssertionError('Unlisted mode accepted')
assert o.rotation_mode=='XZY' and tuple(o.rotation_euler)==before
try:view.order='XYZ'
except Exception:pass
else:raise AssertionError('Unlisted view mutation accepted')
assert o.rotation_mode=='XZY' and tuple(o.rotation_euler)==before
"""))
