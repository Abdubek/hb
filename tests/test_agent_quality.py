"""Agent affordances, review freshness, geometry diagnosis and final preview."""
import hashlib
import json
import math
import subprocess
import unittest
import test_cli
from normalize import revision


class AgentQuality(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def recipe(self, name, params=None):
        return self.hb('recipe', name, '--params', json.dumps(params or {}))['code']

    def scene(self):
        code = self.recipe('housing') + '\n' + self.recipe('studio')
        self.hb('check', self.script(code))
        return self.hb('run', self.script(code))

    def review(self):
        return self.hb('review', '--size', 96, '--out', 'review.json')['review']

    def assess(self, r):
        a = r['assessment_template']
        for key in a['checks']:
            a['checks'][key] = {'pass': True, 'notes': 'Synthetic test assessment for protocol validation; no aesthetic score.'}
        a['acknowledged_warnings'] = {i['id']: 'Intentional test geometry.' for i in r['diagnostics']['issues']}
        p = self.path/'assessment.json'
        p.write_text(json.dumps(a))
        return p

    def test_capabilities_and_mcp_use_shared_command_metadata(self):
        c = self.hb('capabilities', '--task', 'кабель')
        self.assertEqual(c['recipes'][0]['name'], 'cable')
        self.assertTrue(all(r['available'] for r in c['recipes']))
        self.assertIn('bezier', [f['name'] for f in c['features']])
        self.assertNotIn('Bezier/NURBS', json.dumps(c['not_implemented']))
        rows = [dict(jsonrpc='2.0', id=1, method='initialize', params=dict(protocolVersion='2025-11-25',clientInfo={},capabilities={})),dict(jsonrpc='2.0',method='notifications/initialized'),dict(jsonrpc='2.0',id=2,method='tools/list')]
        p = subprocess.run([str(test_cli.HB),'serve','--mcp'],input='\n'.join(map(json.dumps,rows))+'\n',text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        tools = json.loads(p.stdout.splitlines()[-1])['result']['tools']
        self.assertEqual({t['name'][3:] for t in tools},set(c['commands'])-{'serve --jsonrpc','serve --mcp'})
        export = next(t for t in tools if t['name']=='hb_export')
        self.assertIn('USDZ',export['description']);self.assertNotIn('unavailable',export['description'])

    def test_all_recipes_check_run_and_export(self):
        params = {'font': str(test_cli.ROOT/'compat/fixtures/fonts/DejaVuSans.ttf')}
        for name in ('housing','cable','label','studio'):
            with self.subTest(recipe=name):
                code=self.recipe(name,params if name=='label' else {})
                self.hb('check',self.script(code))
                self.hb('run',self.script(code),'--scene',name+'.hb','--out',name+'.glb')
                before=(self.path/(name+'.hb')).read_bytes()
                self.hb('run',self.script(code),'--scene',name+'.hb',ok=False)
                self.assertEqual(before,(self.path/(name+'.hb')).read_bytes())
        self.scene()
        self.assertTrue(self.hb('inspect')['diagnostics']['geometry_ready'])

    def test_recipe_validation(self):
        for name,params in [('housing',{'bevel':1}),('housing',{'dimensions':[0,1,1]}),('cable',{'points':[[0,0,0]]}),('studio',{'unknown':1}),('label',{}),('label',{'font':'font.ttf','text':'Привет'}),('housing',{'name':'bad\0name'})]:
            with self.subTest(name=name,params=params):
                self.assertEqual(self.hb('recipe',name,'--params',json.dumps(params),ok=False)['error']['code'],'USAGE')
        self.assertFalse((self.path/'scene.hb').exists())

    def test_review_delivery_and_image_content(self):
        current=self.scene();r=self.review();assessment=self.assess(r)
        self.assertEqual(r['revision'],current['revision'])
        self.assertEqual(r['image_sha256'],hashlib.sha256((self.path/'review.review.png').read_bytes()).hexdigest())
        self.assertEqual(r['render']['views'],['camera','front','right','top','wire'])
        delivered=self.hb('deliver','--review','review.json','--assessment',assessment,'--out','result.glb')
        self.assertEqual(delivered['revision'],current['revision'])
        self.assertTrue((self.path/'result.delivery.json').is_file())
        self.assertEqual(delivered['output_sha256'],hashlib.sha256((self.path/'result.glb').read_bytes()).hexdigest())

    def test_stale_revision_and_image_are_rejected(self):
        self.scene();r=self.review();assessment=self.assess(r)
        image=self.path/'review.review.png';image.write_bytes(image.read_bytes()+b'changed')
        args=['deliver','--review','review.json','--assessment',assessment,'--out','result.glb']
        self.assertEqual(self.hb(*args,ok=False)['error']['code'],'STALE_REVIEW')
        r=self.review();self.assess(r)
        self.hb('run',self.script("import bpy\nbpy.data.objects['Housing'].location.x += .1"))
        self.assertEqual(self.hb(*args,ok=False)['error']['code'],'STALE_REVIEW')
        self.assertFalse((self.path/'result.glb').exists())

    def test_assessment_and_warning_requirements(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_plane_add()'))
        r=self.review();assessment=self.path/'assessment.json';assessment.write_text(json.dumps(r['assessment_template']))
        args=['deliver','--review','review.json','--assessment',assessment,'--out','result.glb']
        self.assertEqual(self.hb(*args,ok=False)['error']['code'],'ASSESSMENT_REQUIRED')
        self.assess(r);a=json.loads(assessment.read_text());a['acknowledged_warnings']={};assessment.write_text(json.dumps(a))
        self.assertEqual(self.hb(*args,ok=False)['error']['code'],'UNREVIEWED_WARNING')
        self.assess(r);self.hb(*args)

    def test_quality_diagnostics_and_input_protection(self):
        self.hb('run',self.script('''import bpy
m=bpy.data.meshes.new('Bad');m.from_pydata([(0,0,0),(1,0,0),(2,0,0)],[],[(0,1,2)])
o=bpy.data.objects.new('Bad',m);bpy.context.collection.objects.link(o)
'''))
        d=self.hb('inspect')['diagnostics'];self.assertFalse(d['geometry_ready'])
        self.assertIn('DEGENERATE_TRIANGLES',[i['code'] for i in d['issues']])
        original=(self.path/'scene.hb').read_bytes()
        self.hb('review','--out','./scene.hb',ok=False)
        self.assertEqual(original,(self.path/'scene.hb').read_bytes())
        self.hb('inspect','--profile','everything',ok=False)
        self.hb('inspect','--camera','Missing',ok=False)

    def test_final_preview_is_opt_in_and_deterministic(self):
        self.scene()
        self.hb('render','--views','camera','--size',96,'--out','default.png')
        self.hb('render','--views','camera','--quality','draft','--size',96,'--out','draft.png')
        self.assertEqual((self.path/'default.png').read_bytes(),(self.path/'draft.png').read_bytes())
        r=self.hb('render','--views','camera','--quality','final','--size',96,'--out','final.png')
        self.assertEqual(r['render']['supersampling'],2)
        self.assertNotEqual((self.path/'draft.png').read_bytes(),(self.path/'final.png').read_bytes())
        self.hb('render','--views','camera','--quality','final','--size',96,'--out','again.png')
        self.assertEqual((self.path/'again.png').read_bytes(),(self.path/'final.png').read_bytes())
        self.hb('render','--quality','final','--size',2048,ok=False)

    def test_spatial_cyclic_curve_is_closed_with_uniform_frame_correction(self):
        count=40
        points=[[(2+.3*math.cos(3*t))*math.cos(t),1.4*math.sin(t),.4*math.sin(2*t)+.3*math.cos(t)] for t in [i*2*math.pi/count for i in range(count)]]
        self.hb('run',self.script(f'''import bpy
c=bpy.data.curves.new('Loop','CURVE');c.dimensions='3D';c.bevel_depth=.025;c.bevel_resolution=2
s=c.splines.new('POLY');s.points.add({count-1});s.use_cyclic_u=True
for p,co in zip(s.points,{points!r}):p.co=(*co,1)
o=bpy.data.objects.new('Loop',c);bpy.context.collection.objects.link(o)
'''))
        m=revision(self.path/'scene.hb')['scene']['meshes'][0];edges={}
        for f in m['faces']:
            for a,b in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append(a<b)
        self.assertTrue(all(len(v)==2 and v[0]!=v[1] for v in edges.values()))
        def sub(a,b):return [x-y for x,y in zip(a,b)]
        def dot(a,b):return sum(x*y for x,y in zip(a,b))
        def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
        def norm(a):return math.sqrt(dot(a,a))
        def unit(a):return [x/norm(a) for x in a]
        directions=[unit(sub(points[(i+1)%count],points[i])) for i in range(count)]
        tangents=[unit([a+b for a,b in zip(directions[i-1],directions[i])]) for i in range(count)]
        radials=[]
        for i,center in enumerate(points):
            ring=m['vertices'][i*8:(i+1)*8]
            for v in ring:self.assertAlmostEqual(norm(sub(v,center)),.025,delta=2e-6)
            radials.append(unit(sub(ring[0],center)))
        rates=[]
        for i in range(count):
            j=(i+1)%count;axis=cross(tangents[i],tangents[j]);sine=norm(axis);cosine=dot(tangents[i],tangents[j]);axis=unit(axis);r=radials[i]
            transported=[r[k]*cosine+cross(axis,r)[k]*sine+axis[k]*dot(axis,r)*(1-cosine) for k in range(3)]
            angle=math.atan2(dot(tangents[j],cross(transported,radials[j])),dot(transported,radials[j]))
            rates.append(angle/norm(sub(points[j],points[i])))
        self.assertLess(max(rates)-min(rates),.002)
        self.hb('export','loop.glb')

    def test_inline_assessment_and_review_mcp_image(self):
        self.scene();r=self.review();a=json.loads(self.assess(r).read_text())
        self.hb('deliver','--review','review.json','--assessment-json',json.dumps(a),'--out','inline.glb')
        rows=[dict(jsonrpc='2.0',id=1,method='initialize',params=dict(protocolVersion='2025-11-25',clientInfo={},capabilities={})),dict(jsonrpc='2.0',method='notifications/initialized'),dict(jsonrpc='2.0',id=2,method='tools/call',params={'name':'hb_review','arguments':{'scene':str(self.path/'scene.hb'),'args':['--size','64','--out',str(self.path/'mcp.json')]}})]
        p=subprocess.run([str(test_cli.HB),'serve','--mcp'],input='\n'.join(map(json.dumps,rows))+'\n',text=True,capture_output=True)
        reply=json.loads(p.stdout.splitlines()[-1])['result']
        self.assertFalse(reply['isError']);self.assertTrue(any(c['type']=='image' for c in reply['content']))

    def test_checker_preserves_tuple_positions_and_rejects_bad_api(self):
        source='''import bpy
def make():
    c=bpy.data.curves.new('C','CURVE')
    s=c.splines.new('BEZIER')
    return c,s
pair=make()
c,s=pair
p=s.bezier_points[0]
p.handle_left_type='AUTO'
last=pair[-1]
last.bezier_points[0].co=(0,0,0)
'''
        self.hb('check',self.script(source))
        result=self.hb('check',self.script(source+"\nlast.bezier_points[0].unsupported_magic()"),ok=False)
        self.assertTrue(any('unsupported_magic' in e['message'] for e in result['errors']))

    def test_environment_final_mode_uses_directional_light(self):
        self.scene()
        self.hb('run',self.script('''import bpy
world=bpy.data.worlds.new('Directional');world.use_nodes=True
world.node_tree.nodes.clear()
out=world.node_tree.nodes.new('ShaderNodeOutputWorld')
bg=world.node_tree.nodes.new('ShaderNodeBackground')
env=world.node_tree.nodes.new('ShaderNodeTexEnvironment')
image=bpy.data.images.new('Hemisphere',width=4,height=2,float_buffer=True)
image.colorspace_settings.name='Non-Color'
image.pixels=[0,0,0,1]*4+[1,.2,.05,1]*4
env.image=image
world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
world.node_tree.links.new(bg.outputs['Background'],out.inputs['Surface'])
bpy.context.scene.world=world
'''))
        draft=self.hb('render','--size',64,'--views','camera','--out','env-draft.png')
        final=self.hb('render','--size',64,'--views','camera','--quality','final','--out','env-final.png')
        self.assertFalse(draft['render']['directional_environment']);self.assertTrue(final['render']['directional_environment'])

    def test_review_focus_ignores_flat_backdrop_and_allows_explicit_selection(self):
        self.scene()
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_plane_add(size=100)\nbpy.context.object.name='Backdrop'\nbpy.context.object.location.z=-.1"))
        r=self.review()
        self.assertEqual(r['render']['focus'],['Housing'])
        explicit=self.hb('review','--size',64,'--out','explicit.json','--focus','Backdrop')['review']
        self.assertEqual(explicit['render']['focus'],['Backdrop'])
        self.assertEqual(self.hb('review','--size',64,'--focus','Missing',ok=False)['error']['code'],'RENDER_ERROR')

    def test_final_orthographic_lighting_is_dolly_invariant_and_convex_ao_is_clean(self):
        from png import rgba
        self.hb('run',self.script('''import bpy
from mathutils import Vector
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1)
o=bpy.context.object
for f in o.data.polygons:f.use_smooth=True
m=bpy.data.materials.new('Matte');m.diffuse_color=(.6,.6,.6,1);m.roughness=.4;o.data.materials.append(m)
w=bpy.data.worlds.new('Constant');w.use_nodes=False;w.color=(.4,.4,.4);bpy.context.scene.world=w
light=bpy.data.lights.new('Off','SUN');light.energy=0
lamp=bpy.data.objects.new('Off',light);bpy.context.collection.objects.link(lamp)
c=bpy.data.cameras.new('Camera');c.type='ORTHO';c.ortho_scale=3
o=bpy.data.objects.new('Camera',c);bpy.context.collection.objects.link(o);o.location=(0,-4,0);o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=o
'''))
        self.hb('render','--quality','final','--views','camera','--size',128,'--out','constant.png')
        _,_,pixels=rgba((self.path/'constant.png').read_bytes())
        values=[pixels[y][x][0] for y in range(45,83) for x in range(45,83)]
        self.assertLessEqual(max(values)-min(values),1,'Constant light must not produce depth-AO contour bands on a convex sphere')
        self.hb('run',self.script("import bpy\nbpy.data.lights['Off'].energy=2\nbpy.data.materials['Matte'].metallic=.6"))
        self.hb('render','--quality','final','--views','camera','--size',128,'--out','near.png')
        self.hb('run',self.script("import bpy\nbpy.data.objects['Camera'].location.y=-16"))
        self.hb('render','--quality','final','--views','camera','--size',128,'--out','far.png')
        _,_,near=rgba((self.path/'near.png').read_bytes());_,_,far=rgba((self.path/'far.png').read_bytes())
        self.assertLessEqual(max(abs(a-b) for ra,rb in zip(near,far) for pa,pb in zip(ra,rb) for a,b in zip(pa,pb)),1)

    def test_checker_keeps_math_arguments_separate_from_lists(self):
        self.hb('check', self.script("""from mathutils import Quaternion, Matrix

def compare(a, b):
    return list(a) == list(b)
q = Quaternion((1, 0, 0, 0))
compare([1, 0, 0, 0], [1, 0, 0, 0])
compare(q, q)
m = q.to_matrix()
m[0] = list(m[0])
m[0][0] = 1
"""))

    def test_checker_preserves_api_values_in_dictionary_items(self):
        source = """import bpy
objects = {'cube': bpy.context.object}
for name, obj in objects.items():
    obj.not_a_supported_property = 1
"""
        report = self.hb('check', self.script(source), ok=False)
        self.assertTrue(any('not_a_supported_property' in e['message'] for e in report['errors']))

    def test_checker_list_alias_mutation_still_tracks_api(self):
        source = """import bpy

def add(items):
    items.append(bpy.context.object)
objects = []
add(objects)
objects[0].not_a_supported_property = 1
"""
        report = self.hb('check', self.script(source), ok=False)
        self.assertTrue(any('not_a_supported_property' in e['message'] for e in report['errors']))
