# Real-source corpus coverage

Status: 400 scripts acquired.

| Origin | Scripts | Blender pass | hb check pass |
|---|---:|---:|---:|
| Claude Opus 5 | 150 | 138 | 0 |
| GPT-6 Astra | 150 | 98 | 0 |
| Blender StackExchange | 92 | 55 | 3 |
| GitHub gists | 8 | 7 | 0 |

Public licenses: 8 MIT gist files, 54 CC BY-SA 4.0 answer snippets and 38 CC BY-SA 3.0 answer snippets. The original share-alike licenses apply to the explicitly requested StackExchange sources; the permissive-license filter applies to gists. Per-file attribution, license URLs and snapshots are in the index and acquisition records.

`hb check`: **3/400 (0.75%)**. Blender 4.5.9 LTS: 298 pass, 102 invalid (3 process crashes), 0 unresolved process outcomes.

The denominator is every acquired script, including invalid ones. Frequencies count distinct scripts, once per symbol per script. Exactly 2% belongs to the at-or-above group. These are preflight results, not runtime or geometry equivalence.

Symbols use the current checker's static alias/type inference. Dynamic Python and unparsed syntax cannot be exhaustively enumerated. Parameter restrictions remain separate entries. Inferred parent paths appear alongside member paths; their percentages must not be summed. `bpy.types.IDData` is a checker placeholder for object data, not a Blender RNA type; its member paths retain that inference limitation.

5 syntax-error scripts remain in the denominator but have no resolved AST census; see `corpus/coverage.json` for their filenames. Unsupported tables report checker diagnostics, which can include false positives from type inference. In particular, `bpy.types.MeshPolygon.inputs[.default_value]` and `bpy.types.ShaderNode.use_smooth` reflect the checker conflating variables named `p` used for shader nodes and mesh polygons; these reported paths are not real RNA members. They remain visible as checker defects, not API implementation requests.

Invalid scripts remain byte-identical under `corpus/invalid/`. Each record contains Blender's exception and a direct hb runtime result. A second hb probe compiles the original unchanged source under its original filename and observes the exception class; its message and line must agree with the direct run before classification. Timeouts and infrastructure failures are unresolved, not script errors.

Invalid error comparisons: 6 identical class/message/line; 96 different errors; 0 unresolved. The requested same-error requirement is unmet wherever the errors differ; fixing hb is outside the permitted paths.

hb SHA-256: `d8f46caabedba0a8e53aa08226004bd7f0858218f038d13ea4b7b60aaecfd0cd`. Source hashes, prompts, responses, licenses and complete process logs are under `corpus/`.

## Top 20 unsupported symbols

| Symbol / restriction | Scripts | % |
|---|---:|---:|
| `bpy.context.scene.render.engine` | 234 | 58.50% |
| `bpy.ops.wm` | 225 | 56.25% |
| `bpy.ops.wm.read_factory_settings` | 220 | 55.00% |
| `bpy.types.World.node_tree` | 218 | 54.50% |
| `bpy.types.World.node_tree.nodes` | 218 | 54.50% |
| `bpy.types.World.use_nodes=True` | 217 | 54.25% |
| `bpy.data.curves` | 133 | 33.25% |
| `bpy.data.curves.new` | 133 | 33.25% |
| `bpy.context.scene.cycles` | 124 | 31.00% |
| `bpy.context.scene.cycles.samples` | 121 | 30.25% |
| `bpy.types.Light.angle` | 74 | 18.50% |
| `bpy.context.scene.unit_settings` | 74 | 18.50% |
| `bpy.context.scene.unit_settings.system` | 74 | 18.50% |
| `bmesh.ops.bevel` | 61 | 15.25% |
| `bpy.context.scene.view_settings` | 54 | 13.50% |
| `bpy.context.scene.view_settings.view_transform` | 52 | 13.00% |
| `bpy.types.Camera.dof` | 47 | 11.75% |
| `bpy.types.Camera.dof.use_dof` | 47 | 11.75% |
| `bpy.types.Camera.dof.aperture_fstop` | 46 | 11.50% |
| `bpy.types.Material.blend_method` | 44 | 11.00% |

## At or above 2%

| Symbol / restriction | Scripts | % | Unsupported in scripts |
|---|---:|---:|---:|
| `bpy.context` | 361 | 90.25% | 0 |
| `bpy.ops` | 341 | 85.25% | 0 |
| `bpy.data` | 328 | 82.00% | 0 |
| `bpy.context.scene` | 322 | 80.50% | 0 |
| `bpy.context.scene.camera` | 305 | 76.25% | 0 |
| `bpy.data.materials` | 303 | 75.75% | 0 |
| `bpy.data.materials.new` | 303 | 75.75% | 0 |
| `bpy.types.Material` | 303 | 75.75% | 0 |
| `mathutils.Vector` | 302 | 75.50% | 0 |
| `bpy.types.ShaderNode` | 301 | 75.25% | 0 |
| `bpy.types.ShaderNode.inputs` | 301 | 75.25% | 0 |
| `bpy.types.Object.location` | 300 | 75.00% | 0 |
| `bpy.types.Object.rotation_euler` | 299 | 74.75% | 0 |
| `bpy.types.Material.node_tree` | 298 | 74.50% | 0 |
| `bpy.types.Material.node_tree.nodes` | 298 | 74.50% | 0 |
| `bpy.types.Material.use_nodes` | 298 | 74.50% | 0 |
| `bpy.types.NodeSocket.default_value` | 298 | 74.50% | 0 |
| `bpy.context.scene.world` | 296 | 74.00% | 0 |
| `bpy.types.Object` | 294 | 73.50% | 0 |
| `mathutils.Vector.to_track_quat` | 287 | 71.75% | 0 |
| `mathutils.Quaternion.to_euler` | 286 | 71.50% | 0 |
| `bpy.data.objects` | 282 | 70.50% | 0 |
| `bpy.types.IDData` | 273 | 68.25% | 0 |
| `bpy.data.objects.new` | 272 | 68.00% | 0 |
| `bpy.types.Collection.objects` | 271 | 67.75% | 0 |
| `bpy.types.Collection.objects.link` | 271 | 67.75% | 0 |
| `bpy.context.scene.render` | 258 | 64.50% | 0 |
| `bpy.context.scene.render.engine` | 234 | 58.50% | 234 |
| `bpy.types.Modifier` | 227 | 56.75% | 0 |
| `bpy.types.Object.modifiers` | 227 | 56.75% | 0 |
| `bpy.types.IDData.materials` | 226 | 56.50% | 0 |
| `bpy.types.IDData.materials.append` | 226 | 56.50% | 0 |
| `bpy.context.scene.render.resolution_x` | 225 | 56.25% | 0 |
| `bpy.context.scene.render.resolution_y` | 225 | 56.25% | 0 |
| `bpy.ops.wm` | 225 | 56.25% | 225 |
| `bpy.types.Object.modifiers.new` | 225 | 56.25% | 0 |
| `bpy.ops.wm.read_factory_settings` | 220 | 55.00% | 220 |
| `bpy.types.Object.location.to_track_quat` | 219 | 54.75% | 0 |
| `bpy.data.meshes` | 218 | 54.50% | 0 |
| `bpy.data.meshes.new` | 218 | 54.50% | 0 |
| `bpy.types.Mesh` | 218 | 54.50% | 0 |
| `bpy.types.World.node_tree` | 218 | 54.50% | 218 |
| `bpy.types.World.node_tree.nodes` | 218 | 54.50% | 218 |
| `bpy.types.World.use_nodes` | 217 | 54.25% | 0 |
| `bpy.types.World.use_nodes=True` | 217 | 54.25% | 217 |
| `bpy.ops.mesh` | 216 | 54.00% | 0 |
| `bpy.ops.object` | 211 | 52.75% | 0 |
| `bpy.types.Object.name` | 203 | 50.75% | 0 |
| `mathutils.Vector.length` | 199 | 49.75% | 0 |
| `bpy.types.Modifier.segments` | 197 | 49.25% | 0 |
| `bpy.types.Modifier.width` | 197 | 49.25% | 0 |
| `bpy.context.object` | 191 | 47.75% | 0 |
| `bpy.types.MeshPolygon` | 186 | 46.50% | 0 |
| `bpy.types.Material.node_tree.nodes.get` | 181 | 45.25% | 0 |
| `bpy.data.worlds` | 180 | 45.00% | 0 |
| `bpy.types.MeshPolygon.use_smooth` | 180 | 45.00% | 0 |
| `bpy.data.worlds.new` | 179 | 44.75% | 0 |
| `bpy.ops.mesh.primitive_cylinder_add` | 178 | 44.50% | 0 |
| `bpy.context.collection` | 175 | 43.75% | 0 |
| `bpy.ops.mesh.primitive_cube_add` | 173 | 43.25% | 0 |
| `bpy.types.World` | 169 | 42.25% | 0 |
| `bpy.ops.object.transform_apply` | 163 | 40.75% | 0 |
| `bpy.data.lights` | 155 | 38.75% | 0 |
| `bpy.data.lights.new` | 155 | 38.75% | 0 |
| `bpy.types.Light` | 155 | 38.75% | 0 |
| `bpy.types.Light.energy` | 155 | 38.75% | 0 |
| `bpy.types.Material.diffuse_color` | 155 | 38.75% | 0 |
| `bpy.data.cameras` | 153 | 38.25% | 0 |
| `bpy.types.Camera` | 153 | 38.25% | 0 |
| `bpy.types.Light.size` | 153 | 38.25% | 0 |
| `bpy.ops.object.camera_add` | 153 | 38.25% | 0 |
| `bpy.data.cameras.new` | 151 | 37.75% | 0 |
| `bpy.types.Camera.lens` | 150 | 37.50% | 0 |
| `bpy.types.IDData.polygons` | 148 | 37.00% | 0 |
| `bpy.ops.object.light_add` | 148 | 37.00% | 0 |
| `bpy.context.scene.render.resolution_percentage` | 146 | 36.50% | 0 |
| `bpy.types.Object.dimensions` | 144 | 36.00% | 0 |
| `bmesh.new` | 143 | 35.75% | 0 |
| `bmesh.ops` | 142 | 35.50% | 0 |
| `bpy.types.IDData.size` | 142 | 35.50% | 0 |
| `bpy.types.IDData.energy` | 141 | 35.25% | 0 |
| `bpy.types.Light.color` | 138 | 34.50% | 0 |
| `bpy.types.IDData.ortho_scale` | 137 | 34.25% | 0 |
| `bpy.types.IDData.type` | 137 | 34.25% | 0 |
| `bmesh.types.BMesh` | 135 | 33.75% | 0 |
| `bmesh.types.BMesh.free` | 134 | 33.50% | 0 |
| `bmesh.types.BMesh.to_mesh` | 134 | 33.50% | 0 |
| `bpy.data.curves` | 133 | 33.25% | 133 |
| `bpy.data.curves.new` | 133 | 33.25% | 133 |
| `bpy.context.scene.cycles` | 124 | 31.00% | 124 |
| `bpy.context.scene.cycles.samples` | 121 | 30.25% | 121 |
| `bmesh.types.BMesh.verts` | 118 | 29.50% | 0 |
| `bmesh.types.BMesh.faces` | 116 | 29.00% | 0 |
| `bmesh.ops.create_cube` | 113 | 28.25% | 0 |
| `mathutils.Matrix` | 111 | 27.75% | 0 |
| `bmesh.ops.create_cone` | 101 | 25.25% | 0 |
| `bpy.types.Mesh.materials` | 101 | 25.25% | 0 |
| `bpy.types.Mesh.materials.append` | 101 | 25.25% | 0 |
| `bpy.context.scene.collection` | 97 | 24.25% | 0 |
| `bmesh.ops.recalc_face_normals` | 97 | 24.25% | 0 |
| `bpy.ops.object.select_all` | 95 | 23.75% | 0 |
| `bpy.types.Mesh.from_pydata` | 88 | 22.00% | 0 |
| `mathutils.Matrix.Translation` | 87 | 21.75% | 0 |
| `bpy.types.Mesh.update` | 87 | 21.75% | 0 |
| `bpy.types.Object.scale` | 86 | 21.50% | 0 |
| `bpy.ops.object.delete` | 86 | 21.50% | 0 |
| `bmesh.types.BMesh.verts.new` | 77 | 19.25% | 0 |
| `bpy.types.World.color` | 77 | 19.25% | 0 |
| `bpy.types.Light.angle` | 74 | 18.50% | 74 |
| `mathutils.Matrix.Diagonal` | 74 | 18.50% | 0 |
| `bpy.context.scene.unit_settings` | 74 | 18.50% | 74 |
| `bpy.context.scene.unit_settings.system` | 74 | 18.50% | 74 |
| `bpy.types.Mesh.polygons` | 73 | 18.25% | 0 |
| `bpy.types.ShaderNode.outputs` | 70 | 17.50% | 0 |
| `mathutils.Vector.normalized` | 70 | 17.50% | 0 |
| `bmesh.types.BMesh.edges` | 68 | 17.00% | 0 |
| `bmesh.types.BMesh.faces.new` | 68 | 17.00% | 0 |
| `mathutils.Vector.x` | 66 | 16.50% | 0 |
| `bpy.types.Modifier.thickness` | 63 | 15.75% | 0 |
| `bpy.types.Camera.clip_end` | 63 | 15.75% | 0 |
| `mathutils.Matrix.to_4x4` | 62 | 15.50% | 0 |
| `bmesh.ops.bevel` | 61 | 15.25% | 61 |
| `mathutils.Euler` | 61 | 15.25% | 0 |
| `bpy.context.view_layer` | 61 | 15.25% | 0 |
| `bpy.ops.mesh.primitive_uv_sphere_add` | 61 | 15.25% | 0 |
| `mathutils.Vector.y` | 59 | 14.75% | 0 |
| `bpy.types.Material.node_tree.nodes.new` | 59 | 14.75% | 0 |
| `bpy.types.Material.node_tree.links` | 58 | 14.50% | 0 |
| `bpy.types.Material.node_tree.links.new` | 58 | 14.50% | 0 |
| `bpy.types.Light.shape` | 57 | 14.25% | 0 |
| `mathutils.Matrix.Rotation` | 55 | 13.75% | 0 |
| `bpy.ops.mesh.primitive_torus_add` | 54 | 13.50% | 0 |
| `bmesh.types.BMFace` | 54 | 13.50% | 0 |
| `bpy.types.Light.shadow_soft_size` | 54 | 13.50% | 0 |
| `bpy.context.scene.view_settings` | 54 | 13.50% | 54 |
| `bmesh.types.BMVert` | 52 | 13.00% | 0 |
| `bpy.context.scene.view_settings.view_transform` | 52 | 13.00% | 52 |
| `bpy.types.Modifier.limit_method` | 51 | 12.75% | 0 |
| `bpy.types.Light.size_y` | 49 | 12.25% | 0 |
| `mathutils.Vector.z` | 47 | 11.75% | 0 |
| `bpy.types.Camera.dof` | 47 | 11.75% | 47 |
| `bpy.types.Camera.dof.use_dof` | 47 | 11.75% | 47 |
| `bmesh.ops.scale` | 46 | 11.50% | 0 |
| `bpy.types.Camera.dof.aperture_fstop` | 46 | 11.50% | 46 |
| `bpy.types.Material.blend_method` | 44 | 11.00% | 44 |
| `mathutils.Euler.to_matrix` | 43 | 10.75% | 0 |
| `bpy.types.Modifier.angle_limit` | 43 | 10.75% | 0 |
| `bpy.types.IDData.shape` | 42 | 10.50% | 0 |
| `bpy.types.Mesh.validate` | 40 | 10.00% | 40 |
| `bpy.types.Camera.clip_start` | 40 | 10.00% | 0 |
| `bpy.types.MeshPolygon.vertices` | 40 | 10.00% | 0 |
| `bpy.ops.object.text_add` | 40 | 10.00% | 40 |
| `bpy.types.IDData.body` | 40 | 10.00% | 40 |
| `bpy.context.view_layer.objects` | 39 | 9.75% | 0 |
| `bpy.context.view_layer.objects.active` | 39 | 9.75% | 0 |
| `bpy.types.Camera.dof.focus_distance` | 38 | 9.50% | 38 |
| `bpy.types.IDData.extrude` | 38 | 9.50% | 38 |
| `bpy.types.Modifier.offset` | 37 | 9.25% | 0 |
| `bpy.types.Modifier.split_angle` | 36 | 9.00% | 36 |
| `bpy.types.Object.modifiers.new(type='EDGE_SPLIT')` | 36 | 9.00% | 36 |
| `bpy.types.IDData.angle` | 36 | 9.00% | 36 |
| `bpy.context.active_object` | 36 | 9.00% | 0 |
| `bpy.ops.mesh.primitive_cone_add` | 36 | 9.00% | 0 |
| `bmesh.ops.create_uvsphere` | 33 | 8.25% | 0 |
| `bpy.types.Object.empty_display_size` | 32 | 8.00% | 0 |
| `bpy.types.Object.select_set` | 32 | 8.00% | 0 |
| `mathutils.Quaternion.to_matrix` | 32 | 8.00% | 0 |
| `bmesh.types.BMFace.smooth` | 31 | 7.75% | 0 |
| `bpy.types.ShaderNode.color_ramp` | 31 | 7.75% | 31 |
| `bpy.types.ShaderNode.color_ramp.elements` | 31 | 7.75% | 31 |
| `bpy.types.ShaderNode.color_ramp.elements.color` | 31 | 7.75% | 31 |
| `bpy.types.Object.rotation_euler.z` | 31 | 7.75% | 0 |
| `bpy.types.IDData.color` | 30 | 7.50% | 0 |
| `bpy.types` | 30 | 7.50% | 0 |
| `bpy.types.Object.rotation_euler.x` | 29 | 7.25% | 0 |
| `bmesh.ops.translate` | 28 | 7.00% | 0 |
| `mathutils.Vector.cross` | 28 | 7.00% | 0 |
| `bpy.types.IDData.align_x` | 28 | 7.00% | 28 |
| `mathutils.Vector.normalize` | 26 | 6.50% | 0 |
| `bpy.ops.mesh.primitive_plane_add` | 26 | 6.50% | 0 |
| `mathutils.Matrix.Identity` | 26 | 6.50% | 0 |
| `bmesh.types.BMFace.material_index` | 25 | 6.25% | 0 |
| `bpy.context.view_layer.update` | 25 | 6.25% | 0 |
| `bpy.utils.register_class` | 25 | 6.25% | 25 |
| `bpy.utils` | 25 | 6.25% | 25 |
| `bpy.data.collections` | 24 | 6.00% | 0 |
| `bpy.types.Collection` | 24 | 6.00% | 0 |
| `bpy.types.Object.matrix_world` | 24 | 6.00% | 24 |
| `bmesh.types.BMesh.normal_update` | 23 | 5.75% | 0 |
| `bmesh.types.BMesh.from_mesh` | 23 | 5.75% | 0 |
| `bpy.data.collections.new` | 23 | 5.75% | 0 |
| `bpy.types.Collection.children` | 23 | 5.75% | 0 |
| `bpy.types.Collection.children.link` | 23 | 5.75% | 0 |
| `bmesh.ops.remove_doubles` | 22 | 5.50% | 22 |
| `bmesh.ops.create_grid` | 21 | 5.25% | 0 |
| `bmesh.ops.create_icosphere` | 21 | 5.25% | 21 |
| `bpy.ops.mesh.primitive_ico_sphere_add` | 21 | 5.25% | 21 |
| `bpy.types.ShaderNode.location` | 20 | 5.00% | 20 |
| `bmesh.types.BMFace.normal` | 20 | 5.00% | 0 |
| `bpy.ops.mesh.primitive_ico_sphere_add(radius=...)` | 20 | 5.00% | 20 |
| `bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=...)` | 20 | 5.00% | 20 |
| `bpy.ops.object.shade_auto_smooth` | 20 | 5.00% | 20 |
| `bpy.types.ShaderNode.color_ramp.elements.position` | 20 | 5.00% | 20 |
| `mathutils.Vector.lerp` | 19 | 4.75% | 0 |
| `bpy.utils.unregister_class` | 19 | 4.75% | 19 |
| `bmesh.types.BMEdge` | 18 | 4.50% | 0 |
| `bpy.data.objects.remove` | 18 | 4.50% | 0 |
| `mathutils.Quaternion` | 18 | 4.50% | 0 |
| `bmesh.types.BMVert.co` | 17 | 4.25% | 0 |
| `bmesh.ops.spin` | 17 | 4.25% | 17 |
| `bpy.types.Camera.sensor_width` | 17 | 4.25% | 0 |
| `bpy.types.Object.rotation_euler.y` | 17 | 4.25% | 0 |
| `bmesh.types.BMesh.edges.new` | 16 | 4.00% | 0 |
| `bmesh.types.BMVert.link_faces` | 16 | 4.00% | 16 |
| `bpy.types.Operator` | 16 | 4.00% | 16 |
| `bpy.context.scene.objects` | 15 | 3.75% | 0 |
| `bmesh.types.BMVert.co.z` | 15 | 3.75% | 0 |
| `bmesh.types.BMFace.normal.z` | 15 | 3.75% | 0 |
| `bpy.context.selected_objects` | 15 | 3.75% | 0 |
| `bpy.types.Object.rotation_mode` | 15 | 3.75% | 0 |
| `bpy.types.Object.rotation_quaternion` | 15 | 3.75% | 15 |
| `bmesh.types` | 15 | 3.75% | 0 |
| `bmesh.types.BMVert.co.x` | 14 | 3.50% | 0 |
| `bpy.types.Light.spot_blend` | 14 | 3.50% | 0 |
| `bpy.types.Light.spot_size` | 14 | 3.50% | 0 |
| `bpy.types.World.node_tree.links` | 14 | 3.50% | 14 |
| `bpy.types.World.node_tree.links.new` | 14 | 3.50% | 14 |
| `bpy.types.World.node_tree.nodes.new` | 14 | 3.50% | 14 |
| `bpy.context.scene.cycles.use_denoising` | 14 | 3.50% | 14 |
| `bpy.types.Object.empty_display_type` | 14 | 3.50% | 0 |
| `bpy.types.ShaderNode.operation` | 14 | 3.50% | 14 |
| `mathutils.Vector.dot` | 13 | 3.25% | 0 |
| `bpy.context.scene.unit_settings.length_unit` | 13 | 3.25% | 13 |
| `bmesh.ops.extrude_face_region` | 13 | 3.25% | 0 |
| `bmesh.types.BMElement` | 13 | 3.25% | 0 |
| `bpy.types.ShaderNode.sun_elevation` | 13 | 3.25% | 13 |
| `bpy.types.ShaderNode.sun_rotation` | 13 | 3.25% | 13 |
| `bpy.types.Material.surface_render_method` | 13 | 3.25% | 13 |
| `bpy.types.MeshPolygon.inputs` | 13 | 3.25% | 13 |
| `bpy.types.MeshPolygon.inputs.default_value` | 13 | 3.25% | 13 |
| `bmesh.types.BMVert.co.y` | 12 | 3.00% | 0 |
| `bpy.types.Object.location.length` | 12 | 3.00% | 0 |
| `bpy.types.Object.constraints` | 12 | 3.00% | 12 |
| `bpy.types.ShaderNode.use_smooth` | 12 | 3.00% | 12 |
| `bmesh.from_edit_mesh` | 12 | 3.00% | 12 |
| `bmesh.types.BMEdge.calc_face_angle` | 11 | 2.75% | 11 |
| `bmesh.types.BMEdge.smooth` | 11 | 2.75% | 11 |
| `bpy.types.Object.matrix_parent_inverse` | 11 | 2.75% | 11 |
| `bmesh.ops.transform` | 11 | 2.75% | 0 |
| `bpy.types.Object.constraints.new` | 11 | 2.75% | 11 |
| `bpy.ops.object.mode_set` | 11 | 2.75% | 11 |
| `bpy.types.World.node_tree.nodes.get` | 10 | 2.50% | 10 |
| `bpy.ops.object.modifier_apply` | 10 | 2.50% | 0 |
| `bpy.types.Modifier.name` | 10 | 2.50% | 0 |
| `bpy.types.Modifier.object` | 10 | 2.50% | 0 |
| `bpy.types.Modifier.operation` | 10 | 2.50% | 0 |
| `bpy.types.ShaderNode.sky_type` | 10 | 2.50% | 10 |
| `bpy.types.IDData.materials.clear` | 10 | 2.50% | 0 |
| `bpy.types.Object.type` | 10 | 2.50% | 0 |
| `bpy.props` | 10 | 2.50% | 10 |
| `bpy.context.scene.render.film_transparent` | 9 | 2.25% | 9 |
| `bpy.types.Camera.dof.focus_object` | 9 | 2.25% | 9 |
| `bpy.types.Modifier.solver` | 9 | 2.25% | 0 |
| `bpy.types.Modifier.solver='EXACT'` | 9 | 2.25% | 9 |
| `bpy.types.IDData.update` | 9 | 2.25% | 0 |
| `bpy.data.meshes.remove` | 9 | 2.25% | 0 |
| `bpy.types.Modifier.use_edge_sharp` | 9 | 2.25% | 9 |
| `bpy.types.IDData.align_y` | 9 | 2.25% | 9 |
| `bpy.context.scene.cycles.transmission_bounces` | 9 | 2.25% | 9 |
| `bpy.ops.object.empty_add` | 9 | 2.25% | 0 |
| `bpy.types.IDData.lens` | 9 | 2.25% | 0 |
| `bpy.ops.object.editmode_toggle` | 9 | 2.25% | 9 |
| `bpy.types.Object.mode` | 9 | 2.25% | 9 |
| `bpy.props.StringProperty` | 9 | 2.25% | 9 |
| `bmesh.types.BMFace.verts` | 8 | 2.00% | 0 |
| `bpy.types.ShaderNode.inputs.get` | 8 | 2.00% | 8 |
| `bmesh.ops.rotate` | 8 | 2.00% | 0 |
| `bpy.ops.object.shade_smooth` | 8 | 2.00% | 0 |
| `bmesh.types.BMesh.verts.ensure_lookup_table` | 8 | 2.00% | 0 |
| `bpy.types.ShaderNode.wave_type` | 8 | 2.00% | 8 |
| `bpy.context.scene.frame_end` | 8 | 2.00% | 8 |
| `bpy.ops.object.camera_add(align='VIEW')` | 8 | 2.00% | 8 |
| `bpy.ops.render` | 8 | 2.00% | 8 |
| `bpy.ops.render.render` | 8 | 2.00% | 8 |
| `bpy.ops.transform` | 8 | 2.00% | 8 |
| `bpy.types.Panel` | 8 | 2.00% | 8 |
| `bpy.types.Scene` | 8 | 2.00% | 8 |

## Below 2%

| Symbol / restriction | Scripts | % | Unsupported in scripts |
|---|---:|---:|---:|
| `bmesh.types.BMEdge.link_faces` | 7 | 1.75% | 7 |
| `mathutils.Matrix.normalized` | 7 | 1.75% | 7 |
| `mathutils.Matrix.to_3x3` | 7 | 1.75% | 0 |
| `mathutils.Vector.to_4d` | 7 | 1.75% | 0 |
| `bmesh.ops.delete` | 7 | 1.75% | 0 |
| `bmesh.types.BMVert.link_edges` | 7 | 1.75% | 7 |
| `bpy.types.IDData.transform` | 7 | 1.75% | 7 |
| `mathutils.Vector.rotation_difference` | 7 | 1.75% | 7 |
| `bpy.types.MeshPolygon.normal` | 7 | 1.75% | 7 |
| `bpy.types.IDData.vertices` | 7 | 1.75% | 0 |
| `bpy.types.Material.node_tree.nodes.remove` | 7 | 1.75% | 7 |
| `bpy.types.Material.node_tree.links.get` | 7 | 1.75% | 7 |
| `bpy.ops.transform.rotate` | 7 | 1.75% | 7 |
| `bpy.types.PropertyGroup` | 7 | 1.75% | 7 |
| `bpy.app` | 7 | 1.75% | 7 |
| `bmesh.types.BMesh.verts.index_update` | 6 | 1.50% | 0 |
| `bpy.types.IDData.shadow_soft_size` | 6 | 1.50% | 0 |
| `bpy.types.Material.node_tree.links.inputs` | 6 | 1.50% | 6 |
| `bpy.types.Material.node_tree.links.inputs.default_value` | 6 | 1.50% | 6 |
| `bpy.types.MeshPolygon.material_index` | 6 | 1.50% | 0 |
| `bpy.types.Object.matrix_world.inverted` | 6 | 1.50% | 6 |
| `mathutils.Vector.copy` | 6 | 1.50% | 0 |
| `bpy.types.MeshPolygon.normal.z` | 6 | 1.50% | 6 |
| `bpy.types.MeshVertex` | 6 | 1.50% | 0 |
| `bpy.types.MeshVertex.co` | 6 | 1.50% | 0 |
| `bmesh.types.BMVert.link_faces.material_index` | 6 | 1.50% | 6 |
| `bpy.types.IDData.dof` | 6 | 1.50% | 6 |
| `bpy.types.IDData.dof.use_dof` | 6 | 1.50% | 6 |
| `bpy.types.ShaderNode.bands_direction` | 6 | 1.50% | 6 |
| `bpy.types.ShaderNode.altitude` | 6 | 1.50% | 6 |
| `bpy.context.scene.cycles.preview_samples` | 6 | 1.50% | 6 |
| `bpy.props.CollectionProperty` | 6 | 1.50% | 6 |
| `bpy.app.handlers` | 6 | 1.50% | 6 |
| `bmesh.types.BMVert.index` | 5 | 1.25% | 0 |
| `bmesh.types.BMFace.normal.normalized` | 5 | 1.25% | 0 |
| `bpy.ops.object.shade_smooth_by_angle` | 5 | 1.25% | 5 |
| `bpy.types.Material.node_tree.nodes.clear` | 5 | 1.25% | 0 |
| `bpy.types.Object.location.z` | 5 | 1.25% | 0 |
| `bpy.data.materials.remove` | 5 | 1.25% | 0 |
| `mathutils.Vector.length.y` | 5 | 1.25% | 5 |
| `mathutils.noise` | 5 | 1.25% | 5 |
| `mathutils.noise.noise` | 5 | 1.25% | 5 |
| `mathutils.Matrix.to_euler` | 5 | 1.25% | 0 |
| `mathutils.Vector.angle` | 5 | 1.25% | 0 |
| `bpy.context.scene.cycles.max_bounces` | 5 | 1.25% | 5 |
| `bpy.types.IDData.dof.aperture_fstop` | 5 | 1.25% | 5 |
| `bpy.types.Modifier.use_clamp_overlap` | 5 | 1.25% | 0 |
| `bpy.context.scene.view_settings.look` | 5 | 1.25% | 5 |
| `bpy.types.ShaderNode.type` | 5 | 1.25% | 0 |
| `bpy.context.scene.frame_start` | 5 | 1.25% | 5 |
| `bpy.data.collections.get` | 5 | 1.25% | 0 |
| `mathutils.Vector.length.length` | 5 | 1.25% | 5 |
| `bpy.ops.mesh.poke` | 5 | 1.25% | 5 |
| `bpy.ops.object.material_slot_assign` | 5 | 1.25% | 5 |
| `bpy.types.Object.active_material_index` | 5 | 1.25% | 5 |
| `bpy.props.EnumProperty` | 5 | 1.25% | 5 |
| `bpy.types.Menu` | 5 | 1.25% | 5 |
| `bmesh.types.BMFace.calc_center_median` | 4 | 1.00% | 4 |
| `bpy.types.ShaderNode.color_ramp.elements.new` | 4 | 1.00% | 4 |
| `bmesh.types.BMVert.link_faces.smooth` | 4 | 1.00% | 4 |
| `mathutils.Vector.length.x` | 4 | 1.00% | 4 |
| `mathutils.Quaternion.length` | 4 | 1.00% | 4 |
| `bpy.types.Material.use_backface_culling` | 4 | 1.00% | 4 |
| `bpy.types.Modifier.harden_normals` | 4 | 1.00% | 0 |
| `mathutils.Matrix.to_track_quat` | 4 | 1.00% | 4 |
| `bpy.types.Collection.objects.unlink` | 4 | 1.00% | 0 |
| `bpy.types.ShaderNode.color_ramp.interpolation` | 4 | 1.00% | 4 |
| `bpy.types.ShaderNode.wave_profile` | 4 | 1.00% | 4 |
| `bpy.types.MeshPolygon.index` | 4 | 1.00% | 0 |
| `bpy.types.IDData.clip_end` | 4 | 1.00% | 0 |
| `bpy.ops.mesh.subdivide` | 4 | 1.00% | 4 |
| `bpy.context.screen` | 4 | 1.00% | 4 |
| `bpy.context.screen.areas` | 4 | 1.00% | 4 |
| `bpy.context.screen.areas.type` | 4 | 1.00% | 4 |
| `bpy.props.BoolProperty` | 4 | 1.00% | 4 |
| `bpy.props.IntProperty` | 4 | 1.00% | 4 |
| `bpy.context.edit_object` | 4 | 1.00% | 4 |
| `bpy.context.edit_object.data` | 4 | 1.00% | 4 |
| `bpy.context.scene.objects.active` | 4 | 1.00% | 4 |
| `bpy.types.Camera.shift_y` | 3 | 0.75% | 0 |
| `bpy.types.Modifier.use_rim` | 3 | 0.75% | 0 |
| `bmesh.ops.subdivide_edges` | 3 | 0.75% | 3 |
| `bmesh.types.BMesh.faces.ensure_lookup_table` | 3 | 0.75% | 0 |
| `bpy.types.Modifier.use_edge_angle` | 3 | 0.75% | 3 |
| `bpy.ops.object.join` | 3 | 0.75% | 0 |
| `bpy.types.Object.copy` | 3 | 0.75% | 0 |
| `bpy.types.Modifier.levels` | 3 | 0.75% | 0 |
| `mathutils.Vector.length.z` | 3 | 0.75% | 3 |
| `bpy.types.Modifier.use_even_offset` | 3 | 0.75% | 0 |
| `bpy.data.curves.remove` | 3 | 0.75% | 3 |
| `mathutils.Matrix.transposed` | 3 | 0.75% | 0 |
| `mathutils.Matrix.x` | 3 | 0.75% | 3 |
| `bpy.context.scene.cycles.transparent_max_bounces` | 3 | 0.75% | 3 |
| `bpy.types.Camera.ortho_scale` | 3 | 0.75% | 0 |
| `bpy.types.Camera.type` | 3 | 0.75% | 0 |
| `bpy.types.ShaderNode.blend_type` | 3 | 0.75% | 3 |
| `bpy.context.scene.frame_set` | 3 | 0.75% | 3 |
| `bpy.types.Object.keyframe_insert` | 3 | 0.75% | 3 |
| `mathutils.Matrix.length` | 3 | 0.75% | 3 |
| `bpy.types.ShaderNode.air_density` | 3 | 0.75% | 3 |
| `bpy.types.ShaderNode.dust_density` | 3 | 0.75% | 3 |
| `bpy.types.Object.material_slots` | 3 | 0.75% | 3 |
| `bpy.types.Object.material_slots.material` | 3 | 0.75% | 3 |
| `bpy.data.cameras.remove` | 3 | 0.75% | 0 |
| `bpy.types.Material.inputs` | 3 | 0.75% | 3 |
| `bpy.types.Material.inputs.default_value` | 3 | 0.75% | 3 |
| `bpy.types.IDData.size_y` | 3 | 0.75% | 0 |
| `bpy.types.MeshPolygon.co` | 3 | 0.75% | 3 |
| `bpy.types.ShaderNode.co` | 3 | 0.75% | 3 |
| `mathutils.Quaternion.to_track_quat` | 3 | 0.75% | 3 |
| `bpy.types.IDData.dof.focus_object` | 3 | 0.75% | 3 |
| `bpy.context.area` | 3 | 0.75% | 3 |
| `bpy.context.copy` | 3 | 0.75% | 3 |
| `bpy.context.screen.areas.spaces` | 3 | 0.75% | 3 |
| `bpy.context.window` | 3 | 0.75% | 3 |
| `bpy.props.FloatProperty` | 3 | 0.75% | 3 |
| `bpy.props.PointerProperty` | 3 | 0.75% | 3 |
| `bmesh.update_edit_mesh` | 3 | 0.75% | 3 |
| `bpy.types.MeshPolygon.select` | 3 | 0.75% | 3 |
| `bpy.ops.mesh.reveal` | 3 | 0.75% | 3 |
| `bpy.ops.mesh.select_all` | 3 | 0.75% | 3 |
| `bpy.data.node_groups` | 3 | 0.75% | 3 |
| `bpy.data.scenes` | 3 | 0.75% | 3 |
| `bpy.types.ShaderNode.gradient_type` | 2 | 0.50% | 2 |
| `bmesh.ops.triangulate` | 2 | 0.50% | 2 |
| `bpy.ops.object.convert` | 2 | 0.50% | 2 |
| `bmesh.types.BMVert.link_faces.verts` | 2 | 0.50% | 2 |
| `bmesh.types.BMEdge.verts` | 2 | 0.50% | 0 |
| `bpy.types.ShaderNode.offset` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.squash` | 2 | 0.50% | 2 |
| `mathutils.Matrix.translation` | 2 | 0.50% | 0 |
| `bpy.types.MeshPolygon.center` | 2 | 0.50% | 2 |
| `bpy.types.MeshPolygon.center.z` | 2 | 0.50% | 2 |
| `mathutils.Vector.rotate` | 2 | 0.50% | 2 |
| `bmesh.ops.inset_individual` | 2 | 0.50% | 2 |
| `bmesh.types.BMFace.edges` | 2 | 0.50% | 0 |
| `bpy.types.Modifier.material_offset` | 2 | 0.50% | 0 |
| `bpy.types.Modifier.material_offset_rim` | 2 | 0.50% | 0 |
| `bpy.ops.mesh.primitive_grid_add` | 2 | 0.50% | 2 |
| `bpy.ops.mesh.primitive_grid_add(size=...)` | 2 | 0.50% | 2 |
| `bpy.ops.mesh.primitive_grid_add(x_subdivisions=...)` | 2 | 0.50% | 2 |
| `bpy.ops.mesh.primitive_grid_add(y_subdivisions=...)` | 2 | 0.50% | 2 |
| `bpy.types.MeshVertex.co.z` | 2 | 0.50% | 0 |
| `bpy.types.Object.name.startswith` | 2 | 0.50% | 2 |
| `bpy.ops.object.origin_set` | 2 | 0.50% | 2 |
| `bpy.types.IDData.skin_vertices` | 2 | 0.50% | 2 |
| `bpy.types.IDData.skin_vertices.data` | 2 | 0.50% | 2 |
| `bpy.types.IDData.skin_vertices.data.radius` | 2 | 0.50% | 2 |
| `bpy.types.Modifier.render_levels` | 2 | 0.50% | 0 |
| `bpy.types.Object.modifiers.new(type='SKIN')` | 2 | 0.50% | 2 |
| `bpy.types.Modifier.use_replace` | 2 | 0.50% | 2 |
| `bpy.types.Object.modifiers.new(type='WIREFRAME')` | 2 | 0.50% | 2 |
| `bpy.types.IDData.dof.focus_distance` | 2 | 0.50% | 2 |
| `mathutils.Matrix.y` | 2 | 0.50% | 2 |
| `mathutils.Matrix.z` | 2 | 0.50% | 2 |
| `bpy.types.Camera.dof.aperture_blades` | 2 | 0.50% | 2 |
| `bpy.types.Camera.sensor_fit` | 2 | 0.50% | 0 |
| `bpy.context.scene.timeline_markers` | 2 | 0.50% | 2 |
| `bpy.context.scene.timeline_markers.new` | 2 | 0.50% | 2 |
| `bpy.types.Object.rotation_euler.copy` | 2 | 0.50% | 2 |
| `bpy.types.Object.rotation_euler.to_matrix` | 2 | 0.50% | 0 |
| `bpy.types.Object.to_track_quat` | 2 | 0.50% | 2 |
| `bpy.types.Object.animation_data` | 2 | 0.50% | 2 |
| `bpy.types.Object.animation_data.action` | 2 | 0.50% | 2 |
| `bpy.types.Object.animation_data.action.fcurves` | 2 | 0.50% | 2 |
| `bpy.types.Object.animation_data.action.fcurves.keyframe_points` | 2 | 0.50% | 2 |
| `bpy.types.Object.animation_data.action.fcurves.keyframe_points.interpolation` | 2 | 0.50% | 2 |
| `bpy.types.Object.users_collection` | 2 | 0.50% | 0 |
| `bpy.context.view_layer.active_layer_collection` | 2 | 0.50% | 2 |
| `bpy.context.view_layer.layer_collection` | 2 | 0.50% | 2 |
| `bpy.context.view_layer.layer_collection.children` | 2 | 0.50% | 2 |
| `bpy.data.materials.get` | 2 | 0.50% | 0 |
| `bpy.types.Object.matrix_world.length` | 2 | 0.50% | 2 |
| `bpy.types.Object.matrix_world.normalized` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.to_track_quat` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 2 | 0.50% | 2 |
| `bpy.types.World.node_tree.nodes.remove` | 2 | 0.50% | 2 |
| `mathutils.Euler.z` | 2 | 0.50% | 0 |
| `bmesh.ops.create_circle` | 2 | 0.50% | 0 |
| `bpy.data.lights.remove` | 2 | 0.50% | 0 |
| `bpy.types.Camera.users` | 2 | 0.50% | 0 |
| `bpy.types.Light.users` | 2 | 0.50% | 0 |
| `bpy.types.Material.users` | 2 | 0.50% | 0 |
| `bpy.types.Mesh.users` | 2 | 0.50% | 0 |
| `bpy.types.Collection.name` | 2 | 0.50% | 0 |
| `bpy.types.Material.links` | 2 | 0.50% | 2 |
| `bpy.types.Material.links.new` | 2 | 0.50% | 2 |
| `bpy.types.Material.node_tree.blend_method` | 2 | 0.50% | 2 |
| `bpy.types.Material.node_tree.inputs` | 2 | 0.50% | 2 |
| `bpy.types.Material.node_tree.inputs.default_value` | 2 | 0.50% | 2 |
| `bpy.types.Material.node_tree.use_backface_culling` | 2 | 0.50% | 2 |
| `bpy.types.Material.nodes` | 2 | 0.50% | 2 |
| `bpy.types.Material.nodes.new` | 2 | 0.50% | 2 |
| `bpy.types.Object.hide_render` | 2 | 0.50% | 0 |
| `bpy.types.Object.hide_viewport` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.blend_method` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.links` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.links.new` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.nodes` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.nodes.new` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.use_backface_culling` | 2 | 0.50% | 2 |
| `bpy.types.ShaderNode.color_ramp.elements.remove` | 2 | 0.50% | 2 |
| `bpy.types.Object.scale.y` | 2 | 0.50% | 0 |
| `bpy.types.IDData.splines` | 2 | 0.50% | 2 |
| `bpy.types.Object.scale.x` | 2 | 0.50% | 0 |
| `bpy.types.IDData.clip_start` | 2 | 0.50% | 0 |
| `bpy.types.ShaderNode.material_index` | 2 | 0.50% | 2 |
| `bpy.data.objects.get` | 2 | 0.50% | 0 |
| `bpy.data.actions` | 2 | 0.50% | 2 |
| `bpy.ops.curve` | 2 | 0.50% | 2 |
| `bpy.types.Camera.name` | 2 | 0.50% | 0 |
| `bpy.ops.screen` | 2 | 0.50% | 2 |
| `bpy.ops.screen.screen_full_area` | 2 | 0.50% | 2 |
| `bpy.props.FloatVectorProperty` | 2 | 0.50% | 2 |
| `bpy.types.AddonPreferences` | 2 | 0.50% | 2 |
| `bpy.types.Scene.my_tool` | 2 | 0.50% | 2 |
| `mathutils.Matrix.Scale` | 2 | 0.50% | 0 |
| `bpy.utils.unregister_module` | 2 | 0.50% | 2 |
| `bpy.context.window.screen` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas.regions` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas.regions.type` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas.spaces` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas.spaces.region_3d` | 2 | 0.50% | 2 |
| `bpy.context.window.screen.areas.type` | 2 | 0.50% | 2 |
| `bpy.types.IDData.view_frame` | 2 | 0.50% | 2 |
| `bpy.context.scene.node_tree` | 2 | 0.50% | 2 |
| `bpy.context.scene.node_tree.nodes` | 2 | 0.50% | 2 |
| `bpy.context.scene.node_tree.nodes.new` | 2 | 0.50% | 2 |
| `bpy.msgbus` | 2 | 0.50% | 2 |
| `bpy.msgbus.subscribe_rna` | 2 | 0.50% | 2 |
| `bpy.types.SpaceView3D` | 2 | 0.50% | 2 |
| `bpy.types.SpaceView3D.draw_handler_add` | 2 | 0.50% | 2 |
| `bpy.types.SpaceView3D.draw_handler_remove` | 2 | 0.50% | 2 |
| `bpy.ops.object.duplicate_move` | 2 | 0.50% | 2 |
| `bpy.ops.mesh.remove_doubles` | 2 | 0.50% | 2 |
| `bpy.app.handlers.load_post` | 2 | 0.50% | 2 |
| `bpy.app.handlers.load_post.append` | 2 | 0.50% | 2 |
| `bpy.app.handlers.persistent` | 2 | 0.50% | 2 |
| `bpy.types.IDData.loops` | 2 | 0.50% | 2 |
| `bpy.types.Object.active_material` | 2 | 0.50% | 2 |
| `bpy.types.Object.active_material.node_tree` | 2 | 0.50% | 2 |
| `bpy.types.Object.active_material.node_tree.nodes` | 2 | 0.50% | 2 |
| `bpy.context.scene.customLists` | 2 | 0.50% | 2 |
| `bpy.context.scene.customLists.add` | 2 | 0.50% | 2 |
| `bpy.context.scene.customLists.subLists` | 2 | 0.50% | 2 |
| `bpy.context.scene.customLists.subLists.add` | 2 | 0.50% | 2 |
| `bpy.types.Scene.customLists` | 2 | 0.50% | 2 |
| `bpy.types.Object.matrix_world.decompose` | 2 | 0.50% | 2 |
| `bpy.data.node_groups.new` | 2 | 0.50% | 2 |
| `bpy.types.Object.pose` | 2 | 0.50% | 2 |
| `bpy.types.Object.pose.bones` | 2 | 0.50% | 2 |
| `bpy.ops.uv` | 2 | 0.50% | 2 |
| `bpy.context.scene.update` | 2 | 0.50% | 2 |
| `bpy.types.Object.x` | 1 | 0.25% | 1 |
| `bpy.types.Object.y` | 1 | 0.25% | 1 |
| `bpy.types.Object.z` | 1 | 0.25% | 1 |
| `mathutils.Vector.parent` | 1 | 0.25% | 1 |
| `bmesh.types.BMVert.co.length` | 1 | 0.25% | 0 |
| `bpy.types.IDData.name` | 1 | 0.25% | 0 |
| `mathutils.Matrix.copy` | 1 | 0.25% | 0 |
| `bpy.types.IDData.bevel_resolution` | 1 | 0.25% | 1 |
| `bpy.types.Material.verts` | 1 | 0.25% | 1 |
| `bpy.types.Material.verts.link_edges` | 1 | 0.25% | 1 |
| `bpy.types.Material.verts.link_faces` | 1 | 0.25% | 1 |
| `bpy.types.Material.verts.link_faces.smooth` | 1 | 0.25% | 1 |
| `bpy.types.Material.verts.link_faces.verts` | 1 | 0.25% | 1 |
| `bpy.types.IDData.auto_smooth_angle` | 1 | 0.25% | 1 |
| `bpy.types.IDData.use_auto_smooth` | 1 | 0.25% | 1 |
| `mathutils.Matrix.append` | 1 | 0.25% | 1 |
| `mathutils.Matrix.translation.z` | 1 | 0.25% | 0 |
| `bpy.types.Camera.dof.aperture_fsize` | 1 | 0.25% | 1 |
| `bpy.types.Collection.all_objects` | 1 | 0.25% | 1 |
| `bpy.types.MeshVertex.co.x` | 1 | 0.25% | 0 |
| `bpy.types.MeshVertex.co.y` | 1 | 0.25% | 0 |
| `bpy.types.IDData.bevel_depth` | 1 | 0.25% | 1 |
| `bpy.types.IDData.space_character` | 1 | 0.25% | 1 |
| `bmesh.types.BMFace.normal.x` | 1 | 0.25% | 0 |
| `bpy.types.IDData.skin_vertices.data.use_root` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.use_smooth_shade` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.use_boundary` | 1 | 0.25% | 1 |
| `bpy.data.textures` | 1 | 0.25% | 0 |
| `bpy.data.textures.new` | 1 | 0.25% | 0 |
| `bpy.types.CloudsTexture` | 1 | 0.25% | 0 |
| `bpy.types.CloudsTexture.noise_depth` | 1 | 0.25% | 0 |
| `bpy.types.CloudsTexture.noise_scale` | 1 | 0.25% | 0 |
| `bpy.types.Modifier.mid_level` | 1 | 0.25% | 0 |
| `bpy.types.Modifier.strength` | 1 | 0.25% | 0 |
| `bpy.types.Modifier.texture` | 1 | 0.25% | 0 |
| `bpy.context.evaluated_depsgraph_get` | 1 | 0.25% | 1 |
| `bpy.data.meshes.new_from_object` | 1 | 0.25% | 1 |
| `bpy.types.Object.evaluated_get` | 1 | 0.25% | 1 |
| `bmesh.ops.inset_region` | 1 | 0.25% | 1 |
| `bmesh.types.BMElement.co` | 1 | 0.25% | 0 |
| `bmesh.types.BMElement.co.x` | 1 | 0.25% | 0 |
| `bmesh.types.BMElement.co.y` | 1 | 0.25% | 0 |
| `bmesh.types.BMElement.co.z` | 1 | 0.25% | 0 |
| `bpy.types.ShaderNode.axis` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.direction_type` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.turbidity` | 1 | 0.25% | 1 |
| `bpy.types.Object.children` | 1 | 0.25% | 0 |
| `bpy.types.Object.rotation_euler.rotate_axis` | 1 | 0.25% | 1 |
| `bpy.types.Object.animation_data.action.fcurves.extrapolation` | 1 | 0.25% | 1 |
| `bmesh.types.BMVert.append` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.miter_outer` | 1 | 0.25% | 1 |
| `mathutils.Quaternion.cross` | 1 | 0.25% | 1 |
| `mathutils.Quaternion.dot` | 1 | 0.25% | 0 |
| `mathutils.Quaternion.normalized` | 1 | 0.25% | 0 |
| `mathutils.Quaternion.rotation_difference` | 1 | 0.25% | 1 |
| `mathutils.Vector.to_euler` | 1 | 0.25% | 1 |
| `mathutils.Matrix.to_quaternion` | 1 | 0.25% | 0 |
| `bpy.types.Light.use_shadow` | 1 | 0.25% | 0 |
| `bpy.types.Material.metallic` | 1 | 0.25% | 0 |
| `bpy.types.Material.roughness` | 1 | 0.25% | 0 |
| `mathutils.Vector.length.angle` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.cross` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.normalize` | 1 | 0.25% | 1 |
| `mathutils.noise.fractal` | 1 | 0.25% | 1 |
| `bmesh.types.BMVert.tag` | 1 | 0.25% | 1 |
| `bpy.types.IDData.set_sharp_from_angle` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_world.length.length` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_world.length.to_track_quat` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_world.to_track_quat` | 1 | 0.25% | 1 |
| `bpy.types.World.node_tree.nodes.clear` | 1 | 0.25% | 1 |
| `bpy.types.Material.use_transparent_shadow` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.sun_intensity` | 1 | 0.25% | 1 |
| `bmesh.ops.solidify` | 1 | 0.25% | 1 |
| `bpy.types.Object.material_slots.link` | 1 | 0.25% | 1 |
| `bpy.types.Material.node_tree.links.clear` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_basis` | 1 | 0.25% | 1 |
| `bmesh.ops.reverse_faces` | 1 | 0.25% | 1 |
| `bmesh.types.BMEdge.link_faces.verts` | 1 | 0.25% | 1 |
| `bmesh.types.BMElement.link_faces` | 1 | 0.25% | 1 |
| `bmesh.types.BMElement.link_faces.verts` | 1 | 0.25% | 1 |
| `bpy.data.worlds.get` | 1 | 0.25% | 0 |
| `bpy.types.Light.spread` | 1 | 0.25% | 1 |
| `bpy.types.Object.display_type` | 1 | 0.25% | 1 |
| `bpy.types.Light.diffuse_factor` | 1 | 0.25% | 1 |
| `bpy.types.Light.specular_factor` | 1 | 0.25% | 1 |
| `bpy.types.NodeSocket` | 1 | 0.25% | 0 |
| `bpy.types.ShaderNode.feature` | 1 | 0.25% | 1 |
| `mathutils.Vector.to_tuple` | 1 | 0.25% | 1 |
| `bpy.types.Light.name` | 1 | 0.25% | 0 |
| `mathutils.Vector.length.normalized` | 1 | 0.25% | 1 |
| `mathutils.Vector.x.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.x.normalized` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `mathutils.Vector.length.length.to_track_quat` | 1 | 0.25% | 1 |
| `bpy.data.worlds.remove` | 1 | 0.25% | 0 |
| `bpy.types.World.users` | 1 | 0.25% | 0 |
| `bpy.types.Modifier.length` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.rotation_euler` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.rotation_euler.x` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.to_track_quat` | 1 | 0.25% | 1 |
| `bpy.types.Object.length` | 1 | 0.25% | 1 |
| `bpy.types.Object.segments` | 1 | 0.25% | 1 |
| `bpy.types.Object.width` | 1 | 0.25% | 1 |
| `bpy.context.scene.cross` | 1 | 0.25% | 1 |
| `bpy.context.scene.length` | 1 | 0.25% | 1 |
| `bpy.context.scene.to_track_quat` | 1 | 0.25% | 1 |
| `bpy.types.Material.name` | 1 | 0.25% | 0 |
| `bpy.types.IDData.splines.bezier_points` | 1 | 0.25% | 1 |
| `bpy.types.MeshPolygon.handle_left_type` | 1 | 0.25% | 1 |
| `bpy.types.MeshPolygon.handle_right_type` | 1 | 0.25% | 1 |
| `bpy.types.IDData.space_line` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.handle_left_type` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.handle_right_type` | 1 | 0.25% | 1 |
| `bpy.types.IDData.sensor_fit` | 1 | 0.25% | 0 |
| `bpy.types.ShaderNode.vertices` | 1 | 0.25% | 1 |
| `bpy.types.IDData.dof.aperture_blades` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.index` | 1 | 0.25% | 1 |
| `bpy.types.IDData.sensor_width` | 1 | 0.25% | 0 |
| `bpy.types.IDData.edges` | 1 | 0.25% | 0 |
| `bpy.types.MeshEdge` | 1 | 0.25% | 0 |
| `bpy.types.MeshEdge.vertices` | 1 | 0.25% | 0 |
| `bpy.types.MeshVertex.co.copy` | 1 | 0.25% | 0 |
| `bpy.types.MeshVertex.co.length` | 1 | 0.25% | 0 |
| `bpy.types.MeshVertex.co.to_track_quat` | 1 | 0.25% | 0 |
| `bpy.types.Object.scale.z` | 1 | 0.25% | 0 |
| `bpy.types.ShaderNode.normal` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.normal.z` | 1 | 0.25% | 1 |
| `bpy.types.IDData.spot_blend` | 1 | 0.25% | 0 |
| `bpy.types.IDData.spot_size` | 1 | 0.25% | 0 |
| `bpy.context.preferences` | 1 | 0.25% | 1 |
| `bpy.context.preferences.edit` | 1 | 0.25% | 1 |
| `bpy.context.preferences.edit.use_negative_frames` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.bloom_intensity` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.gtao_distance` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.gtao_factor` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.ssr_quality` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.taa_render_samples` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.use_bloom` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.use_gtao` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.use_ssr` | 1 | 0.25% | 1 |
| `bpy.context.scene.eevee.use_ssr_halfres` | 1 | 0.25% | 1 |
| `bpy.context.scene.frame_current` | 1 | 0.25% | 1 |
| `bpy.context.scene.render.filepath` | 1 | 0.25% | 0 |
| `bpy.context.scene.render.fps` | 1 | 0.25% | 1 |
| `bpy.context.scene.render.image_settings` | 1 | 0.25% | 1 |
| `bpy.context.scene.render.image_settings.file_format` | 1 | 0.25% | 1 |
| `bpy.context.window_manager` | 1 | 0.25% | 1 |
| `bpy.context.window_manager.clipboard` | 1 | 0.25% | 1 |
| `bpy.data.actions.name` | 1 | 0.25% | 1 |
| `bpy.data.actions.remove` | 1 | 0.25% | 1 |
| `bpy.data.collections.remove` | 1 | 0.25% | 0 |
| `bpy.data.curves.name` | 1 | 0.25% | 1 |
| `bpy.ops.collection` | 1 | 0.25% | 1 |
| `bpy.ops.collection.create` | 1 | 0.25% | 1 |
| `bpy.ops.curve.simple` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.primitive_circle_add` | 1 | 0.25% | 0 |
| `bpy.ops.object.constraint_add` | 1 | 0.25% | 1 |
| `bpy.ops.object.shade_flat` | 1 | 0.25% | 0 |
| `bpy.ops.outliner` | 1 | 0.25% | 1 |
| `bpy.ops.outliner.orphans_purge` | 1 | 0.25% | 1 |
| `bpy.types.IDData.bevel_mode` | 1 | 0.25% | 1 |
| `bpy.types.IDData.bevel_object` | 1 | 0.25% | 1 |
| `bpy.types.IDData.passepartout_alpha` | 1 | 0.25% | 1 |
| `bpy.types.Material.color_ramp` | 1 | 0.25% | 1 |
| `bpy.types.Material.color_ramp.elements` | 1 | 0.25% | 1 |
| `bpy.types.Material.color_ramp.elements.color` | 1 | 0.25% | 1 |
| `bpy.types.Material.color_ramp.elements.new` | 1 | 0.25% | 1 |
| `bpy.types.Material.object` | 1 | 0.25% | 1 |
| `bpy.types.Object.constraints.target` | 1 | 0.25% | 1 |
| `bpy.types.Object.hide_select` | 1 | 0.25% | 1 |
| `bpy.types.Object.hide_set` | 1 | 0.25% | 1 |
| `bpy.types.Object.shape_key_add` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.name` | 1 | 0.25% | 0 |
| `bpy.types.ShaderNode.object` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.regions` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.active` | 1 | 0.25% | 1 |
| `bpy.ops.image` | 1 | 0.25% | 1 |
| `bpy.ops.image.view_all` | 1 | 0.25% | 1 |
| `bpy.types.Object.rotate` | 1 | 0.25% | 1 |
| `bpy.context.space_data` | 1 | 0.25% | 1 |
| `bpy.context.space_data.overlay_type` | 1 | 0.25% | 1 |
| `bpy.ops.screen.area_join` | 1 | 0.25% | 1 |
| `bpy.ops.screen.area_split` | 1 | 0.25% | 1 |
| `bpy.types.SEQUENCER_HT_header` | 1 | 0.25% | 1 |
| `bpy.types.SEQUENCER_HT_header.prepend` | 1 | 0.25% | 1 |
| `bpy.types.SEQUENCER_HT_header.remove` | 1 | 0.25% | 1 |
| `mathutils.geometry.distance_point_to_plane` | 1 | 0.25% | 1 |
| `bpy.ops.wm.call_menu_pie` | 1 | 0.25% | 1 |
| `bpy.types.WorkSpaceTool` | 1 | 0.25% | 1 |
| `bpy.utils.register_tool` | 1 | 0.25% | 1 |
| `bpy.utils.unregister_tool` | 1 | 0.25% | 1 |
| `bpy.types.Object.copies` | 1 | 0.25% | 1 |
| `bpy.types.Object.my_prop` | 1 | 0.25% | 1 |
| `bpy.context.scene.object_bases` | 1 | 0.25% | 1 |
| `bpy.types.Object.modifier_active_index` | 1 | 0.25% | 1 |
| `bpy.utils.register_module` | 1 | 0.25% | 1 |
| `bpy.context.scene.node_tree.links` | 1 | 0.25% | 1 |
| `bpy.context.scene.node_tree.links.new` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.base_path` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.file_slots` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.file_slots.new` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.file_slots.remove` | 1 | 0.25% | 1 |
| `bpy.types.Object.path_resolve` | 1 | 0.25% | 1 |
| `bpy.types.VIEW3D_MT_curve_add` | 1 | 0.25% | 1 |
| `bpy.types.VIEW3D_MT_curve_add.append` | 1 | 0.25% | 1 |
| `bpy.types.VIEW3D_MT_curve_add.remove` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_complete` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_complete.append` | 1 | 0.25% | 1 |
| `bpy.ops.development` | 1 | 0.25% | 1 |
| `bpy.ops.development.fooOp` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.layer_name` | 1 | 0.25% | 1 |
| `bpy.app.driver_namespace` | 1 | 0.25% | 1 |
| `bpy.app.handlers.frame_change_post` | 1 | 0.25% | 1 |
| `bpy.app.handlers.frame_change_post.append` | 1 | 0.25% | 1 |
| `bpy.app.handlers.frame_change_post.clear` | 1 | 0.25% | 1 |
| `bpy.data.texts` | 1 | 0.25% | 1 |
| `bpy.data.texts.get` | 1 | 0.25% | 1 |
| `bpy.ops.object.join_shapes` | 1 | 0.25% | 1 |
| `bpy.ops.object.shape_key_add` | 1 | 0.25% | 1 |
| `bpy.ops.object.shape_key_remove` | 1 | 0.25% | 1 |
| `bpy.props.*` | 1 | 0.25% | 1 |
| `bpy.ops.object.simple_operator` | 1 | 0.25% | 1 |
| `bpy.app.handlers.load_post.remove` | 1 | 0.25% | 1 |
| `bpy.app.handlers.scene_update_pre` | 1 | 0.25% | 1 |
| `bpy.app.handlers.scene_update_pre.append` | 1 | 0.25% | 1 |
| `bpy.app.handlers.scene_update_pre.remove` | 1 | 0.25% | 1 |
| `bpy.ops.wm.revert_mainfile` | 1 | 0.25% | 1 |
| `mathutils.geometry.normal` | 1 | 0.25% | 1 |
| `bpy.data.armatures` | 1 | 0.25% | 1 |
| `bpy.data.armatures.get` | 1 | 0.25% | 1 |
| `bpy.types.Scene.arma` | 1 | 0.25% | 1 |
| `bpy.types.Scene.arma_coll` | 1 | 0.25% | 1 |
| `bpy.types.Scene.arma_name` | 1 | 0.25% | 1 |
| `bpy.types.Scene.bone` | 1 | 0.25% | 1 |
| `bpy.types.Scene.bone_name` | 1 | 0.25% | 1 |
| `bpy.types.NODE_MT_add` | 1 | 0.25% | 1 |
| `bpy.types.NODE_MT_add.append` | 1 | 0.25% | 1 |
| `bpy.types.NODE_MT_add.remove` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna.properties` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna.properties.enum_items` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna.properties.enum_items.description` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna.properties.enum_items.identifier` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNodeMath.bl_rna.properties.enum_items.name` | 1 | 0.25% | 1 |
| `bpy.ops.test` | 1 | 0.25% | 1 |
| `bpy.ops.test.open_filebrowser` | 1 | 0.25% | 1 |
| `bpy.types.OperatorFileListElement` | 1 | 0.25% | 1 |
| `bpy.path` | 1 | 0.25% | 1 |
| `bpy.path.display_name` | 1 | 0.25% | 1 |
| `bpy.types.Menu.draw_preset` | 1 | 0.25% | 1 |
| `bpy.types.OBJECT_PT_display` | 1 | 0.25% | 1 |
| `bpy.types.OBJECT_PT_display.prepend` | 1 | 0.25% | 1 |
| `bpy.types.OBJECT_PT_display.remove` | 1 | 0.25% | 1 |
| `bpy.utils.execfile` | 1 | 0.25% | 1 |
| `bpy.types.Object.dimensions.x` | 1 | 0.25% | 0 |
| `bpy.ops.object.material_slot_add` | 1 | 0.25% | 1 |
| `bpy.types.Object.color` | 1 | 0.25% | 1 |
| `bpy.context.scene.user_of_id` | 1 | 0.25% | 1 |
| `bpy.types.IDData.loops.vertex_index` | 1 | 0.25% | 1 |
| `bpy.types.MeshPolygon.loop_start` | 1 | 0.25% | 1 |
| `bpy.types.MeshPolygon.loop_total` | 1 | 0.25% | 1 |
| `bpy.types.IDData.loops.foreach_get` | 1 | 0.25% | 1 |
| `bpy.types.IDData.loops.foreach_set` | 1 | 0.25% | 1 |
| `bpy.types.IDData.polygons.foreach_get` | 1 | 0.25% | 1 |
| `bmesh.ops.duplicate` | 1 | 0.25% | 1 |
| `bpy.types.Object.material_slots.material.diffuse_color` | 1 | 0.25% | 1 |
| `bpy.types.Object.material_slots.material.show_transparent_back` | 1 | 0.25% | 1 |
| `bpy.types.Object.material_slots.material.use_backface_culling` | 1 | 0.25% | 1 |
| `bpy.types.Object.show_name` | 1 | 0.25% | 1 |
| `bpy.types.LayerObjects` | 1 | 0.25% | 1 |
| `bpy.ops.import_scene` | 1 | 0.25% | 1 |
| `bpy.ops.import_scene.obj` | 1 | 0.25% | 1 |
| `bpy.types.Object.active_material.node_tree.nodes.get` | 1 | 0.25% | 1 |
| `bpy.context.scene.customLists.clear` | 1 | 0.25% | 1 |
| `bpy.context.scene.customLists.name` | 1 | 0.25% | 1 |
| `bpy.context.scene.customLists.subLists.customString` | 1 | 0.25% | 1 |
| `bpy.context.scene.subLists` | 1 | 0.25% | 1 |
| `bpy.context.scene.subLists.clear` | 1 | 0.25% | 1 |
| `bpy.types.Scene.subLists` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.tris_convert_to_quads` | 1 | 0.25% | 1 |
| `bpy.context.area.tag_redraw` | 1 | 0.25% | 1 |
| `bpy.context.region` | 1 | 0.25% | 1 |
| `bpy.context.region.height` | 1 | 0.25% | 1 |
| `bpy.context.region.width` | 1 | 0.25% | 1 |
| `bpy.context.tool_settings` | 1 | 0.25% | 1 |
| `bpy.context.tool_settings.mesh_select_mode` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.select_nth` | 1 | 0.25% | 1 |
| `bmesh.types.BMVert.select` | 1 | 0.25% | 1 |
| `bpy.data.node_groups.nodes` | 1 | 0.25% | 1 |
| `bpy.data.node_groups.nodes.font` | 1 | 0.25% | 1 |
| `bpy.data.node_groups.nodes.font.name` | 1 | 0.25% | 1 |
| `bpy.context.workspace` | 1 | 0.25% | 1 |
| `bpy.context.workspace.tools` | 1 | 0.25% | 1 |
| `bpy.data.grease_pencils` | 1 | 0.25% | 1 |
| `bpy.data.grease_pencils.layers` | 1 | 0.25% | 1 |
| `bpy.data.grease_pencils.layers.remove` | 1 | 0.25% | 1 |
| `bpy.ops.wm.tool_set_by_id` | 1 | 0.25% | 1 |
| `bpy.ops.wm.modal_timer_operator` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.delete` | 1 | 0.25% | 1 |
| `bpy.types.MeshPolygon.normal.y` | 1 | 0.25% | 1 |
| `bpy.data.fonts` | 1 | 0.25% | 1 |
| `bpy.data.fonts.load` | 1 | 0.25% | 1 |
| `bpy.types.Object.bound_box` | 1 | 0.25% | 1 |
| `bpy.types.SpaceView3D.my_handler` | 1 | 0.25% | 1 |
| `mathutils.Euler.x` | 1 | 0.25% | 0 |
| `mathutils.Euler.y` | 1 | 0.25% | 0 |
| `bpy.context.scene.layers` | 1 | 0.25% | 1 |
| `bpy.types.Scene.my_prop` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.draw_channels` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.image` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.image.pixels` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.image_user` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.image_user.frame_offset` | 1 | 0.25% | 1 |
| `bpy.context.screen.areas.spaces.type` | 1 | 0.25% | 1 |
| `bpy.data.images` | 1 | 0.25% | 0 |
| `bpy.data.images.load` | 1 | 0.25% | 0 |
| `bpy.data.images.new` | 1 | 0.25% | 0 |
| `bpy.data.images.remove` | 1 | 0.25% | 0 |
| `bpy.types.Image` | 1 | 0.25% | 0 |
| `bpy.types.Image.pixels` | 1 | 0.25% | 0 |
| `bpy.types.Image.size` | 1 | 0.25% | 0 |
| `bpy.types.Image.user_clear` | 1 | 0.25% | 1 |
| `bpy.app.handlers.frame_change_pre` | 1 | 0.25% | 1 |
| `bpy.app.handlers.frame_change_pre.append` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.primitive_ico_sphere_add(size=...)` | 1 | 0.25% | 1 |
| `bpy.data.actions.new` | 1 | 0.25% | 1 |
| `bpy.types.IDData.animation_data` | 1 | 0.25% | 1 |
| `bpy.types.IDData.animation_data.action` | 1 | 0.25% | 1 |
| `bpy.types.IDData.animation_data_create` | 1 | 0.25% | 1 |
| `bpy.types.MeshVertex.index` | 1 | 0.25% | 0 |
| `bpy.context.scene.objects.link` | 1 | 0.25% | 1 |
| `bpy.types.Scene.prop_a` | 1 | 0.25% | 1 |
| `bpy.types.Scene.prop_b` | 1 | 0.25% | 1 |
| `bpy.types.Scene.prop_c` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.groups.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.index.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group.group` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.data.vertices.select` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.vertex_groups` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.vertex_groups.add` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.vertex_groups.index` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.vertex_groups.weight` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.matrix_world` | 1 | 0.25% | 1 |
| `bpy.context.edit_object.matrix_world.length` | 1 | 0.25% | 1 |
| `bpy.types.Object.closest_point_on_mesh` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.loopcut_slide` | 1 | 0.25% | 1 |
| `bpy.context.scene.objects.active.location` | 1 | 0.25% | 1 |
| `bpy.context.scene.objects.active.name` | 1 | 0.25% | 1 |
| `bpy.context.scene.objects.active.rotation_euler` | 1 | 0.25% | 1 |
| `bpy.ops.wm.call_menu` | 1 | 0.25% | 1 |
| `bpy.data.groups` | 1 | 0.25% | 1 |
| `bpy.data.groups.new` | 1 | 0.25% | 1 |
| `bpy.data.scenes.objects` | 1 | 0.25% | 1 |
| `bpy.data.scenes.objects.unlink` | 1 | 0.25% | 1 |
| `bpy.types.Object.user_clear` | 1 | 0.25% | 1 |
| `bpy.types.Object.hide` | 1 | 0.25% | 1 |
| `bpy.ops.node` | 1 | 0.25% | 1 |
| `bpy.ops.node.add_node` | 1 | 0.25% | 1 |
| `bpy.ops.node.group_edit` | 1 | 0.25% | 1 |
| `bpy.ops.node.tree_socket_add` | 1 | 0.25% | 1 |
| `bpy.types.Object.active_material.node_tree.nodes.new` | 1 | 0.25% | 1 |
| `bpy.types.ShaderNode.node_tree` | 1 | 0.25% | 1 |
| `bpy.types.Scene.bl_rna` | 1 | 0.25% | 1 |
| `bpy.types.Scene.bl_rna.properties` | 1 | 0.25% | 1 |
| `bpy.types.Scene.bl_rna.properties.fixed_type` | 1 | 0.25% | 1 |
| `bpy.types.Scene.my_collection_prop` | 1 | 0.25% | 1 |
| `bpy.types.bpy_prop_collection` | 1 | 0.25% | 1 |
| `bpy.ops.ptcache` | 1 | 0.25% | 1 |
| `bpy.ops.ptcache.bake` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.canvas_settings` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.canvas_settings.canvas_surfaces` | 1 | 0.25% | 1 |
| `bpy.types.Modifier.canvas_settings.canvas_surfaces.point_cache` | 1 | 0.25% | 1 |
| `bmesh.types.BMesh.clear` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.get` | 1 | 0.25% | 1 |
| `bpy.types.RENDER_PT_render` | 1 | 0.25% | 1 |
| `bpy.types.RENDER_PT_render.append` | 1 | 0.25% | 1 |
| `bpy.types.RENDER_PT_render.remove` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_cancel` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_cancel.append` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_cancel.remove` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_post` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_post.append` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_post.remove` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_pre` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_pre.append` | 1 | 0.25% | 1 |
| `bpy.app.handlers.render_pre.remove` | 1 | 0.25% | 1 |
| `bpy.ops.render.multi` | 1 | 0.25% | 1 |
| `bpy.data.filepath` | 1 | 0.25% | 1 |
| `bpy.ops.object.lamp_add` | 1 | 0.25% | 1 |
| `bpy.context.area.type` | 1 | 0.25% | 1 |
| `bpy.context.area.ui_type` | 1 | 0.25% | 1 |
| `bpy.ops.transform.translate` | 1 | 0.25% | 1 |
| `bpy.ops.uv.select_all` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_world.copy` | 1 | 0.25% | 1 |
| `bpy.types.Object.matrix_world.invert` | 1 | 0.25% | 1 |
| `bpy.types.Object.rotation_euler.rotate` | 1 | 0.25% | 1 |
| `bpy.ops.view3d` | 1 | 0.25% | 1 |
| `bpy.ops.view3d.select` | 1 | 0.25% | 1 |
| `bpy.ops.object.add` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.constraints` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.constraints.new` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.constraints.remove` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.constraints.update` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.types.Object.pose.bones.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.hide` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.select_linked` | 1 | 0.25% | 1 |
| `bpy.ops.mesh.select_mode` | 1 | 0.25% | 1 |
| `bpy.ops.uv.follow_active_quads` | 1 | 0.25% | 1 |
| `bpy.ops.uv.unwrap` | 1 | 0.25% | 1 |
| `bpy.ops.curve.make_segment` | 1 | 0.25% | 1 |
| `bpy.types.IDData.splines.points` | 1 | 0.25% | 1 |
| `bpy.types.IDData.splines.points.co` | 1 | 0.25% | 1 |
| `bpy.types.IDData.splines.points.select` | 1 | 0.25% | 1 |

## Unresolved static paths

These `STATIC_UNRESOLVED` diagnostics still reject preflight, but are not counted as confirmed unsupported symbols or new API backlog demands.

| Diagnostic path | Scripts | % |
|---|---:|---:|
| `bpy.types.Material.<dynamic>` | 10 | 2.50% |
| `<API inference did not converge>` | 4 | 1.00% |
| `bpy.types.<dynamic>` | 1 | 0.25% |
| `bpy.data.scenes.<dynamic>` | 1 | 0.25% |

## Backlog comparison

These checker-reported unsupported paths newly reach 2% compared with the historical synthetic baseline, recomputed using the same per-script counting method. This measures a change of corpus, not a compatibility regression. Mapping is to named entries in `docs/compatibility.md`; broad statements that all Blender RNA is unsupported do not count as a specific backlog entry. Static inference may report paths that are not real Blender members; inspect the recorded diagnostics before scheduling implementation.

| Newly ≥2% unsupported path | Previous % | New % | Backlog coverage |
|---|---:|---:|---|
| `bpy.context.scene.render.engine` | 0.00% | 58.50% | **Not listed** |
| `bpy.ops.wm` | 0.00% | 56.25% | **Not listed** |
| `bpy.ops.wm.read_factory_settings` | 0.00% | 55.00% | **Not listed** |
| `bpy.types.World.node_tree` | 0.00% | 54.50% | World: node editing and constant Background nodes |
| `bpy.types.World.node_tree.nodes` | 0.00% | 54.50% | World: node editing and constant Background nodes |
| `bpy.types.World.use_nodes=True` | 0.00% | 54.25% | World: node editing and constant Background nodes |
| `bpy.data.curves` | 0.00% | 33.25% | Data API: curves and text objects |
| `bpy.data.curves.new` | 0.00% | 33.25% | Data API: curves and text objects |
| `bpy.context.scene.cycles` | 0.00% | 31.00% | Deliberate non-goal: Cycles-grade rendering |
| `bpy.context.scene.cycles.samples` | 0.00% | 30.25% | Deliberate non-goal: Cycles-grade rendering |
| `bpy.types.Light.angle` | 0.00% | 18.50% | **Not listed** |
| `bpy.context.scene.unit_settings` | 0.00% | 18.50% | **Not listed** |
| `bpy.context.scene.unit_settings.system` | 0.00% | 18.50% | **Not listed** |
| `bmesh.ops.bevel` | 0.00% | 15.25% | Missing operations: editable bmesh operators |
| `bpy.context.scene.view_settings` | 0.00% | 13.50% | **Not listed** |
| `bpy.context.scene.view_settings.view_transform` | 0.00% | 13.00% | **Not listed** |
| `bpy.types.Camera.dof` | 0.00% | 11.75% | **Not listed** |
| `bpy.types.Camera.dof.use_dof` | 0.00% | 11.75% | **Not listed** |
| `bpy.types.Camera.dof.aperture_fstop` | 0.00% | 11.50% | **Not listed** |
| `bpy.types.Material.blend_method` | 0.00% | 11.00% | Materials: transmission and material settings |
| `bpy.types.Mesh.validate` | 0.00% | 10.00% | **Not listed** |
| `bpy.ops.object.text_add` | 0.00% | 10.00% | Data API: curves and text objects |
| `bpy.types.IDData.body` | 0.00% | 10.00% | Data API: curves/text (checker generic datablock alias) |
| `bpy.types.Camera.dof.focus_distance` | 0.00% | 9.50% | **Not listed** |
| `bpy.types.IDData.extrude` | 0.00% | 9.50% | Data API: curves/text (checker generic datablock alias) |
| `bpy.types.Modifier.split_angle` | 0.00% | 9.00% | **Not listed** |
| `bpy.types.Object.modifiers.new(type='EDGE_SPLIT')` | 0.00% | 9.00% | **Not listed** |
| `bpy.types.IDData.angle` | 0.00% | 9.00% | **Not listed** |
| `bpy.types.ShaderNode.color_ramp` | 0.00% | 7.75% | Deliberate non-goal: arbitrary shader graphs |
| `bpy.types.ShaderNode.color_ramp.elements` | 0.00% | 7.75% | Deliberate non-goal: arbitrary shader graphs |
| `bpy.types.ShaderNode.color_ramp.elements.color` | 0.00% | 7.75% | Deliberate non-goal: arbitrary shader graphs |
| `bpy.types.IDData.align_x` | 0.00% | 7.00% | Data API: curves/text (checker generic datablock alias) |
| `bpy.utils.register_class` | 0.00% | 6.25% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bpy.utils` | 0.00% | 6.25% | Deliberate non-goal: addon registration namespace used by these samples |
| `bpy.types.Object.matrix_world` | 0.00% | 6.00% | Data API: matrix_world and constraints |
| `bmesh.ops.remove_doubles` | 0.00% | 5.50% | Missing operations: editable bmesh operators |
| `bmesh.ops.create_icosphere` | 0.00% | 5.25% | **Not listed** |
| `bpy.ops.mesh.primitive_ico_sphere_add` | 0.00% | 5.25% | Missing operations: ico-sphere primitive |
| `bpy.types.ShaderNode.location` | 0.00% | 5.00% | **Not listed** |
| `bpy.ops.mesh.primitive_ico_sphere_add(radius=...)` | 0.00% | 5.00% | Missing operations: ico-sphere primitive |
| `bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=...)` | 0.00% | 5.00% | Missing operations: ico-sphere primitive |
| `bpy.ops.object.shade_auto_smooth` | 0.00% | 5.00% | **Not listed** |
| `bpy.types.ShaderNode.color_ramp.elements.position` | 0.00% | 5.00% | Deliberate non-goal: arbitrary shader graphs |
| `bpy.utils.unregister_class` | 0.00% | 4.75% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bmesh.ops.spin` | 0.00% | 4.25% | **Not listed** |
| `bmesh.types.BMVert.link_faces` | 0.00% | 4.00% | BMesh data: full Blender element/lifecycle API parity (broad existing entry) |
| `bpy.types.Operator` | 0.00% | 4.00% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bpy.types.Object.rotation_quaternion` | 0.00% | 3.75% | **Not listed** |
| `bpy.types.World.node_tree.links` | 0.00% | 3.50% | World: node editing and constant Background nodes |
| `bpy.types.World.node_tree.links.new` | 0.00% | 3.50% | World: node editing and constant Background nodes |
| `bpy.types.World.node_tree.nodes.new` | 0.00% | 3.50% | World: node editing and constant Background nodes |
| `bpy.context.scene.cycles.use_denoising` | 0.00% | 3.50% | Deliberate non-goal: Cycles-grade rendering |
| `bpy.types.ShaderNode.operation` | 0.00% | 3.50% | Deliberate non-goal: arbitrary shader graphs |
| `bpy.context.scene.unit_settings.length_unit` | 0.00% | 3.25% | **Not listed** |
| `bpy.types.ShaderNode.sun_elevation` | 0.00% | 3.25% | Deliberate non-goal: arbitrary shader graphs (Sky/Wave texture nodes) |
| `bpy.types.ShaderNode.sun_rotation` | 0.00% | 3.25% | Deliberate non-goal: arbitrary shader graphs (Sky/Wave texture nodes) |
| `bpy.types.Material.surface_render_method` | 0.00% | 3.25% | Materials: transmission and material settings |
| `bpy.types.MeshPolygon.inputs` | 0.00% | 3.25% | **Not listed** |
| `bpy.types.MeshPolygon.inputs.default_value` | 0.00% | 3.25% | **Not listed** |
| `bpy.types.Object.constraints` | 0.00% | 3.00% | Data API: matrix_world and constraints |
| `bpy.types.ShaderNode.use_smooth` | 0.00% | 3.00% | **Not listed** |
| `bmesh.from_edit_mesh` | 0.00% | 3.00% | BMesh data: full Blender element/lifecycle API parity (broad existing entry) |
| `bmesh.types.BMEdge.calc_face_angle` | 0.00% | 2.75% | BMesh data: full Blender element/lifecycle API parity (broad existing entry) |
| `bmesh.types.BMEdge.smooth` | 0.00% | 2.75% | BMesh data: full Blender element/lifecycle API parity (broad existing entry) |
| `bpy.types.Object.matrix_parent_inverse` | 0.00% | 2.75% | **Not listed** |
| `bpy.types.Object.constraints.new` | 0.00% | 2.75% | Data API: matrix_world and constraints |
| `bpy.ops.object.mode_set` | 0.00% | 2.75% | **Not listed** |
| `bpy.types.World.node_tree.nodes.get` | 0.00% | 2.50% | World: node editing and constant Background nodes |
| `bpy.types.ShaderNode.sky_type` | 0.00% | 2.50% | Deliberate non-goal: arbitrary shader graphs (Sky/Wave texture nodes) |
| `bpy.props` | 0.00% | 2.50% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bpy.context.scene.render.film_transparent` | 0.00% | 2.25% | **Not listed** |
| `bpy.types.Camera.dof.focus_object` | 0.00% | 2.25% | **Not listed** |
| `bpy.types.Modifier.solver='EXACT'` | 0.00% | 2.25% | BOOLEAN limits: solvers and collection operands |
| `bpy.types.Modifier.use_edge_sharp` | 0.00% | 2.25% | **Not listed** |
| `bpy.types.IDData.align_y` | 0.00% | 2.25% | Data API: curves/text (checker generic datablock alias) |
| `bpy.context.scene.cycles.transmission_bounces` | 0.00% | 2.25% | Deliberate non-goal: Cycles-grade rendering |
| `bpy.ops.object.editmode_toggle` | 0.00% | 2.25% | **Not listed** |
| `bpy.types.Object.mode` | 0.00% | 2.25% | **Not listed** |
| `bpy.props.StringProperty` | 0.00% | 2.25% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bpy.types.ShaderNode.inputs.get` | 0.00% | 2.00% | **Not listed** |
| `bpy.types.ShaderNode.wave_type` | 0.00% | 2.00% | Deliberate non-goal: arbitrary shader graphs (Sky/Wave texture nodes) |
| `bpy.context.scene.frame_end` | 0.00% | 2.00% | Deliberate non-goal: animation timeline |
| `bpy.ops.object.camera_add(align='VIEW')` | 0.00% | 2.00% | Deliberate non-goal: interactive viewport alignment |
| `bpy.ops.render` | 0.00% | 2.00% | Missing operations: bpy I/O and rendering operators |
| `bpy.ops.render.render` | 0.00% | 2.00% | Missing operations: bpy I/O and rendering operators |
| `bpy.ops.transform` | 0.00% | 2.00% | **Not listed** |
| `bpy.types.Panel` | 0.00% | 2.00% | Deliberate non-goals: GUI/interactive viewport and addon/plugin loading |
| `bpy.types.Scene` | 0.00% | 2.00% | **Not listed** |

The full symbol tables include supported paths; supported symbols do not require backlog entries. The mapping rules are preserved in `corpus/tools/backlog-map.json`.
