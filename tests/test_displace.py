import json,zlib,struct
import unittest
import test_cli
from normalize import revision
from displace_extensions_check import compare

class Displace(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_thousand_blender_texture_samples(self):
        fixture=str(test_cli.ROOT/'compat/fixtures/cell_noise.json')
        self.hb('run',self.script(f'''import bpy,json
tex=bpy.data.textures.new('Noise',type='CLOUDS');tex.noise_basis='CELL_NOISE'
rows=json.load(open({fixture!r}))
for r in rows:
    tex.noise_depth=r['depth'];tex.noise_scale=r['scale'];tex.noise_type='HARD_NOISE' if r['hard'] else 'SOFT_NOISE';tex.intensity=r['intensity'];tex.contrast=r['contrast']
    value=tex.evaluate(r['position'])
    assert tuple(value[:3])==(0,0,0)
    assert value[3]==r['value'],(r,value[3])
'''))
    def test_shared_texture_removal_and_revision_restore(self):
        first=self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add()
o=bpy.context.object;o.name='Surface'
t=bpy.data.textures.new('Cells',type='CLOUDS');t.noise_basis='CELL_NOISE'
m=o.modifiers.new('Noise','DISPLACE');m.texture=t
copy=o.copy();bpy.context.collection.objects.link(copy)
assert t.users==2
'''))['revision']
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\nbpy.data.textures.remove(bpy.data.textures['Cells'],do_unlink=False)"),ok=False)
        self.assertEqual(before,(self.path/'scene.hb').read_bytes())
        self.hb('run',self.script("import bpy\nbpy.data.textures.remove(bpy.data.textures['Cells'])\nassert len(bpy.data.textures)==0\nassert all(o.modifiers[0].texture is None for o in bpy.data.objects)"),'--out','uniform.glb')
        self.hb('import','uniform.glb','--scene','uniform.hb')
        meshes=revision(self.path/'uniform.hb')['scene']['meshes']
        self.assertTrue(all(abs(v[2]-.5)<1e-6 for mesh in meshes for v in mesh['vertices']))
        self.hb('checkout',first)
        self.hb('run',self.script("import bpy\nassert bpy.data.textures['Cells'].users==2"))
    def test_texture_edits_re_evaluate_and_apply_preserves_uvs(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_plane_add()
t=bpy.data.textures.new('Cells',type='CLOUDS');t.noise_basis='CELL_NOISE';t.noise_depth=0
o=bpy.context.object;m=o.modifiers.new('Noise','DISPLACE');m.texture=t;m.direction='Z'
'''),'--out','first.glb')
        self.hb('run',self.script("import bpy\nbpy.data.textures['Cells'].intensity=1.5"),'--out','second.glb')
        self.assertNotEqual((self.path/'first.glb').read_bytes(),(self.path/'second.glb').read_bytes())
        before=revision(self.path/'scene.hb')['scene']['meshes'][0]['uv_layers']
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Noise')"))
        after=revision(self.path/'scene.hb')['scene']
        self.assertEqual(before,after['meshes'][0]['uv_layers'])
        self.assertFalse(after['objects'][0]['modifiers'])
    def test_unsupported_modes_fail_and_rollback(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_plane_add()\nbpy.context.object.modifiers.new('Noise','DISPLACE')"))
        before=(self.path/'scene.hb').read_bytes()
        for source in ("m.space='GLOBAL'","m.direction='RGB_TO_XYZ'","m.texture_coords='UV'","m.texture=bpy.data.textures.new('Legacy',type='CLOUDS')","t=bpy.data.textures.new('Image',type='IMAGE')","t=bpy.data.textures.new('Cell',type='CLOUDS');t.noise_basis='CELL_NOISE';t.noise_depth=30;t.evaluate((1e6,0,0))"):
            with self.subTest(source=source):
                self.hb('run',self.script("import bpy\nm=bpy.context.object.modifiers['Noise']\n"+source),ok=False)
                self.assertEqual(before,(self.path/'scene.hb').read_bytes())
        self.hb('check',self.script("import bpy\nbpy.data.textures.new('Image',type='IMAGE')"),ok=False)
        self.hb('check',self.script("import bpy\nt=bpy.data.textures.new('Cell',type='CLOUDS');t.noise_basis='CELL_NOISE'"))

    def test_groups_and_custom_normals_match_96_blender_cases(self):
        self.hb('check',test_cli.ROOT/'compat/golden/m3_displace.py')
        self.hb('run',test_cli.ROOT/'compat/displace_extensions_probe.py')
        reference=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/displace-reference.json.zlib').read_bytes()))
        compare(reference,revision(self.path/'scene.hb')['scene'])

    def test_group_stack_export_and_apply_preserve_memberships(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
g=o.vertex_groups.new(name='Mask');g.add([0,1],.25,'REPLACE');g.add([3],1,'REPLACE')
o.data.normals_split_custom_set([(.2,.3,1)]*24)
m=o.modifiers.new('Displace','DISPLACE');m.strength=.4;m.vertex_group='Mask';m.invert_vertex_group=True
"""),'--out','stack.glb')
        before=revision(self.path/'scene.hb')['scene']['meshes'][0]['deform_weights']
        self.hb('run',self.script("import bpy\nbpy.ops.object.modifier_apply(modifier='Displace')"),'--out','applied.glb')
        after=revision(self.path/'scene.hb')['scene']['meshes'][0]['deform_weights']
        self.assertEqual(before,after)
        # Evaluated export assigns a temporary mesh name; all other JSON and binary data agree.
        def glb(path):
            data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0]
            doc=json.loads(data[20:20+length])
            for mesh in doc['meshes']:mesh.pop('name')
            return doc,data[20+length:]
        self.assertEqual(glb(self.path/'stack.glb'),glb(self.path/'applied.glb'))

    def test_smooth_custom_normal_rejection_preserves_modifier_and_geometry(self):
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
o=bpy.context.object
for face in o.data.polygons:face.use_smooth=True
o.data.normals_split_custom_set([(.2,.3,1)]*24)
m=o.modifiers.new('Displace','DISPLACE')
before=[tuple(v.co) for v in o.data.vertices]
try:bpy.ops.object.modifier_apply(modifier=m.name)
except Exception as error:assert 'flat input faces' in str(error)
else:raise AssertionError('Unverified smooth custom normals accepted')
assert before==[tuple(v.co) for v in o.data.vertices] and len(o.modifiers)==1
o.modifiers.remove(m)
"""))
