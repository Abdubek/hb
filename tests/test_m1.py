import unittest,json,struct,subprocess,sys,zlib,shutil
from pathlib import Path
import test_cli
from test_cli import HB,ROOT
from normalize import revision

class Assembly(unittest.TestCase):
    setUp=test_cli.CLI.setUp;tearDown=test_cli.CLI.tearDown;hb=test_cli.CLI.hb;script=test_cli.CLI.script
    def test_revision_navigation_and_diff(self):
        a=self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))['revision']
        old=(self.path/'scene.hb.revisions'/f'{a}.hbr').read_bytes()
        b=self.hb('run',self.script('import bpy\nbpy.data.objects["Cube"].location=(3,0,0)'))['revision']
        delta=self.hb('diff',a,b)['changes']['objects']['modified'][0]
        self.assertEqual(delta['location'],{'before':[0,0,0],'after':[3,0,0]})
        self.assertEqual(self.hb('undo')['revision'],a)
        self.assertEqual(self.hb('checkout',b)['revision'],b)
        self.assertEqual([r['revision'] for r in self.hb('log')['revisions']],[b,a])
        self.assertEqual(old,(self.path/'scene.hb.revisions'/f'{a}.hbr').read_bytes())
    def test_scene_lock_and_failed_export(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()');self.hb('run',p)
        before=(self.path/'scene.hb').read_bytes();(self.path/'scene.hb.lock').write_text('999999999')
        self.assertEqual(self.hb('run',p,ok=False)['error']['code'],'SCENE_BUSY')
        (self.path/'scene.hb.lock').unlink();self.hb('run',p,'--out','missing/out.glb',ok=False)
        self.assertEqual(before,(self.path/'scene.hb').read_bytes())
    def test_old_m0_migration(self):
        old=ROOT/'compat/fixtures/m0.hb'
        shutil.copy(old,self.path/'old.hb')
        self.assertGreater(self.hb('query','stats','--scene','old.hb')['result']['objects'],0)
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'),'--scene','old.hb')
        self.hb('undo','--scene','old.hb')
    def test_world_bounds_surface_distance_and_containment(self):
        self.hb('run',self.script('''import bpy
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.name='outer';a.scale=(2,2,2)
bpy.ops.mesh.primitive_cube_add(size=1);b=bpy.context.object;b.name='inner'
p=bpy.data.objects.new('parent',None);bpy.context.collection.objects.link(p);p.location=(3,0,0)
a.parent=p;b.parent=p
'''))
        self.assertEqual(self.hb('query','bbox','outer')['result']['bbox']['min'],[1,-2,-2])
        self.assertAlmostEqual(self.hb('query','distance','outer','inner')['result']['distance'],1.5)
        self.assertTrue(self.hb('query','inside','inner','outer')['result']['inside'])
        self.assertEqual(self.hb('query','overlaps')['result']['pairs'][0]['relation'],'containment')
    def test_distance_is_not_bbox_distance(self):
        self.hb('run',self.script('''import bpy
for name,verts in [('a',[(0,0,0),(2,0,0),(0,2,0)]),('b',[(2,2,0),(2,.9,0),(.9,2,0)])]:
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],[(0,1,2)]);o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
'''))
        self.assertGreater(self.hb('query','distance','a','b')['result']['distance'],.6)
        self.assertEqual(self.hb('query','overlaps')['result']['pairs'],[])
    def test_frustum_crossing_without_inside_vertices(self):
        self.hb('run',self.script('''import bpy
m=bpy.data.meshes.new('large');m.from_pydata([(-100,-100,-5),(100,-100,-5),(0,100,-5)],[],[(0,1,2)])
o=bpy.data.objects.new('crossing',m);bpy.context.collection.objects.link(o)
c=bpy.data.cameras.new('lens');o=bpy.data.objects.new('camera',c);bpy.context.collection.objects.link(o);bpy.context.scene.camera=o
'''))
        self.assertEqual(self.hb('query','visible')['result']['objects'],['crossing'])
        self.hb('render','--views','camera','--size','64','--out','view.png')
    def test_contact_sheet_determinism(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        a=self.hb('render','--size','64','--out','a.png');self.hb('render','--size','64','--out','b.png')
        self.assertEqual((self.path/'a.png').read_bytes(),(self.path/'b.png').read_bytes())
        self.assertEqual(struct.unpack('>II',(self.path/'a.png').read_bytes()[16:24]),(192,192))
        self.assertEqual(a['render']['triangles'],12)
    def test_gltf_textures_materials_hierarchy_roundtrip(self):
        self.hb('run',self.script('''import bpy
p=bpy.data.objects.new('root',None);bpy.context.collection.objects.link(p);p.location=(1,2,3);p.rotation_euler=(.2,-.4,.8)
bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name='panel';o.parent=p;o.location=(2,0,0)
for name,color in [('red',(1,0,0,1)),('green',(0,1,0,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;o.data.materials.append(m)
o.data.polygons[1].material_index=1
copy=o.copy();copy.name='shared';copy.location=(0,3,0);bpy.context.collection.objects.link(copy)
'''),'--out','out.glb')
        before=self.hb('query','bbox','--all')['result']
        self.hb('import','out.glb','--scene','import.hb')
        after=self.hb('query','bbox','--all','--scene','import.hb')['result']
        for a,b in zip(before['objects'],after['objects']):
            self.assertEqual(a['name'],b['name'])
            for x,y in zip(a['bbox']['min'],b['bbox']['min']):self.assertAlmostEqual(x,y,places=5)
        s=revision(self.path/'import.hb')['scene'];self.assertEqual(len(s['meshes']),1);self.assertEqual(len(s['materials']),2)
        self.hb('export','copy.gltf','--scene','import.hb');self.hb('import','copy.gltf','--scene','again.hb')
    def test_embedded_texture_import(self):
        self.hb('run',ROOT/'compat/golden/m1_material.py','--out','textured.glb')
        self.hb('import','textured.glb','--scene','import.hb')
        s=revision(self.path/'import.hb')['scene'];self.assertEqual(len(s['images']),3)
        self.assertTrue(all(i.get('encoded') for i in s['images']))
        self.hb('render','--scene','import.hb','--views','iso','--size','64')
    def test_obj_multi_material_negative_indices(self):
        (self.path/'asset.mtl').write_text('newmtl red\nKd 1 0 0\nnewmtl green\nKd 0 1 0\n')
        (self.path/'asset.obj').write_text('mtllib asset.mtl\nv 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\no first\nusemtl red\nf 1 2 3\ng second\nusemtl green\nf -4 -2 -1\n')
        self.hb('import','asset.obj');s=self.hb('query','stats')['result'];self.assertEqual(s['objects'],2);self.assertEqual(s['materials'],2)
        self.hb('export','asset.glb')
    def test_missing_linked_texture_is_corrective(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cube_add()\no=bpy.context.object\nm=bpy.data.materials.new('m');m.use_nodes=True\no.data.materials.append(m)\nt=m.node_tree.nodes.new('ShaderNodeTexImage')\nm.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])"))
        result=self.hb('render','--size','64',ok=False)
        self.assertEqual(result['error']['code'],'RENDER_ERROR');self.assertIn('assign node.image',result['error']['message'])
    def test_invalid_import_is_transactional(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'));before=(self.path/'scene.hb').read_bytes()
        (self.path/'bad.gltf').write_text(json.dumps({'asset':{'version':'2.0'},'extensionsRequired':['KHR_draco_mesh_compression']}))
        self.assertIn('extension',self.hb('import','bad.gltf',ok=False)['error']['message'])
        self.assertEqual(before,(self.path/'scene.hb').read_bytes())
    def rpc(self,mode,messages):
        p=subprocess.run([str(HB),'serve',mode],input='\n'.join(json.dumps(m) for m in messages)+'\n',capture_output=True,text=True,cwd=self.path)
        self.assertEqual(p.returncode,0,p.stderr);return [json.loads(s) for s in p.stdout.splitlines()]
    def test_jsonrpc_notification_executes_without_reply(self):
        replies=self.rpc('--jsonrpc',[{'jsonrpc':'2.0','method':'run','params':{'code':'import bpy\nbpy.ops.mesh.primitive_cube_add()'}},{'jsonrpc':'2.0','id':1,'method':'query','params':{'args':['stats']}}])
        self.assertEqual(len(replies),1);self.assertEqual(replies[0]['result']['result']['objects'],1)
    def test_wrong_light_property_and_unimplemented_shader_inputs(self):
        for source in ["import bpy\nl=bpy.data.lights.new('sun','SUN')\nl.size=2", "import bpy\nm=bpy.data.materials.new('m');m.use_nodes=True\nm.node_tree.nodes['Principled BSDF'].inputs['Normal'].default_value=(1,0,0)"]:
            self.assertEqual(self.hb('run',self.script(source),ok=False)['error']['code'],'UNSUPPORTED_API')
    def test_jsonrpc_batch_repeated_python(self):
        replies=self.rpc('--jsonrpc',[[{'jsonrpc':'2.0','id':1,'method':'check','params':{'code':'import bpy\nbpy.ops.mesh.primitive_cube_add()'}},{'jsonrpc':'2.0','id':2,'method':'run','params':{'code':'import bpy\nbpy.ops.mesh.primitive_cube_add()'}}],{'jsonrpc':'2.0','id':3,'method':'query','params':{'args':['stats']}}])
        self.assertEqual(len(replies),2);self.assertTrue(replies[0][0]['result']['ok']);self.assertTrue(replies[0][1]['result']['ok']);self.assertEqual(replies[1]['result']['result']['objects'],1)
    def test_mcp_lifecycle_and_precheck(self):
        replies=self.rpc('--mcp',[{'jsonrpc':'2.0','id':0,'method':'tools/list'}, {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'hb_run','arguments':{'code':'import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.ops.wm.save_as_mainfile(filepath="x.blend")'}}}])
        self.assertEqual(replies[1]['result']['serverInfo']['version'],self.hb('capabilities')['version'])
        self.assertIn('error',replies[0]);self.assertEqual({t['name'][3:] for t in replies[2]['result']['tools']},set(self.hb('capabilities')['commands'])-{'serve --jsonrpc','serve --mcp'});self.assertTrue(replies[3]['result']['isError']);self.assertFalse((self.path/'scene.hb').exists())
    def test_rpc_rejects_malformed_arguments(self):
        for params in ({'scene':42}, {'code':False}, {'unknown':'value'}):
            result=self.rpc('--jsonrpc',[{'jsonrpc':'2.0','id':1,'method':'run','params':params}])[0]
            self.assertEqual(result['error']['data']['code'],'INVALID_PARAMS')
            self.assertFalse((self.path/'scene.hb').exists())
    def test_scene_camera_preflight_matches_supported_object(self):
        source="""import bpy
camera=bpy.data.cameras.new('Lens')
obj=bpy.data.objects.new('Camera',camera)
bpy.context.collection.objects.link(obj)
bpy.context.scene.camera=obj
assert bpy.context.scene.camera.name=='Camera'
bpy.context.scene.camera.location=(1,2,3)
"""
        path=self.script(source)
        self.hb('check',path)
        self.hb('run',path)
        bad=self.script(source+"bpy.context.scene.camera.unsupported_camera_property=1\n")
        self.assertFalse(self.hb('check',bad,ok=False)['ok'])
if __name__=='__main__':unittest.main()
