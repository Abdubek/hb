"""Product geometry invariants, independent of generated topology ordering."""
import collections
import ast
import math
import json
import zlib
import unittest
import test_cli
from normalize import revision


def signed_volume(mesh):
    total = 0.
    for face in mesh['faces']:
        a = mesh['vertices'][face[0]]
        for i in range(1, len(face)-1):
            b, c = (mesh['vertices'][face[j]] for j in (i, i+1))
            total += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
    return total


class ModelingQuality(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def closed(self, mesh):
        edges = collections.defaultdict(list)
        for face in mesh['faces']:
            self.assertGreaterEqual(len(set(face)), 3)
            for a, b in zip(face, face[1:]+face[:1]):
                edges[tuple(sorted((a,b)))].append(1 if a < b else -1)
        self.assertTrue(edges)
        self.assertTrue(all(len(uses)==2 and sum(uses)==0 for uses in edges.values()))
        self.assertTrue(all(math.isfinite(x) for v in mesh['vertices'] for x in v))
        self.assertGreater(signed_volume(mesh), 0)
        loops = sum(map(len, mesh['faces']))
        for layer in mesh['uv_layers']:
            self.assertEqual(len(layer['data']), loops)
            self.assertTrue(all(math.isfinite(x) for uv in layer['data'] for x in uv))

    def test_general_bevel_solids_and_angle_selection(self):
        primitives = [
            'bpy.ops.mesh.primitive_cylinder_add(vertices=16)',
            'bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=1,radius2=.4)',
            'bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=1,radius2=0)',
            'bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)',
        ]
        for primitive in primitives:
            for limit in ('NONE', 'ANGLE'):
                for segments in (1, 4, 8):
                    with self.subTest(primitive=primitive, limit=limit, segments=segments):
                        source = f'''import bpy
{primitive}
o=bpy.context.object
o.data.materials.append(bpy.data.materials.new('Side'))
o.data.materials.append(bpy.data.materials.new('Cap'))
o.data.polygons[0].material_index=1
m=o.modifiers.new('Round','BEVEL');m.width=.08;m.segments={segments};m.limit_method={limit!r}
bpy.ops.object.modifier_apply(modifier=m.name)
'''
                        self.hb('run',self.script(source),'--scene','case.hb','--out','case.glb')
                        mesh=revision(self.path/'case.hb')['scene']['meshes'][-1]
                        self.closed(mesh)
                        self.assertIn(1,mesh['material_indices'])
                        # Start each case with fresh state; retain media/output checks.
                        (self.path/'case.hb').unlink()
        self.hb('import','case.glb','--scene','roundtrip.hb')
        self.hb('render','--scene','roundtrip.hb','--views','iso','--size','128','--out','roundtrip.png')

    def test_bevel_clamping_and_boundary_rollback(self):
        self.hb('run',self.script('import bpy\nbpy.ops.mesh.primitive_cylinder_add(vertices=12)'))
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\nm=bpy.context.object.modifiers.new('B','BEVEL');m.width=100;m.use_clamp_overlap=False"),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script("import bpy\nm=bpy.context.object.modifiers.new('B','BEVEL');m.width=100;m.use_clamp_overlap=True\nbpy.ops.object.modifier_apply(modifier=m.name)"),'--out','clamped.glb')
        self.closed(revision(self.path/'scene.hb')['scene']['meshes'][0])
        before=(self.path/'scene.hb').read_bytes()
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_plane_add()\nbpy.context.object.modifiers.new('B','BEVEL')"),ok=False)
        self.assertEqual((self.path/'scene.hb').read_bytes(),before)

    def test_bezier_cubic_centerline_caps_and_edit_history(self):
        code='''import bpy
c=bpy.data.curves.new('Arc','CURVE');c.dimensions='3D';c.resolution_u=8
s=c.splines.new('BEZIER');s.bezier_points.add(1)
a=s.bezier_points[0];b=s.bezier_points[1]
a.co=(0,0,0);b.co=(2,0,0)
a.handle_right=(0,0,2);b.handle_left=(2,0,2)
o=bpy.data.objects.new('Arc',c);bpy.context.collection.objects.link(o)
'''
        script=self.script(code);self.hb('check',script)
        first=self.hb('run',script)['revision']
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),9)
        for i,v in enumerate(mesh['vertices']):
            t=i/8
            expected=[6*(1-t)*t*t+2*t*t*t,0,6*(1-t)*t]
            for x,y in zip(v,expected):self.assertAlmostEqual(x,y,places=6)
        self.hb('run',self.script("import bpy\nc=bpy.data.curves['Arc'];c.bevel_depth=.05;c.use_fill_caps=True"),'--out','cable.glb')
        self.closed(revision(self.path/'scene.hb')['scene']['meshes'][0])
        self.hb('render','--views','iso','--size','128','--out','cable.png')
        self.hb('checkout',first)
        self.assertEqual(len(revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']),9)
        self.hb('run',self.script("import bpy\nc=bpy.data.curves['Arc'];p=c.splines[0].bezier_points[0];p.co.x=.2\nassert abs(p.handle_right.x-.2)<1e-6"))

    def test_bezier_automatic_vector_and_invalid_edits(self):
        script=test_cli.ROOT/'compat/golden/modeling_quality_curves.py'
        self.hb('check',script);self.hb('run',script)
        for mesh in revision(self.path/'scene.hb')['scene']['meshes']:self.closed(mesh)
        handles=self.script('''import bpy
p=bpy.data.curves['Cable'].splines[0].bezier_points[0]
assert p.handle_right.length>.1
p=bpy.data.curves['Manual'].splines[0].bezier_points[0]
p.handle_left_type='ALIGNED';p.handle_right_type='ALIGNED';p.handle_left=(-1,2,-1);p.handle_right=(1,2,1)
a=p.handle_left-p.co;b=p.handle_right-p.co
assert a.cross(b).length<1e-6 and a.dot(b)<0
''')
        self.hb('check',handles);self.hb('run',handles)
        before=(self.path/'scene.hb').read_bytes()
        for change in ("p.handle_left=(float('nan'),0,0)","p.handle_right_type='AUTO_CLAMPED'","p.co=(20000,0,0)","c.splines[0].bezier_points.add(4096)"):
            self.hb('run',self.script("import bpy\nc=bpy.data.curves['Cable'];p=c.splines[0].bezier_points[0]\n"+change),ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script("import bpy\nc=bpy.data.curves['Cable'];c.bevel_depth=0\nfor p in c.splines[0].bezier_points:p.handle_left_type='VECTOR';p.handle_right_type='VECTOR'"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['vertices']),3)

    def test_extruded_text_matches_blender_volume_and_preserves_holes(self):
        references=json.loads(zlib.decompress((test_cli.ROOT/'compat/fixtures/modeling-quality-reference.json.zlib').read_bytes()))['records']
        font=str(test_cli.ROOT/'compat/fixtures/fonts/DejaVuSans.ttf')
        for ref in references:
            if not ref['name'].startswith('text-'):continue
            body,size=ref['name'][5:].rsplit('-',1)
            with self.subTest(body=body,size=size):
                code=f'''import bpy
c=bpy.data.curves.new('Text','FONT');c.font=bpy.data.fonts.load({font!r});c.body={body!r};c.resolution_u=8;c.size={size};c.extrude=.1
o=bpy.data.objects.new('Text',c);bpy.context.collection.objects.link(o)
'''
                script=self.script(code);self.hb('check',script)
                self.hb('run',script,'--scene','text.hb','--out','text.glb')
                mesh=revision(self.path/'text.hb')['scene']['meshes'][0]
                self.closed(mesh)
                self.assertAlmostEqual(signed_volume(mesh),ref['volume'],delta=2e-6)
                for axis in range(3):
                    self.assertAlmostEqual(min(v[axis] for v in mesh['vertices']),ref['bounds'][0][axis],delta=2e-6)
                    self.assertAlmostEqual(max(v[axis] for v in mesh['vertices']),ref['bounds'][1][axis],delta=2e-6)
                # Closed O/B must have genus 1/2, rather than filled-in holes.
                if body in ('O','B'):
                    edges={tuple(sorted((a,b))) for face in mesh['faces'] for a,b in zip(face,face[1:]+face[:1])}
                    self.assertEqual(len(mesh['vertices'])-len(edges)+len(mesh['faces']),0 if body=='O' else -2)
                (self.path/'text.hb').unlink()
        self.hb('import','text.glb','--scene','imported-text.hb')
        self.hb('render','--scene','imported-text.hb','--views','iso','--size','128','--out','text.png')

    def test_text_extrusion_history_and_invalid_depth(self):
        first=self.hb('run',test_cli.ROOT/'compat/golden/modeling_quality_text.py')['revision']
        before=(self.path/'scene.hb').read_bytes()
        for depth in ('-.1',"float('inf')",'101'):
            self.hb('run',self.script('import bpy\nbpy.context.object.data.extrude='+depth),ok=False)
            self.assertEqual((self.path/'scene.hb').read_bytes(),before)
        self.hb('run',self.script('import bpy\nbpy.context.object.data.extrude=0'))
        self.assertTrue(all(v[2]==0 for v in revision(self.path/'scene.hb')['scene']['meshes'][0]['vertices']))
        self.hb('checkout',first)
        self.closed(revision(self.path/'scene.hb')['scene']['meshes'][0])

    def test_cylinder_bevel_has_continuous_circular_rings(self):
        self.hb('run',self.script("import bpy\nbpy.ops.mesh.primitive_cylinder_add(vertices=48)\nm=bpy.context.object.modifiers.new('B','BEVEL');m.width=.09;m.segments=6\nbpy.ops.object.modifier_apply(modifier=m.name)"))
        mesh=revision(self.path/'scene.hb')['scene']['meshes'][0]
        self.closed(mesh)
        rings=collections.defaultdict(list)
        for x,y,z in mesh['vertices']:rings[round(z,6)].append(math.hypot(x,y))
        for radii in rings.values():
            self.assertLess(max(radii)-min(radii),2e-6,'A cylinder rim must not develop wedges between neighboring edge profiles')

    def test_bevel_bmesh_and_triangulated_convex_input(self):
        self.hb('run',self.script('''import bpy,bmesh
bpy.ops.mesh.primitive_cylinder_add(vertices=12,calc_uvs=False)
o=bpy.context.object
t=o.modifiers.new('Triangulate','TRIANGULATE')
bpy.ops.object.modifier_apply(modifier=t.name)
bm=bmesh.new();bm.from_mesh(o.data)
result=bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.05,segments=3)
assert len(result['faces'])>0
assert all(abs(face.normal.z)<.99999 for face in result['faces'])
bm.to_mesh(o.data);bm.free()
'''),'--out','bmesh.glb')
        self.closed(revision(self.path/'scene.hb')['scene']['meshes'][0])

    def test_bezier_handle_behavior_matches_blender_source_probes(self):
        import hashlib
        import subprocess
        reference=json.loads((test_cli.ROOT/'compat/fixtures/bezier-handles-source-review.json').read_text())
        probe=test_cli.ROOT/'compat/blender_source_handle_probe.py'
        self.assertEqual(hashlib.sha256(probe.read_bytes()).hexdigest(),reference['probe_sha256'])
        self.hb('check',probe)
        result=subprocess.run([str(test_cli.HB),'run',str(probe),'--scene',str(self.path/'handles.hb')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        actual={row[0]:row for line in result.stderr.splitlines() if line.startswith('REVIEW ') for row in [ast.literal_eval(line[7:])]}
        self.assertEqual(len(actual),len(reference['cases']))
        for case in reference['cases']:
            with self.subTest(case=case['name']):
                for index,field in ((2,'left'),(3,'right')):
                    for expected,observed in zip(case[field],actual[case['name']][index]):self.assertAlmostEqual(expected,observed,delta=2e-6)
