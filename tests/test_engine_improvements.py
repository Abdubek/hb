"""Checker container ownership and thin-cuboid modifier regression tests."""
import unittest
import test_cli
from normalize import revision

class EngineImprovements(unittest.TestCase):
    setUp=test_cli.CLI.setUp
    tearDown=test_cli.CLI.tearDown
    hb=test_cli.CLI.hb
    script=test_cli.CLI.script

    def test_checker_isolates_comprehension_bindings(self):
        source=test_cli.ROOT/'compat/golden/m3_checker_comprehensions.py'
        self.hb('check',source)
        self.hb('run',source,'--out','comprehensions.glb')
        self.assertEqual(self.hb('query','stats')['result']['objects'],1)
        self.assertEqual((self.path/'comprehensions.glb').read_bytes()[:4],b'glTF')

    def test_checker_preserves_api_errors_across_comprehension_scopes(self):
        setup='''import bpy
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
material=bpy.data.materials.new('Paint');material.use_nodes=True
p=material.node_tree.nodes['Principled BSDF']
'''
        for expression,expected in (
            ('[p.unsupported_magic() for p in obj.data.polygons]','bpy.types.MeshPolygon.unsupported_magic'),
            ('{p.unsupported_magic() for p in obj.data.polygons}','bpy.types.MeshPolygon.unsupported_magic'),
            ('{p.index:p.unsupported_magic() for p in obj.data.polygons}','bpy.types.MeshPolygon.unsupported_magic'),
            ('any(p.unsupported_magic() for p in obj.data.polygons)','bpy.types.MeshPolygon.unsupported_magic'),
            ('[p for p in obj.data.polygons]\np.use_smooth=True','bpy.types.ShaderNode.use_smooth'),
            ('faces=[p for p in obj.data.polygons]\nfaces[0].unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces={p for p in obj.data.polygons}\nfor face in faces:face.unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces={p for p in obj.data.polygons}\nfaces.copy().pop().unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces={p.index:p for p in obj.data.polygons}\nfaces[0].unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces=(p for p in obj.data.polygons)\nfor face in faces:face.unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces=(p for p in obj.data.polygons)\nnext(faces).unsupported_magic()','bpy.types.MeshPolygon.unsupported_magic'),
            ('faces=(p for p in obj.data.polygons)\nnext(faces,bpy.context.object).unsupported_magic()','bpy.types.Object.unsupported_magic'),
            ('[p for p in p.unsupported_magic()]','bpy.types.ShaderNode.unsupported_magic'),
            ('for p in obj.data.polygons:pass\np.inputs','bpy.types.MeshPolygon.inputs'),
        ):
            with self.subTest(expression=expression):
                errors=self.hb('check',self.script(setup+expression),ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors),errors)

    def test_checker_accepts_vector_conversion_of_python_tuple_coordinates(self):
        source='''import bpy
from mathutils import Vector

def direction(start, end):
    start, end = Vector(start), Vector(end)
    delta = end - start
    assert delta.length == 1
    return delta.normalized()

for x in [0, 1]:
    vector = direction((x, 0, 0), (x + 1, 0, 0))
    assert tuple(vector) == (1, 0, 0)
    bpy.ops.mesh.primitive_cube_add(location=vector * x)
assert len(bpy.data.objects) == 2
'''
        script=self.script(source)
        self.hb('check',script)
        self.hb('run',script,'--out','converted.glb')
        self.assertEqual(self.hb('query','stats')['result']['objects'],2)
        self.assertEqual((self.path/'converted.glb').read_bytes()[:4],b'glTF')

    def test_checker_preserves_api_errors_alongside_python_tuple_values(self):
        cases=[
            ('''from mathutils import Vector
def direction(start, end):
    start, end = Vector(start), Vector(end)
    delta = end - start
    delta.unsupported_magic()
for x in [0, 1]:
    direction((x, 0, 0), (x + 1, 0, 0))
''','mathutils.Vector.unsupported_magic'),
            ('import bpy\nobjects=(bpy.context.object,)\nobjects.location',
             'bpy.context.object.location'),
            ('import bpy\nobjects=(bpy.context.object,)\nobjects[0].unsupported_magic()',
             'bpy.types.Object.unsupported_magic'),
        ]
        for source,expected in cases:
            with self.subTest(expected=expected):
                errors=self.hb('check',self.script(source),ok=False)['errors']
                self.assertTrue(any(expected in error['message'] for error in errors),errors)

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
