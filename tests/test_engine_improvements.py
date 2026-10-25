"""Checker container ownership and thin-cuboid modifier regression tests."""
import unittest
import test_cli
from normalize import revision

class EngineImprovements(unittest.TestCase):
    setUp=test_cli.CLI.setUp
    tearDown=test_cli.CLI.tearDown
    hb=test_cli.CLI.hb
    script=test_cli.CLI.script

    def test_list_methods_do_not_become_object_methods(self):
        for operation in [
            'parts=[bpy.context.object]\nparts.clear()',
            'parts=[]\nparts.append(bpy.context.object)\nparts.clear()',
            'def clear(items):\n    alias=items\n    alias.clear()\nparts=[bpy.context.object]\nclear(parts)',
            'parts=[]\nalias=parts\nalias.append(bpy.context.object)\nparts.clear()',
        ]:
            self.hb('check',self.script('import bpy\n'+operation))
        for operation in [
            'parts=[bpy.context.object]\nparts[0].clear()',
            'parts=[]\nalias=parts\nalias.append(bpy.context.object)\nparts[0].clear()',
            'def fill(items):\n    items.append(bpy.context.object)\nparts=[]\nfill(parts)\nparts[0].clear()',
            'parts=[bpy.context.object]\nparts.pop().clear()',
        ]:
            errors=self.hb('check',self.script('import bpy\n'+operation),ok=False)['errors']
            self.assertTrue(any('Object.clear' in e['message'] for e in errors),errors)

    def test_thin_clamp_rejects_before_mesh_mutation(self):
        source='''import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
o.dimensions=(2,1,0.002)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=o.modifiers.new('Bevel','BEVEL');m.width=.08;m.segments=2;m.use_clamp_overlap=True
before=[tuple(v.co) for v in o.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:
    assert 'half-thickness limit' in str(error)
    assert 'degenerate' in str(error)
else:raise AssertionError('Numerically collapsed clamp was accepted')
assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
m.width=.0008
bpy.ops.object.modifier_apply(modifier=m.name)
'''
        self.hb('run',self.script(source))
        review=self.hb('review','--size','128','--out','review.json')
        self.assertEqual(review['review']['diagnostics']['errors'],0)

if __name__=='__main__':unittest.main()
