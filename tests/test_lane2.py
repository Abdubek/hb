"""Lane 2 compatibility regression tests; Blender goldens define API values."""
import unittest
import test_cli
from normalize import revision
from png import rgba

class Lane2(unittest.TestCase):
    setUp=test_cli.CLI.setUp
    tearDown=test_cli.CLI.tearDown
    hb=test_cli.CLI.hb
    script=test_cli.CLI.script

    def test_world_nodes_persist_and_drive_constant_preview(self):
        self.hb('run',self.script("""import bpy
w=bpy.data.worlds.new('Lighting');w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,0,0,1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value=2
bpy.context.scene.world=w
"""))
        self.hb('run',self.script("""import bpy
w=bpy.context.scene.world
assert w.node_tree.nodes['Background'].inputs['Strength'].default_value==2
assert tuple(w.node_tree.nodes['Background'].inputs['Color'].default_value)==(.25,0,0,1)
"""))
        self.hb('render','--views','front','--size','32','--out','world.png')
        _,_,pixels=rgba((self.path/'world.png').read_bytes())
        self.assertGreater(pixels[0][0][0],50)
        self.assertEqual(pixels[0][0][1:],[0,0,255] if isinstance(pixels[0][0],list) else (0,0,255))

    def test_world_unsupported_nodes_and_options_rollback(self):
        self.hb('run',self.script("import bpy\nbpy.context.scene.world.use_nodes=True"))
        before=(self.path/'scene.hb').read_bytes()
        for expression in [
            "w.node_tree.nodes.new('ShaderNodeTexSky')",
            "w.node_tree.nodes.new('ShaderNodeBsdfPrincipled')",
            "w.node_tree.nodes.new('ShaderNodeTexEnvironment').projection='MIRROR_BALL'",
            "w.node_tree.nodes.new('ShaderNodeTexEnvironment').interpolation='Closest'",
            "w.node_tree.nodes['Background'].inputs['Weight'].default_value=1",
        ]:
            result=self.hb('run',self.script('import bpy\nw=bpy.context.scene.world\n'+expression),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API')
            self.assertTrue(result['error']['suggestion'])
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_material_transmission_export_matches_blender(self):
        import json
        from pathlib import Path
        from independent_semantics import read
        fixture=test_cli.ROOT/'compat/golden/m3_materials.py'
        self.hb('run',fixture,'--out','materials.glb')
        actual={m['name']:m for m in read(self.path/'materials.glb')['materials']}
        ref=json.loads((test_cli.ROOT/'compat/fixtures/material-export-reference.json').read_text())
        expected=next(m for m in ref['materials'] if m['name']=='Glass')
        self.assertEqual(actual['Glass']['extensions'],expected['extensions'])
        self.hb('import','materials.glb','--scene','import.hb')
        self.hb('export','roundtrip.glb','--scene','import.hb')
        copied={m['name']:m for m in read(self.path/'roundtrip.glb')['materials']}
        self.assertEqual(copied['Glass']['extensions'],expected['extensions'])

    def test_principled_data_persistence_and_explicit_export_metadata(self):
        from independent_semantics import read
        self.hb('run',self.script("""import bpy
m=bpy.data.materials.new('Layered');m.use_nodes=True
p=m.node_tree.nodes['Principled BSDF']
p.inputs['Subsurface Weight'].default_value=.5
p.inputs['Coat Tint'].default_value=(.25,.5,.75,1)
bpy.ops.mesh.primitive_cube_add();bpy.context.object.data.materials.append(m)
"""))
        self.hb('run',self.script("""import bpy
p=bpy.data.materials['Layered'].node_tree.nodes['Principled BSDF']
assert p.inputs['Subsurface Weight'].default_value==.5
assert tuple(p.inputs['Coat Tint'].default_value)==(.25,.5,.75,1)
"""))
        result=self.hb('export','layered.glb')
        material=read(self.path/'layered.glb')['materials'][0]
        self.assertEqual(material['extras']['hb_principled']['Subsurface Weight'],.5)
        self.assertEqual(material['extras']['hb_principled']['Coat Tint'],[.25,.5,.75,1])
        self.assertIn('hb_principled',str(result))
        self.hb('import','layered.glb','--scene','copy.hb')
        self.hb('export','copy.glb','--scene','copy.hb')
        self.assertEqual(read(self.path/'copy.glb')['materials'][0]['extras'],material['extras'])

    def test_material_chain_scope_errors(self):
        self.hb('run',self.script("import bpy\nm=bpy.data.materials.new('M');m.use_nodes=True"))
        before=(self.path/'scene.hb').read_bytes()
        for expression in [
            "m.node_tree.nodes.new('ShaderNodeMixShader')",
            "m.node_tree.nodes.new('ShaderNodeMapping').vector_type='NORMAL'",
            "m.node_tree.nodes.new('ShaderNodeMapping').inputs['Rotation'].default_value=(1,0,0)",
            "m.node_tree.nodes.new('ShaderNodeTexCoord').outputs['Generated']",
            "m.blend_method='BLEND'",
            "m.surface_render_method='DITHERED'",
            "m.node_tree.nodes['Principled BSDF'].inputs['Weight']",
        ]:
            result=self.hb('run',self.script("import bpy\nm=bpy.data.materials['M']\n"+expression),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API',expression)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_invalid_new_material_import_parameters_rollback(self):
        import json
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        for material in [
            {'extensions':{'KHR_materials_ior':{'ior':.5}}},
            {'extensions':{'KHR_materials_transmission':{'transmissionFactor':2}}},
            {'extras':{'hb_principled':{'Unlisted Socket':.5}}},
        ]:
            (self.path/'invalid.gltf').write_text(json.dumps({'asset':{'version':'2.0'},'materials':[material]}))
            self.hb('import','invalid.gltf',ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_mathutils_limits_and_undefined_reference_case(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before=(self.path/'scene.hb').read_bytes()
        for expression in [
            'Matrix(((1,0,0,0),(0,1,0,0))) @ Vector((1,2,3))',
            'Matrix.Identity(4).__setitem__(0,(1e7,0,0,0))\nm=Matrix.Diagonal((1e7,1,1,1));m.decompose()',
            'Quaternion((1e7,0,0,0)).slerp(Quaternion(),.5)',
        ]:
            result=self.hb('run',self.script('from mathutils import Matrix,Vector,Quaternion\n'+expression),ok=False)
            self.assertEqual(result['error']['code'],'UNSUPPORTED_API')
            self.assertTrue(result['error']['suggestion'])
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_texture_assets_match_blender_and_roundtrip(self):
        import json
        from independent_semantics import read
        expected=json.loads((test_cli.ROOT/'compat/fixtures/texture-assets-reference.json').read_text())
        def normalized(doc):
            out={}
            for m in doc['materials']:
                value={}
                for role,info in [('base',m.get('pbrMetallicRoughness',{}).get('baseColorTexture')),('emission',m.get('emissiveTexture'))]:
                    if info is None:continue
                    texture=doc['textures'][info['index']];sampler=doc.get('samplers',[])[texture['sampler']] if 'sampler' in texture else {}
                    value[role]={'texCoord':info.get('texCoord',0),'transform':info.get('extensions',{}).get('KHR_texture_transform'),'wrap':[sampler.get(k,10497) for k in ('wrapS','wrapT')]}
                value['emissiveFactor']=m.get('emissiveFactor',[0,0,0])
                value['strength']=m.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
                out[m['name']]=value
            return out
        self.hb('run',test_cli.ROOT/'compat/golden/m3_texture_assets.py','--out','textures.glb')
        self.assertEqual(normalized(read(self.path/'textures.glb')),normalized(expected))
        for i,source in enumerate([self.path/'textures.glb',test_cli.ROOT/'compat/fixtures/texture-assets-reference.glb']):
            scene='import'+str(i)+'.hb'
            self.hb('import',source,'--scene',scene)
            self.hb('export','roundtrip.glb','--scene',scene)
            actual=read(self.path/'roundtrip.glb')
            self.assertEqual(normalized(actual),normalized(expected))
            for mesh in actual['meshes']:
                self.assertTrue(all('TEXCOORD_1' in p['attributes'] for p in mesh['primitives']))
            self.hb('run',self.script("import bpy\nassert bpy.data.materials['MIRROR'] is not None"),'--scene',scene)
        for args in [('render','--size','32','--out','x.png'),('export','x.obj'),('export','x.usdz')]:
            result=self.hb(*args,ok=False)
            self.assertIn('glTF asset features',str(result))
        before=(self.path/'scene.hb').read_bytes()
        result=self.hb('run',self.script("import bpy\nbpy.data.materials['REPEAT'].node_tree.nodes['Image Texture'].extension='CLIP'"),ok=False)
        self.assertEqual(result['error']['code'],'UNSUPPORTED_API')
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_texture_binding_import_limits_and_uv_override(self):
        import json,struct
        from independent_semantics import read
        source=(test_cli.ROOT/'compat/fixtures/texture-assets-reference.glb').read_bytes()
        count=struct.unpack_from('<I',source,12)[0];original=json.loads(source[20:20+count]);tail=source[20+count:]
        def write(doc):
            encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
            data=struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(tail))+struct.pack('<I4s',len(encoded),b'JSON')+encoded+tail
            path=self.path/'source.glb';path.write_bytes(data);return path
        for field,value in [('texCoord',8),('texCoord',-1),('texCoord',7),('extensions',{'KHR_texture_transform':{'scale':[1]}}),('extensions',{'KHR_unsupported':{}})]:
            doc=json.loads(json.dumps(original));doc['materials'][0]['emissiveTexture'][field]=value
            result=self.hb('import',write(doc),ok=False)
            self.assertIn('texture',str(result).lower())
        doc=json.loads(json.dumps(original))
        doc['materials'][0]['emissiveTexture']['extensions']['KHR_texture_transform']['texCoord']=1
        self.hb('import',write(doc));self.hb('export','override.glb')
        m=next(m for m in read(self.path/'override.glb')['materials'] if m['name']=='REPEAT')
        self.assertEqual(m['emissiveTexture']['extensions']['KHR_texture_transform']['texCoord'],1)

    def test_shared_material_render_uv_requires_explicit_material_split(self):
        self.hb('run',test_cli.ROOT/'compat/golden/m3_texture_assets.py')
        self.hb('run',self.script("""import bpy
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.data.materials.append(bpy.data.materials['REPEAT'])
"""))
        result=self.hb('export','shared.glb',ok=False)
        self.assertIn('duplicate the material',str(result))

    def test_imported_texture_image_users_and_removal(self):
        fixture=test_cli.ROOT/'compat/fixtures/texture-assets-reference.glb'
        self.hb('run',self.script("import bpy\nbpy.ops.import_scene.gltf(filepath="+repr(str(fixture))+")\nassert bpy.data.images['MIRROR'].users==2\nbpy.data.images.remove(bpy.data.images['MIRROR'],do_unlink=True)\nassert bpy.data.images.get('MIRROR') is None"))
        self.hb('export','unlinked.glb')
        from independent_semantics import read
        m=next(m for m in read(self.path/'unlinked.glb')['materials'] if m['name']=='MIRROR')
        self.assertNotIn('emissiveTexture',m)
        self.assertNotIn('baseColorTexture',m['pbrMetallicRoughness'])
