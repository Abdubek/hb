import unittest,json,zlib
import test_cli
from normalize import revision

class Assembly(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script

    def test_torus_roundtrip_and_determinism(self):
        script=self.script('''import bpy
bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=8,mode='EXT_INT',abso_major_rad=2,abso_minor_rad=1)
bpy.context.object.name='Wheel'
bpy.ops.object.shade_smooth()
''')
        self.hb('check',script)
        first=self.hb('run',script,'--out','wheel.glb')
        again=self.hb('run',script,'--scene','again.hb')
        self.assertEqual(first['revision'],again['revision'])
        self.assertEqual(self.hb('render','--views','iso','--size','64')['render']['triangles'],192)
        bbox=self.hb('query','bbox','Wheel')['result']['bbox']
        for actual,expected in zip(bbox['dimensions'],[4,4,1]):self.assertAlmostEqual(actual,expected,places=5)
        self.hb('import','wheel.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],192)

    def test_torus_rejections_and_keyword_checker(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        for options in ('major_radius=.2,minor_radius=.3',"mode='EXT_INT',abso_major_rad=1,abso_minor_rad=2", "major_radius=float('nan')", "align='VIEW'"):
            with self.subTest(options=options):
                self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_torus_add('+options+')'),ok=False)
                self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        for options in ('calc_uvs=False','enter_editmode=False','scale=(1,1,1)'):
            self.hb('check',self.script('import bpy\nbpy.ops.mesh.primitive_torus_add('+options+')'),ok=False)
        self.hb('check',self.script('from bpy import ops\nops.mesh.primitive_torus_add(generate_uvs=False)'))

    def test_join_preserves_bounds_and_revision(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=8,location=(1,2,3),rotation=(.2,.3,.4))
a=bpy.context.object;a.name='Ring';a.scale=(2,.7,1.4)
bpy.ops.mesh.primitive_cube_add(location=(3,0,1),rotation=(.3,.2,.1))
bpy.context.object.name='Block'
a.select_set(True);bpy.context.view_layer.objects.active=a
'''))['revision']
        before=self.hb('query','bbox','--all')['result']
        self.hb('run',self.script("import bpy\nassert bpy.ops.object.join()=={'FINISHED'}"),'--out','joined.glb')
        joined=revision(self.path/'scene.hb')['scene']
        self.assertEqual([o['name'] for o in joined['objects']],['Ring'])
        self.assertEqual(len(joined['meshes']),2)
        bounds=self.hb('query','bbox','Ring')['result']['bbox']
        boxes=[x['bbox'] for x in before['objects']]
        for field,fn in [('min',min),('max',max)]:
            for axis,value in enumerate(bounds[field]):self.assertAlmostEqual(value,fn(x[field][axis] for x in boxes),places=5)
        self.hb('import','joined.glb','--scene','imported.hb')
        self.assertEqual(self.hb('query','stats','--scene','imported.hb')['result']['triangles'],204)
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['objects']),2)

    def test_join_prevalidates_every_source(self):
        for change in ("b.modifiers.new('Repeat','ARRAY')",):
            with self.subTest(change=change):
                # A separate scene keeps each rejection independent.
                scene='reject'+str(len(change))+'.hb'
                self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object
bpy.ops.mesh.primitive_cube_add();b=bpy.context.object
'''+change+'''\na.select_set(True);bpy.context.view_layer.objects.active=a
'''),'--scene',scene)
                before=(self.path/scene).read_bytes()
                self.hb('run',self.script('import bpy\nbpy.ops.object.join()'),'--scene',scene,ok=False)
                self.assertEqual((self.path/scene).read_bytes(),before)

    def test_join_requires_active_selection_and_cancels_single_mesh(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\nassert bpy.ops.object.join()=={'CANCELLED'}"))
        self.hb('run',self.script('import bpy\nbpy.context.object.select_set(False)'))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script('import bpy\nbpy.ops.object.join()'),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_first_uv_layer_initialization(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add(calc_uvs=False)
m=bpy.context.object.data
layer=m.uv_layers.new()
assert [tuple(v.uv) for v in layer.data][:4]==[(0,0),(1,0),(1,1),(0,1)]
blank=m.uv_layers.new(name='Blank',do_init=False)
m.uv_layers.active=blank
copy=m.uv_layers.new(name='Copy')
assert all(tuple(v.uv)==(0,0) for v in copy.data)
'''))

    def test_join_export_uses_material_slot_order(self):
        self.hb('run',self.script('''import bpy
red=bpy.data.materials.new('Red');blue=bpy.data.materials.new('Blue')
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object
a.data.materials.append(blue);a.data.materials.append(red);a.data.polygons[0].material_index=1
bpy.ops.mesh.primitive_cube_add(location=(3,0,0))
a.select_set(True);bpy.context.view_layer.objects.active=a
bpy.ops.object.join()
'''),'--out','slots.glb')
        import json,struct
        data=(self.path/'slots.glb').read_bytes();size=struct.unpack_from('<I',data,12)[0]
        doc=json.loads(data[20:20+size])
        names=[doc['materials'][p['material']]['name'] if 'material' in p else None for p in doc['meshes'][0]['primitives']]
        self.assertEqual(names,['Blue','Red',None])

    def test_hierarchy_reflection_and_shared_blender_references(self):
        references=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/assembly-reference.json.zlib').read_bytes()))
        script=self.script('references='+repr(references)+'\n'+(test_cli.ROOT/'compat/assembly_probe.py').read_text())
        self.hb('check',script)
        self.hb('run',script)

    def test_apply_prevalidates_all_shared_groups(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add();first=bpy.context.object;first.location=(2,3,4)
bpy.ops.mesh.primitive_cube_add();second=bpy.context.object;second.scale=(2,3,4)
shared=bpy.data.objects.new('Unselected',second.data);bpy.context.collection.objects.link(shared)
first.select_set(True);bpy.context.view_layer.objects.active=first
before=[tuple(v.co) for v in first.data.vertices];data=second.data
try:bpy.ops.object.transform_apply()
except Exception:pass
else:raise AssertionError('Partially selected shared data accepted')
assert tuple(first.location)==(2,3,4) and [tuple(v.co) for v in first.data.vertices]==before
assert second.data==data and len(bpy.data.meshes)==2
bpy.ops.object.transform_apply(isolate_users=True)
assert second.data!=shared.data and shared.data==data
assert tuple(first.location)==(0,0,0)
"""))
