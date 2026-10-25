import unittest
import json
import test_cli


class CompatibilityClosure(unittest.TestCase):
    setUp = test_cli.CLI.setUp
    tearDown = test_cli.CLI.tearDown
    hb = test_cli.CLI.hb
    script = test_cli.CLI.script

    def test_solidify_modes_match_42_blender_probes(self):
        from solidify_check import compare
        output = self.path / 'solidify.json'
        source = "import os\nos.environ['HB_SOLIDIFY_RESULTS']=" + repr(str(output)) + '\n'
        source += (test_cli.ROOT / 'compat/solidify_reference.py').read_text()
        self.hb('run', self.script(source))
        expected = json.loads((test_cli.ROOT / 'compat/fixtures/solidify-reference.json').read_text())
        compare(expected, json.loads(output.read_text()))

    def test_solidify_invalid_geometry_preserves_modifier_and_mesh(self):
        self.hb('run', self.script("""import bpy
mesh=bpy.data.meshes.new('Bad');mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,1)],[],[(0,1,2,3)])
obj=bpy.data.objects.new('Bad',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
modifier=obj.modifiers.new('Shell','SOLIDIFY');modifier.solidify_mode='NON_MANIFOLD'
before=[tuple(v.co) for v in mesh.vertices]
try:bpy.ops.object.modifier_apply(modifier='Shell')
except Exception as error:assert 'planar' in str(error)
else:raise AssertionError('Non-planar face accepted')
assert [tuple(v.co) for v in mesh.vertices]==before and len(obj.modifiers)==1
"""))

    def test_solidify_persistent_export_matches_applied(self):
        from obj_semantics import observe, compare
        source = """import bpy
bpy.ops.mesh.primitive_plane_add();obj=bpy.context.object
group=obj.vertex_groups.new(name='Thickness');group.add([0,1],.5,'REPLACE')
modifier=obj.modifiers.new('Shell','SOLIDIFY');modifier.solidify_mode='NON_MANIFOLD';modifier.thickness=.2;modifier.offset=0
modifier.vertex_group='Thickness';modifier.thickness_vertex_group=.1
"""
        self.hb('run', self.script(source), '--scene', 'persistent.hb', '--out', 'persistent.obj')
        self.hb('run', self.script(source + "bpy.ops.object.modifier_apply(modifier='Shell')\n"), '--scene', 'applied.hb', '--out', 'applied.obj')
        compare(observe(self.path / 'persistent.obj'), observe(self.path / 'applied.obj'))

    def test_mirrored_group_axes_and_disabled_flip_match_blender(self):
        output = self.path / 'axes.json'
        source = "import os\nos.environ['HB_MIRROR_GROUP_AXES']=" + repr(str(output)) + '\n'
        source += (test_cli.ROOT / 'compat/mirror_group_axes.py').read_text()
        self.hb('run', self.script(source))
        expected = json.loads((test_cli.ROOT / 'compat/fixtures/mirror-group-axes.json').read_text())
        self.assertEqual(json.loads(output.read_text()), expected)

    def test_mirrored_group_side_names_match_blender(self):
        output = self.path / 'names.json'
        source = "import os\nos.environ['HB_MIRROR_GROUP_NAMES']=" + repr(str(output)) + '\n'
        source += (test_cli.ROOT / 'compat/mirror_group_names.py').read_text()
        self.hb('run', self.script(source))
        expected = json.loads((test_cli.ROOT / 'compat/fixtures/mirror-group-names.json').read_text())
        self.assertEqual(json.loads(output.read_text()), expected)

    def test_mirror_object_references_duplicate_and_delete(self):
        self.hb('run', self.script("""import bpy
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object
control=bpy.data.objects.new('Plane',None);bpy.context.collection.objects.link(control)
modifier=obj.modifiers.new('Mirror','MIRROR');modifier.mirror_object=control
control.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.duplicate()
copy=bpy.context.object;copied_modifier=copy.modifiers[0]
assert copied_modifier.mirror_object.name=='Plane.001'
bpy.data.objects.remove(copied_modifier.mirror_object,do_unlink=True)
assert copied_modifier.mirror_object is None and modifier.mirror_object==control
"""))

    def test_vertex_group_edits_match_blender(self):
        output = self.path / 'groups.json'
        source = "import os\nos.environ['HB_VERTEX_GROUP_RESULTS']=" + repr(str(output)) + '\n'
        source += (test_cli.ROOT / 'compat/vertex_group_reference.py').read_text()
        self.hb('run', self.script(source))
        expected = json.loads((test_cli.ROOT / 'compat/fixtures/vertex-groups.json').read_text())
        self.assertEqual(json.loads(output.read_text()), expected)

    def test_vertex_group_bad_assignment_is_atomic(self):
        self.hb('run', self.script("""import bpy
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object
group=obj.vertex_groups.new(name='Group');group.add([0],.2,'REPLACE')
try:group.add([0,99999],.8,'REPLACE')
except Exception:pass
else:raise AssertionError('Invalid assignment accepted')
assert abs(group.weight(0)-.2)<1e-6
try:group.add([1],float('nan'),'REPLACE')
except ValueError:pass
else:raise AssertionError('Nonfinite weight accepted')
assert len(obj.data.vertices[1].groups)==0
"""))

    def test_array_zero_and_inclusive_merge_thresholds(self):
        output = self.path / 'thresholds.json'
        source = "import os\nos.environ['HB_ARRAY_THRESHOLD_RESULTS']=" + repr(str(output)) + '\n'
        source += (test_cli.ROOT / 'compat/array_thresholds.py').read_text()
        self.hb('run', self.script(source))
        expected = json.loads((test_cli.ROOT / 'compat/fixtures/array-thresholds.json').read_text())
        self.assertEqual(json.loads(output.read_text()), expected)

    def test_array_references_duplicate_and_delete(self):
        self.hb('run', self.script("""import bpy
bpy.ops.mesh.primitive_cube_add();source=bpy.context.object
bpy.ops.mesh.primitive_cube_add(location=(8,0,0));cap=bpy.context.object
control=bpy.data.objects.new('Control',None);bpy.context.collection.objects.link(control)
mod=source.modifiers.new('Array','ARRAY');mod.use_object_offset=True;mod.offset_object=control;mod.start_cap=cap
bpy.ops.object.select_all(action='DESELECT')
source.select_set(True);cap.select_set(True);control.select_set(True);bpy.context.view_layer.objects.active=source
bpy.ops.object.duplicate()
copy=bpy.context.object;copied_mod=copy.modifiers[0]
assert copied_mod.offset_object.name=='Control.001' and copied_mod.start_cap!=cap
assert copied_mod.start_cap.select_get()
bpy.data.objects.remove(copied_mod.offset_object,do_unlink=True)
bpy.data.objects.remove(copied_mod.start_cap,do_unlink=True)
assert copied_mod.offset_object is None and copied_mod.start_cap is None
assert mod.offset_object==control and mod.start_cap==cap
try:mod.end_cap=source
except Exception:pass
else:raise AssertionError('Self cap accepted')
assert mod.end_cap is None
"""))

    def test_array_persistent_export_matches_applied_geometry(self):
        from obj_semantics import observe, compare
        source = """import bpy
bpy.ops.mesh.primitive_plane_add(size=2)
obj=bpy.context.object
mod=obj.modifiers.new('Array','ARRAY');mod.count=3;mod.use_merge_vertices=True
"""
        self.hb('run', self.script(source), '--scene', 'persistent.hb', '--out', 'persistent.obj')
        self.hb('run', self.script(source + "bpy.ops.object.modifier_apply(modifier='Array')\n"), '--scene', 'applied.hb', '--out', 'applied.obj')
        compare(observe(self.path / 'persistent.obj'), observe(self.path / 'applied.obj'))
        scene = test_cli.revision(self.path / 'persistent.hb')['scene']
        self.assertEqual(len(scene['meshes'][0]['vertices']), 4)
        self.assertEqual(len(scene['objects'][0]['modifiers']), 1)

    def test_ply_import_matches_nine_blender_fixtures(self):
        from ply_check import compare
        source = test_cli.ROOT / 'compat/fixtures/ply'
        oracle = json.loads((source / 'reference.json').read_text())
        for name, expected in oracle.items():
            result = self.hb('import', source / (name + '.ply'), '--scene', name + '.hb')
            compare(test_cli.revision(self.path / (name + '.hb'))['scene'], expected)
            if name == 'face-uv': self.assertIn('face.texcoord', str(result['warnings']))
            if name == 'degenerate': self.assertIn('removed 2', str(result['warnings']))
        self.hb('export', 'scene.glb', '--scene', 'ascii.hb')
        self.hb('import', 'scene.glb', '--scene', 'roundtrip.hb')
        mesh = test_cli.revision(self.path / 'roundtrip.hb')['scene']['meshes'][0]
        self.assertEqual(len(mesh['faces']), 3)
        self.assertEqual(len(mesh['colors']), 9)
        self.assertEqual(len(mesh['loop_normals']), 9)
        self.assertEqual(len(mesh['uv_layers'][0]['data']), 9)

    def test_ply_malformed_data_rolls_back(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        before_files = sorted(p.name for p in (self.path / 'scene.hb.revisions').iterdir())
        source = test_cli.ROOT / 'compat/fixtures/ply'
        ascii_data = (source / 'ascii.ply').read_bytes()
        cases = [(source / 'binary_big_endian.ply').read_bytes()[:-1],
                 ascii_data.replace(b'element vertex 5', b'element vertex 100000001'),
                 ascii_data.replace(b'4 0 1 2 3', b'4 0 1 2 999'),
                 ascii_data.replace(b'0 0 0 0 0 1', b'nan 0 0 0 0 1'),
                 ascii_data + b'garbage', ascii_data.replace(b'property float x', b'property float128 x')]
        for data in cases:
            (self.path / 'broken.ply').write_bytes(data)
            result = self.hb('import', 'broken.ply', ok=False)
            self.assertEqual(result['error']['code'], 'IMPORT_ERROR')
            self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
            self.assertEqual(sorted(p.name for p in (self.path / 'scene.hb.revisions').iterdir()), before_files)

    def test_stl_import_matches_seven_blender_fixtures(self):
        source = test_cli.ROOT / 'compat/fixtures/stl'
        reference = json.loads((source / 'reference.json').read_text())
        for name, expected in reference.items():
            result = self.hb('import', source / (name + '.stl'), '--scene', name + '.hb')
            scene = test_cli.revision(self.path / (name + '.hb'))['scene']
            mesh = scene['meshes'][0]
            self.assertEqual(scene['objects'][0]['name'], expected['name'])
            self.assertEqual(mesh['name'], expected['mesh_name'])
            for field in ('vertices', 'faces', 'smooth'):
                self.assertEqual(mesh[field], expected[field], (name, field))
            self.assertEqual(sorted(tuple(sorted(e)) for e in mesh['edges']), sorted(tuple(sorted(e)) for e in expected['edges']))
            self.assertEqual(len(mesh['uv_layers']), expected['uv_layers'])
            self.assertEqual(mesh['loop_normals'], [n for n in expected['normals'] for _ in range(3)])
            if name == 'degenerate-binary':
                self.assertIn('1 duplicate and 1 repeated-vertex', str(result['warnings']))
            if name == 'triangles-ascii':
                # Import is revisioned and undo restores preexisting data exactly.
                before = (self.path / (name + '.hb')).read_bytes()
                self.hb('import', source / 'triangles-binary.stl', '--scene', name + '.hb')
                self.hb('undo', '--scene', name + '.hb')
                self.assertEqual((self.path / (name + '.hb')).read_bytes(), before)

    def test_stl_malformed_input_rolls_back(self):
        import struct
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'))
        before = (self.path / 'scene.hb').read_bytes()
        before_files = sorted(p.name for p in (self.path / 'scene.hb.revisions').iterdir())
        valid = (test_cli.ROOT / 'compat/fixtures/stl/triangles-binary.stl').read_bytes()
        invalid = [valid[:-1], valid[:80] + struct.pack('<I', 99999999) + valid[84:],
                   valid[:96] + struct.pack('<f', float('nan')) + valid[100:],
                   b'solid test\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nendsolid test\n']
        for data in invalid:
            (self.path / 'broken.stl').write_bytes(data)
            result = self.hb('import', 'broken.stl', ok=False)
            self.assertEqual(result['error']['code'], 'IMPORT_ERROR')
            self.assertEqual((self.path / 'scene.hb').read_bytes(), before)
            self.assertEqual(sorted(p.name for p in (self.path / 'scene.hb.revisions').iterdir()), before_files)

    def test_usdz_archive_alignment_crc_and_repeatable_export(self):
        import zipfile, struct
        self.hb('run', test_cli.ROOT / 'compat/golden/m3_format_usdz.py', '--scene', 'source.hb', '--out', 'scene.usdz')
        before = (self.path / 'source.hb').read_bytes()
        first = (self.path / 'scene.usdz').read_bytes()
        self.hb('export', 'copy.usdz', '--scene', 'source.hb')
        self.assertEqual(first, (self.path / 'copy.usdz').read_bytes())
        self.assertEqual(before, (self.path / 'source.hb').read_bytes())
        with zipfile.ZipFile(self.path / 'scene.usdz') as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.namelist()[0], 'scene.usda')
            for entry in archive.infolist():
                name, extra = struct.unpack_from('<HH', first, entry.header_offset + 26)
                self.assertEqual((entry.header_offset + 30 + name + extra) % 64, 0)
                self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
            stage = archive.read('scene.usda').decode()
            self.assertIn('metersPerUnit = 1', stage)
            self.assertIn('upAxis = "Z"', stage)
            self.assertIn('def Mesh "USD_child"', stage)

    def test_usdz_orthographic_units_and_blender_import_warning(self):
        import zipfile
        result = self.hb('run', test_cli.ROOT / 'compat/golden/m3_format_usdz_ortho.py', '--out', 'ortho.usdz')
        self.assertIn('10x', str(result['warnings']))
        with zipfile.ZipFile(self.path / 'ortho.usdz') as archive:
            stage = archive.read('scene.usda').decode()
        self.assertIn('projection = "orthographic"', stage)
        self.assertIn('horizontalAperture = 60', stage)
        self.assertIn('verticalAperture = 33.75', stage)

    def test_usdz_embeds_float_texture_pngs_without_precision_loss(self):
        import zipfile, struct
        self.hb('run', test_cli.ROOT / 'compat/golden/m3_format_usdz_texture.py', '--out', 'texture.usdz')
        data = (self.path / 'texture.usdz').read_bytes()
        with zipfile.ZipFile(self.path / 'texture.usdz') as archive:
            self.assertIsNone(archive.testzip())
            images = [entry for entry in archive.infolist() if entry.filename.endswith('.png')]
            self.assertTrue(images)
            for entry in images:
                name, extra = struct.unpack_from('<HH', data, entry.header_offset + 26)
                self.assertEqual((entry.header_offset + 30 + name + extra) % 64, 0)
                png = archive.read(entry.filename)
                self.assertEqual(struct.unpack('>IIB', png[16:25]), (2, 2, 16))

    def test_cli_obj_export_matches_blender_geometry_and_materials(self):
        from obj_semantics import observe, compare
        self.hb('run', test_cli.ROOT / 'compat/golden/m3_format_obj.py', '--scene', 'source.hb')
        before = (self.path / 'source.hb').read_bytes()
        self.hb('export', 'scene.obj', '--scene', 'source.hb')
        reference = json.loads((test_cli.ROOT / 'compat/fixtures/cli-obj-export.json').read_text())
        compare(reference, observe(self.path / 'scene.obj'))
        self.assertEqual((self.path / 'source.hb').read_bytes(), before)
        self.hb('run', test_cli.ROOT / 'compat/golden/m3_format_obj.py', '--scene', 'inline.hb', '--out', 'inline.obj')
        compare(reference, observe(self.path / 'inline.obj'))
        self.hb('import', 'scene.obj', '--scene', 'imported.hb')
        imported = test_cli.revision(self.path / 'imported.hb')['scene']
        self.assertEqual(len(imported['objects']), 2)

    def test_triangulation_matches_400_blender_polygons(self):
        output = self.path / 'triangles.json'
        source = (test_cli.ROOT / 'compat/triangulation_fuzz.py').read_text()
        source = "import os\nos.environ['HB_TRIANGULATION_RESULTS']=" + repr(str(output)) + '\n' + source
        self.hb('run', self.script(source))
        reference = json.loads((test_cli.ROOT / 'compat/fixtures/triangulation-topology.json').read_text())
        self.assertEqual(json.loads(output.read_text()), reference)

    def test_triangulation_caught_failure_preserves_all_faces(self):
        self.hb('run', self.script("""import bmesh
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,2),(1,0,2),(1,1,2),(0,1,3))]
faces=[bm.faces.new(vertices[:4]),bm.faces.new(vertices[4:])];edges=list(bm.edges)
try:bmesh.ops.triangulate(bm,faces=faces)
except Exception as error:assert 'planar' in str(error)
else:raise AssertionError('Nonplanar polygon accepted')
assert list(bm.verts)==vertices and list(bm.edges)==edges and list(bm.faces)==faces
assert all(len(face.verts)==4 for face in faces)
bm.free()
"""))

    def test_merge_representatives_match_400_blender_workloads(self):
        output = self.path / 'merges.json'
        source = (test_cli.ROOT / 'compat/merge_fuzz.py').read_text()
        source = "import os\nos.environ['HB_MERGE_RESULTS']=" + repr(str(output)) + '\n' + source
        self.hb('run', self.script(source))
        reference = json.loads((test_cli.ROOT / 'compat/fixtures/merge-representatives.json').read_text())
        self.assertEqual(json.loads(output.read_text()), reference)

    def test_import_failure_can_be_caught_without_partial_assets(self):
        # Materials are allocated before accessor validation in the importer.
        asset = {'asset': {'version': '2.0'}, 'materials': [{'name': 'Must roll back'}],
                 'meshes': [{'primitives': [{'attributes': {'POSITION': 99}}]}]}
        (self.path / 'broken.gltf').write_text(json.dumps(asset))
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
before=[o.name for o in bpy.data.objects]
materials=len(bpy.data.materials)
try:bpy.ops.import_scene.gltf(filepath='broken.gltf')
except Exception:pass
else:raise AssertionError('Invalid accessor accepted')
assert [o.name for o in bpy.data.objects]==before
assert len(bpy.data.materials)==materials
assert bpy.context.object.name=='Cube'
'''))

    def test_obj_import_failure_can_be_caught_without_partial_assets(self):
        (self.path / 'broken.mtl').write_text('newmtl Partial material\nKd 1 0 0\n')
        (self.path / 'broken.obj').write_text('mtllib broken.mtl\nv 0 0 0\nf 1 2 99\n')
        self.hb('run', self.script('''import bpy
bpy.ops.mesh.primitive_cube_add()
try:bpy.ops.import_scene.obj(filepath='broken.obj')
except Exception:pass
else:raise AssertionError('Invalid OBJ indices accepted')
assert len(bpy.data.materials)==0
assert len(bpy.data.objects)==1
assert bpy.context.object.name=='Cube'
assert len(bpy.context.selected_objects)==1
'''))

    def test_render_validates_camera_and_size_before_file_output(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()'), '--scene', 'a.hb')
        before = (self.path / 'a.hb').read_bytes()
        for source, message in [
            ("bpy.context.scene.render.filepath='output.png'\nbpy.ops.render.render(write_still=True)", 'active camera'),
            ("bpy.ops.object.camera_add()\nbpy.context.scene.camera=bpy.context.object\nbpy.context.scene.render.resolution_x=4096\nbpy.context.scene.render.filepath='output.png'\nbpy.ops.render.render(write_still=True)", '2048'),
        ]:
            with self.subTest(message=message):
                result = self.hb('run', self.script('import bpy\n' + source), '--scene', 'a.hb', ok=False)
                self.assertIn(message, result['error']['message'])
                self.assertFalse((self.path / 'output.png').exists())
                self.assertEqual((self.path / 'a.hb').read_bytes(), before)

    def test_solidify_caught_failure_preserves_nonmanifold_input(self):
        self.hb('run', self.script("""import bmesh
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1))]
for i in (2,3,4):bm.faces.new((vertices[0],vertices[1],vertices[i]))
faces=list(bm.faces);edges=list(bm.edges)
try:bmesh.ops.solidify(bm,geom=faces,thickness=.2)
except Exception as error:assert 'manifold' in str(error)
else:raise AssertionError('Nonmanifold shell accepted')
assert list(bm.verts)==vertices and list(bm.edges)==edges and list(bm.faces)==faces
assert all(v.is_valid for v in vertices)
bm.free()
"""))

    def test_bisect_caught_failure_preserves_editable_topology(self):
        self.hb('run', self.script("""import bmesh
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0))];face=bm.faces.new(vertices)
edges=list(bm.edges)
try:bmesh.ops.bisect_plane(bm,geom=[face,list(face.edges)[0]],plane_no=(1,0,0),use_snap_center=True)
except Exception as error:assert 'boundary edges' in str(error)
else:raise AssertionError('Incomplete cut selection accepted')
assert list(bm.verts)==vertices and list(bm.edges)==edges and list(bm.faces)==[face]
assert [tuple(v.co) for v in vertices]==[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)]
bm.free()
"""))

    def test_inset_caught_failure_preserves_editable_topology(self):
        self.hb('run', self.script('''import bmesh
bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)
vertices=[tuple(v.co) for v in bm.verts];faces=list(bm.faces)
for thickness in (1.,2.):
    try:bmesh.ops.inset_region(bm,faces=faces,thickness=thickness,use_even_offset=True,use_boundary=True)
    except Exception as error:assert 'collapses' in str(error)
    else:raise AssertionError('Collapsed inset accepted')
    assert [tuple(v.co) for v in bm.verts]==vertices
    assert list(bm.faces)==faces and all(f.is_valid for f in faces)
    assert len(bm.edges)==4
bm.free()
'''))

    def test_bevel_caught_failure_preserves_original_handles(self):
        self.hb('run', self.script('''import bmesh
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
vertices=list(bm.verts);edges=list(bm.edges);faces=list(bm.faces)
try:bmesh.ops.bevel(bm,geom=edges,offset=1)
except Exception as error:assert 'overlap' in str(error)
else:raise AssertionError('Overlapping bevel accepted')
assert list(bm.verts)==vertices and list(bm.edges)==edges and list(bm.faces)==faces
assert all(v.is_valid for group in (vertices,edges,faces) for v in group)
bm.free()
'''))

    def test_ico_limits_preserve_the_committed_scene(self):
        self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_ico_sphere_add()'), '--scene', 'a.hb')
        before = (self.path / 'a.hb').read_bytes()
        for parameters in ('subdivisions=8', 'align="VIEW"', 'enter_editmode=True'):
            with self.subTest(parameters=parameters):
                result = self.hb('run', self.script('import bpy\nbpy.ops.mesh.primitive_ico_sphere_add(' + parameters + ')'), '--scene', 'a.hb', ok=False)
                self.assertEqual(result['error']['code'], 'UNSUPPORTED_API')
                self.assertEqual((self.path / 'a.hb').read_bytes(), before)

    def test_parent_cycle_preserves_the_committed_scene(self):
        source = '''import bpy
bpy.ops.mesh.primitive_cube_add()
root=bpy.context.object;root.name='Root'
bpy.ops.object.empty_add()
child=bpy.context.object;child.name='Child';child.parent=root
root.select_set(True)
'''
        self.hb('run', self.script(source), '--scene', 'a.hb')
        before = (self.path / 'a.hb').read_bytes()
        result = self.hb('run', self.script('import bpy\nbpy.ops.object.parent_set()'), '--scene', 'a.hb', ok=False)
        self.assertIn('Cyclic parent relation', result['error']['message'])
        self.assertEqual((self.path / 'a.hb').read_bytes(), before)

    def test_origin_failure_can_be_caught_without_partial_edits(self):
        source = '''import bpy
bpy.ops.mesh.primitive_cube_add(location=(2,3,4))
obj=bpy.context.object
for vertex in obj.data.vertices:vertex.co.x+=2
obj.scale=(0,1,1)
child=bpy.data.objects.new('Child',None)
bpy.context.collection.objects.link(child);child.parent=obj
vertices=[tuple(v.co) for v in obj.data.vertices]
location=tuple(obj.location)
try:bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
except Exception as error:assert 'nonsingular' in str(error)
else:raise AssertionError('Singular parent accepted')
assert vertices==[tuple(v.co) for v in obj.data.vertices]
assert location==tuple(obj.location)
'''
        self.hb('run', self.script(source))
