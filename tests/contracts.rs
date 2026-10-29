// SPDX-License-Identifier: MIT
// Manifest declarations migrated from the existing golden fixtures.
use std::{
    collections::BTreeSet,
    sync::{Mutex, OnceLock},
};
fn golden(path: &str) {
    static PASSED: OnceLock<Mutex<BTreeSet<String>>> = OnceLock::new();
    let mut passed = PASSED
        .get_or_init(|| Mutex::new(BTreeSet::new()))
        .lock()
        .unwrap();
    if passed.contains(path) {
        return;
    }
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    let output = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
        .arg("run")
        .arg(root.join(path))
        .arg("--scene")
        .arg(temp.join("scene.hb"))
        .current_dir(&temp)
        .output()
        .unwrap();
    let _ = std::fs::remove_dir_all(&temp);
    assert!(
        output.status.success(),
        "{}: {} {}",
        path,
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    passed.insert(path.into());
}
#[doc = "hb:test=compat/golden/collections.py"]
#[doc = "hb:symbol=bpy.context.collection.objects"]
#[doc = "Linked collection objects, insertion order"]
#[doc = "hb:symbol=bpy.context.collection.objects.get"]
#[doc = "get(name, default=None)"]
#[doc = "hb:symbol=bpy.context.scene.objects.get"]
#[doc = "get(name, default=None)"]
#[doc = "hb:symbol=bpy.context.view_layer.objects"]
#[doc = "View-layer objects, insertion order"]
#[doc = "hb:symbol=bpy.context.view_layer.objects.get"]
#[doc = "get(name, default=None)"]
#[test]
fn golden_000() {
    golden("compat/golden/collections.py");
}

#[doc = "hb:test=compat/golden/m0.py"]
#[doc = "hb:symbol=bpy.context.active_object"]
#[doc = "Active object or None"]
#[doc = "hb:symbol=bpy.context.collection.objects.link"]
#[doc = "Link an existing object to the active collection"]
#[doc = "hb:symbol=bpy.context.object"]
#[doc = "Active object or None"]
#[doc = "hb:symbol=bpy.context.scene.objects"]
#[doc = "Linked scene objects"]
#[doc = "hb:symbol=bpy.context.selected_objects"]
#[doc = "List of selected, linked objects"]
#[doc = "hb:symbol=bpy.context.view_layer.objects.active"]
#[doc = "Read/write active linked object"]
#[doc = "hb:symbol=bpy.data.objects"]
#[doc = "Object database: iteration, length, name/index lookup, get"]
#[doc = "hb:symbol=bpy.data.objects.get"]
#[doc = "get(name, default=None)"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_cube_add"]
#[doc = "Keyword-only cube size/location/rotation/scale; WORLD or CURSOR, object or single-mesh EDIT construction; explicit zero size uses unit cube; return to OBJECT before script completion"]
#[doc = "hb:symbol=bpy.types.Object.location"]
#[doc = "XYZ float32 transform; assignment, indexed read/write, iteration"]
#[doc = "hb:symbol=bpy.types.Object.name"]
#[doc = "Read/write unique name"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler"]
#[doc = "Euler radians in Object.rotation_mode order; assignment, indexed read/write, iteration"]
#[doc = "hb:symbol=bpy.types.Object.scale"]
#[doc = "XYZ float32 scale; assignment, indexed read/write, iteration"]
#[doc = "hb:symbol=bpy.types.Object.select_get"]
#[doc = "select_get() returns bool"]
#[doc = "hb:symbol=bpy.types.Object.select_set"]
#[doc = "select_set(state)"]
#[test]
fn golden_001() {
    golden("compat/golden/m0.py");
}

#[doc = "hb:test=compat/golden/m1_assembly.py"]
#[doc = "hb:symbol=bpy.context.collection.objects.unlink"]
#[doc = "Unlink from active collection"]
#[doc = "hb:symbol=bpy.context.scene.camera"]
#[doc = "Active camera object or None"]
#[doc = "hb:symbol=bpy.context.scene.collection"]
#[doc = "Scene master collection"]
#[doc = "hb:symbol=bpy.context.view_layer.update"]
#[doc = "Synchronize evaluated scene state"]
#[doc = "hb:symbol=bpy.data.cameras"]
#[doc = "Camera data blocks"]
#[doc = "hb:symbol=bpy.data.cameras.new"]
#[doc = "new(name)"]
#[doc = "hb:symbol=bpy.data.cameras.remove"]
#[doc = "remove(camera, do_unlink=True)"]
#[doc = "hb:symbol=bpy.data.collections"]
#[doc = "Collections, excluding the scene master collection"]
#[doc = "hb:symbol=bpy.data.collections.new"]
#[doc = "new(name)"]
#[doc = "hb:symbol=bpy.data.collections.remove"]
#[doc = "remove(collection, do_unlink=True)"]
#[doc = "hb:symbol=bpy.data.lights"]
#[doc = "Light data blocks"]
#[doc = "hb:symbol=bpy.data.lights.new"]
#[doc = "new(name, type): POINT, SUN, SPOT, AREA"]
#[doc = "hb:symbol=bpy.data.lights.remove"]
#[doc = "remove(light, do_unlink=True)"]
#[doc = "hb:symbol=bpy.data.materials"]
#[doc = "Material data blocks"]
#[doc = "hb:symbol=bpy.data.materials.new"]
#[doc = "new(name)"]
#[doc = "hb:symbol=bpy.data.materials.remove"]
#[doc = "remove(material, do_unlink=True)"]
#[doc = "hb:symbol=bpy.data.meshes"]
#[doc = "Mesh data blocks: iteration, lookup and creation"]
#[doc = "hb:symbol=bpy.data.meshes.new"]
#[doc = "new(name) creates an empty mesh"]
#[doc = "hb:symbol=bpy.data.meshes.remove"]
#[doc = "remove(mesh, do_unlink=True)"]
#[doc = "hb:symbol=bpy.data.objects.new"]
#[doc = "new(name, object_data): mesh, camera, light or None"]
#[doc = "hb:symbol=bpy.data.objects.remove"]
#[doc = "remove(object, do_unlink=True)"]
#[doc = "hb:symbol=bpy.ops.object.delete"]
#[doc = "Delete selected objects in the scene; use_global supported"]
#[doc = "hb:symbol=bpy.ops.object.select_all"]
#[doc = "action: SELECT, DESELECT, INVERT or TOGGLE"]
#[doc = "hb:symbol=bpy.ops.object.shade_flat"]
#[doc = "Set mesh polygons to flat shading"]
#[doc = "hb:symbol=bpy.ops.object.shade_smooth"]
#[doc = "Set mesh polygons to smooth shading"]
#[doc = "hb:symbol=bpy.types.Camera.clip_end"]
#[doc = "Far clipping plane in meters"]
#[doc = "hb:symbol=bpy.types.Camera.clip_start"]
#[doc = "Near clipping plane in meters"]
#[doc = "hb:symbol=bpy.types.Camera.lens"]
#[doc = "Focal length in millimeters"]
#[doc = "hb:symbol=bpy.types.Camera.name"]
#[doc = "Unique camera data name"]
#[doc = "hb:symbol=bpy.types.Camera.ortho_scale"]
#[doc = "Orthographic view scale"]
#[doc = "hb:symbol=bpy.types.Camera.sensor_fit"]
#[doc = "AUTO, HORIZONTAL or VERTICAL"]
#[doc = "hb:symbol=bpy.types.Camera.sensor_height"]
#[doc = "Sensor height in millimeters"]
#[doc = "hb:symbol=bpy.types.Camera.sensor_width"]
#[doc = "Sensor width in millimeters"]
#[doc = "hb:symbol=bpy.types.Camera.shift_x"]
#[doc = "Horizontal lens shift"]
#[doc = "hb:symbol=bpy.types.Camera.shift_y"]
#[doc = "Vertical lens shift"]
#[doc = "hb:symbol=bpy.types.Camera.type"]
#[doc = "PERSP or ORTHO; panoramic cameras fail explicitly"]
#[doc = "hb:symbol=bpy.types.Collection.children"]
#[doc = "Child collections"]
#[doc = "hb:symbol=bpy.types.Collection.children.link"]
#[doc = "Link child collection"]
#[doc = "hb:symbol=bpy.types.Collection.children.unlink"]
#[doc = "Unlink child collection"]
#[doc = "hb:symbol=bpy.types.Collection.name"]
#[doc = "Unique collection name"]
#[doc = "hb:symbol=bpy.types.Collection.objects"]
#[doc = "Direct object membership"]
#[doc = "hb:symbol=bpy.types.Collection.objects.link"]
#[doc = "Link object to collection"]
#[doc = "hb:symbol=bpy.types.Collection.objects.unlink"]
#[doc = "Unlink object from collection"]
#[doc = "hb:symbol=bpy.types.Light.color"]
#[doc = "Linear RGB"]
#[doc = "hb:symbol=bpy.types.Light.energy"]
#[doc = "Blender energy units"]
#[doc = "hb:symbol=bpy.types.Light.name"]
#[doc = "Unique light name"]
#[doc = "hb:symbol=bpy.types.Light.shadow_soft_size"]
#[doc = "Point/spot source radius"]
#[doc = "hb:symbol=bpy.types.Light.size"]
#[doc = "Area source size"]
#[doc = "hb:symbol=bpy.types.Light.spot_blend"]
#[doc = "Spot cone edge softness"]
#[doc = "hb:symbol=bpy.types.Light.spot_size"]
#[doc = "Spot cone angle in radians"]
#[doc = "hb:symbol=bpy.types.Light.type"]
#[doc = "POINT, SUN, SPOT, AREA"]
#[doc = "hb:symbol=bpy.types.Material.diffuse_color"]
#[doc = "Viewport RGBA, independent of node inputs"]
#[doc = "hb:symbol=bpy.types.Material.metallic"]
#[doc = "Non-node metallic factor"]
#[doc = "hb:symbol=bpy.types.Material.name"]
#[doc = "Unique material name"]
#[doc = "hb:symbol=bpy.types.Material.node_tree"]
#[doc = "None until nodes are enabled; retained when disabled"]
#[doc = "hb:symbol=bpy.types.Material.roughness"]
#[doc = "Non-node roughness factor"]
#[doc = "hb:symbol=bpy.types.Material.use_nodes"]
#[doc = "Enable or disable material node tree"]
#[doc = "hb:symbol=bpy.types.Mesh.copy"]
#[doc = "Copy mesh geometry and material references"]
#[doc = "hb:symbol=bpy.types.Mesh.edges"]
#[doc = "Mesh edges with .vertices and .index"]
#[doc = "hb:symbol=bpy.types.Mesh.from_pydata"]
#[doc = "from_pydata(vertices, edges, faces, shade_flat=True)"]
#[doc = "hb:symbol=bpy.types.Mesh.materials"]
#[doc = "Material slots: append, clear, pop, indexed access and assignment"]
#[doc = "hb:symbol=bpy.types.Mesh.materials.append"]
#[doc = "Append a material data block"]
#[doc = "hb:symbol=bpy.types.Mesh.materials.clear"]
#[doc = "Remove all material slots"]
#[doc = "hb:symbol=bpy.types.Mesh.materials.pop"]
#[doc = "pop(index=-1)"]
#[doc = "hb:symbol=bpy.types.Mesh.name"]
#[doc = "Unique mesh name"]
#[doc = "hb:symbol=bpy.types.Mesh.polygons"]
#[doc = "Mesh polygons with .vertices, .index, .material_index, .use_smooth"]
#[doc = "hb:symbol=bpy.types.Mesh.update"]
#[doc = "update(calc_edges=False, calc_edges_loose=False)"]
#[doc = "hb:symbol=bpy.types.Mesh.users"]
#[doc = "Number of referencing objects"]
#[doc = "hb:symbol=bpy.types.Mesh.vertices"]
#[doc = "Mesh vertices; indexed/iterable with .co and .index"]
#[doc = "hb:symbol=bpy.types.MeshEdge.vertices"]
#[doc = "Two vertex indices"]
#[doc = "hb:symbol=bpy.types.MeshPolygon.material_index"]
#[doc = "Material slot index"]
#[doc = "hb:symbol=bpy.types.MeshPolygon.use_smooth"]
#[doc = "Smooth or flat shading"]
#[doc = "hb:symbol=bpy.types.MeshPolygon.vertices"]
#[doc = "Face vertex indices"]
#[doc = "hb:symbol=bpy.types.MeshVertex.co"]
#[doc = "XYZ coordinate; assignment and indexed access"]
#[doc = "hb:symbol=bpy.types.MeshVertex.index"]
#[doc = "Zero-based vertex index"]
#[doc = "hb:symbol=bpy.types.Object.children"]
#[doc = "Immediate child objects"]
#[doc = "hb:symbol=bpy.types.Object.copy"]
#[doc = "Copy object, sharing its data and retaining transforms"]
#[doc = "hb:symbol=bpy.types.Object.data"]
#[doc = "Shared mesh, camera or light data block; None for an empty"]
#[doc = "hb:symbol=bpy.types.Object.hide_render"]
#[doc = "Exclude object from renders"]
#[doc = "hb:symbol=bpy.types.Object.location.x"]
#[doc = "Component access on transform views (see type deviation)"]
#[doc = "hb:symbol=bpy.types.Object.parent"]
#[doc = "Object parent; local transforms retained"]
#[doc = "hb:symbol=bpy.types.Object.type"]
#[doc = "MESH, CAMERA, LIGHT or EMPTY according to data block"]
#[doc = "hb:symbol=bpy.types.Object.users_collection"]
#[doc = "Collections containing the object"]
#[test]
fn golden_002() {
    golden("compat/golden/m1_assembly.py");
}

#[doc = "hb:test=compat/golden/m1_databases.py"]
#[doc = "hb:symbol=bpy.data.cameras.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.data.collections.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.data.images.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.data.lights.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.data.materials.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.data.meshes.get"]
#[doc = "Name lookup with optional fallback"]
#[doc = "hb:symbol=bpy.types.Camera.users"]
#[doc = "Referencing objects"]
#[doc = "hb:symbol=bpy.types.Collection.users"]
#[doc = "Parent collection references"]
#[doc = "hb:symbol=bpy.types.Image.users"]
#[doc = "Referencing texture nodes"]
#[doc = "hb:symbol=bpy.types.Light.users"]
#[doc = "Referencing objects"]
#[doc = "hb:symbol=bpy.types.Material.users"]
#[doc = "Number of mesh slots referencing the material"]
#[doc = "hb:symbol=bpy.types.MeshEdge.index"]
#[doc = "Zero-based mesh edge index"]
#[doc = "hb:symbol=bpy.types.MeshPolygon.index"]
#[doc = "Zero-based polygon index"]
#[doc = "hb:symbol=bpy.types.NodeLink.from_node"]
#[doc = "Linked output node"]
#[doc = "hb:symbol=bpy.types.NodeLink.from_socket"]
#[doc = "Linked output socket"]
#[doc = "hb:symbol=bpy.types.NodeLink.to_node"]
#[doc = "Linked input node"]
#[doc = "hb:symbol=bpy.types.NodeLink.to_socket"]
#[doc = "Linked input socket"]
#[doc = "hb:symbol=bpy.types.NodeSocket.name"]
#[doc = "Socket name"]
#[doc = "hb:symbol=bpy.types.Object.users"]
#[doc = "Number of collection memberships (parent and scene-camera pointers do not increment ID users)"]
#[test]
fn golden_003() {
    golden("compat/golden/m1_databases.py");
}

#[doc = "hb:test=compat/golden/m1_material.py"]
#[doc = "hb:symbol=bpy.data.images"]
#[doc = "Image data blocks"]
#[doc = "hb:symbol=bpy.data.images.load"]
#[doc = "load(filepath, check_existing=False); PNG and JPEG"]
#[doc = "hb:symbol=bpy.data.images.new"]
#[doc = "new(name, width, height, alpha=True, float_buffer=False, stereo3d=False, is_data=False, tiled=False); non-tiled mono images"]
#[doc = "hb:symbol=bpy.data.images.remove"]
#[doc = "remove(image, do_unlink=True)"]
#[doc = "hb:symbol=bpy.types.Image.colorspace_settings.name"]
#[doc = "sRGB or Non-Color"]
#[doc = "hb:symbol=bpy.types.Image.filepath"]
#[doc = "Image source path"]
#[doc = "hb:symbol=bpy.types.Image.name"]
#[doc = "Unique image name"]
#[doc = "hb:symbol=bpy.types.Image.size"]
#[doc = "Pixel width and height"]
#[doc = "hb:symbol=bpy.types.Material.node_tree.links.new"]
#[doc = "Connect permitted UV/Mapping/Image, Image Color to Principled Base Color or Emission Color, Image Alpha to Alpha, and Principled to output; existing Normal Map chain retained"]
#[doc = "hb:symbol=bpy.types.Material.node_tree.nodes"]
#[doc = "Single Principled/output, image textures and one UV TexCoord/POINT Mapping chain; existing Normal Map retained"]
#[doc = "hb:symbol=bpy.types.Material.node_tree.nodes.clear"]
#[doc = "Remove nodes and links"]
#[doc = "hb:symbol=bpy.types.Material.node_tree.nodes.get"]
#[doc = "Node lookup by name"]
#[doc = "hb:symbol=bpy.types.Material.node_tree.nodes.new"]
#[doc = "ShaderNodeTexImage, ShaderNodeTexCoord, ShaderNodeMapping; existing ShaderNodeNormalMap retained; Principled/Output after clearing"]
#[doc = "hb:symbol=bpy.types.Mesh.uv_layers"]
#[doc = "UV layers"]
#[doc = "hb:symbol=bpy.types.Mesh.uv_layers.active"]
#[doc = "Active UV layer"]
#[doc = "hb:symbol=bpy.types.MeshUVLoop.uv"]
#[doc = "UV pair, assignment and indexed access"]
#[doc = "hb:symbol=bpy.types.MeshUVLoopLayer.data"]
#[doc = "Loop UV values"]
#[doc = "hb:symbol=bpy.types.MeshUVLoopLayer.name"]
#[doc = "UV layer name"]
#[doc = "hb:symbol=bpy.types.ShaderNode.image"]
#[doc = "Image Texture or World Environment Texture image datablock"]
#[doc = "hb:symbol=bpy.types.ShaderNode.inputs"]
#[doc = "Supported named input sockets"]
#[doc = "hb:symbol=bpy.types.ShaderNode.name"]
#[doc = "Unique node name"]
#[doc = "hb:symbol=bpy.types.ShaderNode.outputs"]
#[doc = "Supported named output sockets"]
#[test]
fn golden_004() {
    golden("compat/golden/m1_material.py");
}

#[doc = "hb:test=compat/golden/m1_render_settings.py"]
#[doc = "hb:symbol=bpy.context.scene.render"]
#[doc = "Scene render output settings"]
#[doc = "hb:symbol=bpy.context.scene.render.filepath"]
#[doc = "Render output path"]
#[doc = "hb:symbol=bpy.context.scene.render.pixel_aspect_x"]
#[doc = "Horizontal pixel aspect"]
#[doc = "hb:symbol=bpy.context.scene.render.pixel_aspect_y"]
#[doc = "Vertical pixel aspect"]
#[doc = "hb:symbol=bpy.context.scene.render.resolution_percentage"]
#[doc = "Resolution percentage"]
#[doc = "hb:symbol=bpy.context.scene.render.resolution_x"]
#[doc = "Image width"]
#[doc = "hb:symbol=bpy.context.scene.render.resolution_y"]
#[doc = "Image height"]
#[test]
fn golden_005() {
    golden("compat/golden/m1_render_settings.py");
}

#[doc = "hb:test=compat/golden/m2_array.py"]
#[doc = "hb:symbol=bpy.ops.object.modifier_apply"]
#[doc = "Apply the first supported modifier to an active single-user mesh"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.constant_offset_displace"]
#[doc = "XYZ constant displacement in meters"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.count"]
#[doc = "Fixed count, clamped to 1..10000"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.fit_type"]
#[doc = "FIXED_COUNT only"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.name"]
#[doc = "Unique modifier name"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.relative_offset_displace"]
#[doc = "XYZ relative displacement"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.show_render"]
#[doc = "Enable modifier for CPU preview"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.show_viewport"]
#[doc = "Enable modifier for viewport queries"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.type"]
#[doc = "ARRAY"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.use_constant_offset"]
#[doc = "Enable fixed local displacement"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.use_relative_offset"]
#[doc = "Enable offset relative to evaluated mesh bounding box"]
#[doc = "hb:symbol=bpy.types.Object.modifiers"]
#[doc = "Ordered non-destructive stack; ARRAY/MIRROR/SOLIDIFY/TRIANGULATE and bounded BEVEL subsets"]
#[doc = "hb:symbol=bpy.types.Object.modifiers.clear"]
#[doc = "Remove all modifiers"]
#[doc = "hb:symbol=bpy.types.Object.modifiers.new"]
#[doc = "new(name, type): ARRAY, MIRROR, SOLIDIFY, TRIANGULATE, restricted WELD or restricted BEVEL"]
#[doc = "hb:symbol=bpy.types.Object.modifiers.remove"]
#[doc = "Remove a modifier from this object"]
#[test]
fn golden_006() {
    golden("compat/golden/m2_array.py");
}

#[doc = "hb:test=compat/golden/m2_bevel.py"]
#[doc = "hb:symbol=bpy.types.BevelModifier.affect"]
#[doc = "EDGES on closed convex polyhedral meshes; EDGES/VERTICES on canonical cuboids; textured VERTICES requires one or even segments"]
#[doc = "hb:symbol=bpy.types.BevelModifier.angle_limit"]
#[doc = "Edge angle threshold in radians"]
#[doc = "hb:symbol=bpy.types.BevelModifier.harden_normals"]
#[doc = "False only"]
#[doc = "hb:symbol=bpy.types.BevelModifier.limit_method"]
#[doc = "NONE/ANGLE on closed convex polyhedral meshes; coplanar edges remain unchanged"]
#[doc = "hb:symbol=bpy.types.BevelModifier.loop_slide"]
#[doc = "True only"]
#[doc = "hb:symbol=bpy.types.BevelModifier.material"]
#[doc = "-1 inherited source face material"]
#[doc = "hb:symbol=bpy.types.BevelModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.BevelModifier.offset_type"]
#[doc = "OFFSET only"]
#[doc = "hb:symbol=bpy.types.BevelModifier.profile"]
#[doc = "0.5 circular profile only"]
#[doc = "hb:symbol=bpy.types.BevelModifier.segments"]
#[doc = "Rounded edge segments 1..8; general convex meshes use sampled fillets and corner patches, with per-face UV projection; canonical cuboids retain reference stencils and their UV restrictions"]
#[doc = "hb:symbol=bpy.types.BevelModifier.show_render"]
#[doc = "CPU preview visibility"]
#[doc = "hb:symbol=bpy.types.BevelModifier.show_viewport"]
#[doc = "Viewport visibility"]
#[doc = "hb:symbol=bpy.types.BevelModifier.type"]
#[doc = "BEVEL"]
#[doc = "hb:symbol=bpy.types.BevelModifier.use_clamp_overlap"]
#[doc = "True clamps general mesh width before face insets collapse; canonical cuboids retain half-shortest-edge clamping; False rejects overlapping width"]
#[doc = "hb:symbol=bpy.types.BevelModifier.width"]
#[doc = "Nonnegative OFFSET bevel distance; oversized widths clamp when use_clamp_overlap=True"]
#[test]
fn golden_007() {
    golden("compat/golden/m2_bevel.py");
}

#[doc = "hb:test=compat/golden/m2_bevel_uv.py"]
#[doc = "hb:symbol=bpy.types.MeshPolygon.loop_indices"]
#[doc = "Read-only range of corner indices in this polygon"]
#[test]
fn golden_008() {
    golden("compat/golden/m2_bevel_uv.py");
}

#[doc = "hb:test=compat/golden/m2_bmesh.py"]
#[doc = "hb:symbol=bmesh.new"]
#[doc = "Create a standalone editable mesh, use_operators=True/False"]
#[doc = "hb:symbol=bmesh.ops.delete"]
#[doc = "Delete selected VERTS, EDGES, FACES_ONLY geometry"]
#[doc = "hb:symbol=bmesh.types.BMEdge.verts"]
#[doc = "The two edge vertices"]
#[doc = "hb:symbol=bmesh.types.BMFace.edges"]
#[doc = "Ordered boundary edges"]
#[doc = "hb:symbol=bmesh.types.BMFace.material_index"]
#[doc = "Material slot index"]
#[doc = "hb:symbol=bmesh.types.BMFace.normal"]
#[doc = "Face normal after normal_update"]
#[doc = "hb:symbol=bmesh.types.BMFace.smooth"]
#[doc = "Smooth shading flag"]
#[doc = "hb:symbol=bmesh.types.BMFace.verts"]
#[doc = "Ordered face vertices"]
#[doc = "hb:symbol=bmesh.types.BMVert.co"]
#[doc = "Writable Vector coordinate"]
#[doc = "hb:symbol=bmesh.types.BMVert.index"]
#[doc = "Mutable index, -1 before index_update"]
#[doc = "hb:symbol=bmesh.types.BMVert.is_valid"]
#[doc = "Element validity"]
#[doc = "hb:symbol=bmesh.types.BMesh.edges"]
#[doc = "Mutable edge sequence"]
#[doc = "hb:symbol=bmesh.types.BMesh.edges.ensure_lookup_table"]
#[doc = "Enable indexed edge access"]
#[doc = "hb:symbol=bmesh.types.BMesh.edges.index_update"]
#[doc = "Update edge indices"]
#[doc = "hb:symbol=bmesh.types.BMesh.edges.new"]
#[doc = "Add an edge between distinct vertices"]
#[doc = "hb:symbol=bmesh.types.BMesh.edges.remove"]
#[doc = "Remove edge and incident faces"]
#[doc = "hb:symbol=bmesh.types.BMesh.faces"]
#[doc = "Mutable face sequence"]
#[doc = "hb:symbol=bmesh.types.BMesh.faces.ensure_lookup_table"]
#[doc = "Enable indexed face access"]
#[doc = "hb:symbol=bmesh.types.BMesh.faces.index_update"]
#[doc = "Update face indices"]
#[doc = "hb:symbol=bmesh.types.BMesh.faces.new"]
#[doc = "Add a face using distinct vertices"]
#[doc = "hb:symbol=bmesh.types.BMesh.faces.remove"]
#[doc = "Remove face, retaining edges and vertices"]
#[doc = "hb:symbol=bmesh.types.BMesh.free"]
#[doc = "Invalidate the editable mesh and its elements"]
#[doc = "hb:symbol=bmesh.types.BMesh.from_mesh"]
#[doc = "Append plain geometry; import UV, FLOAT_COLOR, shape and unchanged packed-normal data into an empty BMesh"]
#[doc = "hb:symbol=bmesh.types.BMesh.normal_update"]
#[doc = "Recalculate vertex and face normals"]
#[doc = "hb:symbol=bmesh.types.BMesh.to_mesh"]
#[doc = "Atomically publish geometry and supported editable layers; packed normals require flat faces and unchanged geometry"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts"]
#[doc = "Mutable vertex sequence"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts.ensure_lookup_table"]
#[doc = "Enable indexed vertex access"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts.index_update"]
#[doc = "Update vertex indices"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts.new"]
#[doc = "Add a vertex with a 3D coordinate"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts.remove"]
#[doc = "Remove vertex and incident geometry"]
#[test]
fn golden_009() {
    golden("compat/golden/m2_bmesh.py");
}

#[doc = "hb:test=compat/golden/m2_boolean.py"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.double_threshold"]
#[doc = "Default 1e-6 only; unused by MANIFOLD"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.material_mode"]
#[doc = "INDEX only"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.object"]
#[doc = "Mesh object operand or None; evaluated in owner local coordinates"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.operation"]
#[doc = "DIFFERENCE, UNION or INTERSECT of closed manifold meshes"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.show_render"]
#[doc = "Preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.show_viewport"]
#[doc = "Viewport and glTF evaluation flag"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.type"]
#[doc = "BOOLEAN"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.use_hole_tolerant"]
#[doc = "False only"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.use_self"]
#[doc = "False only"]
#[test]
fn golden_010() {
    golden("compat/golden/m2_boolean.py");
}

#[doc = "hb:test=compat/golden/m2_colors.py"]
#[doc = "hb:symbol=mathutils.Color"]
#[doc = "Float32 RGB sequence with Color arithmetic and scalar multiply/divide; default black"]
#[doc = "hb:symbol=mathutils.Color.b"]
#[doc = "Mutable blue channel"]
#[doc = "hb:symbol=mathutils.Color.copy"]
#[doc = "Independent mutable copy"]
#[doc = "hb:symbol=mathutils.Color.freeze"]
#[doc = "Freeze an unwrapped Color and return itself"]
#[doc = "hb:symbol=mathutils.Color.from_aces_to_scene_linear"]
#[doc = "ACES AP0 to factory scene-linear RGB"]
#[doc = "hb:symbol=mathutils.Color.from_rec709_linear_to_scene_linear"]
#[doc = "Linear Rec.709 to factory scene-linear RGB"]
#[doc = "hb:symbol=mathutils.Color.from_scene_linear_to_aces"]
#[doc = "Factory scene-linear RGB to ACES AP0"]
#[doc = "hb:symbol=mathutils.Color.from_scene_linear_to_rec709_linear"]
#[doc = "Factory scene-linear RGB to linear Rec.709"]
#[doc = "hb:symbol=mathutils.Color.from_scene_linear_to_srgb"]
#[doc = "Factory scene-linear matrix plus measured fast sRGB transfer behavior; positive linear components up to 1e10"]
#[doc = "hb:symbol=mathutils.Color.from_scene_linear_to_xyz_d65"]
#[doc = "Factory scene-linear RGB to CIE XYZ D65"]
#[doc = "hb:symbol=mathutils.Color.from_srgb_to_scene_linear"]
#[doc = "sRGB transfer decoding plus factory scene-linear matrix"]
#[doc = "hb:symbol=mathutils.Color.from_xyz_d65_to_scene_linear"]
#[doc = "CIE XYZ D65 to factory scene-linear RGB"]
#[doc = "hb:symbol=mathutils.Color.g"]
#[doc = "Mutable green channel"]
#[doc = "hb:symbol=mathutils.Color.h"]
#[doc = "HSV hue; assignments clamp to 0..1"]
#[doc = "hb:symbol=mathutils.Color.hsv"]
#[doc = "HSV tuple; assignments clamp all three components to 0..1"]
#[doc = "hb:symbol=mathutils.Color.is_frozen"]
#[doc = "Read-only immutability flag"]
#[doc = "hb:symbol=mathutils.Color.is_valid"]
#[doc = "Read-only validity flag"]
#[doc = "hb:symbol=mathutils.Color.is_wrapped"]
#[doc = "Read-only ownership flag"]
#[doc = "hb:symbol=mathutils.Color.owner"]
#[doc = "Owning RNA value or None for standalone colors"]
#[doc = "hb:symbol=mathutils.Color.r"]
#[doc = "Mutable red channel"]
#[doc = "hb:symbol=mathutils.Color.s"]
#[doc = "HSV saturation; assignments clamp to 0..1"]
#[doc = "hb:symbol=mathutils.Color.v"]
#[doc = "HSV value; assignments clamp to 0..1"]
#[test]
fn golden_011() {
    golden("compat/golden/m2_colors.py");
}

#[doc = "hb:test=compat/golden/m2_data_access.py"]
#[doc = "hb:symbol=bpy.types.Image.pixels"]
#[doc = "Flat RGBA sequence supporting whole-property and indexed/slice assignment"]
#[doc = "hb:symbol=bpy.types.ShaderNode.bl_idname"]
#[doc = "Read-only Blender node identifier"]
#[doc = "hb:symbol=bpy.types.ShaderNode.type"]
#[doc = "Read-only node enum for the supported Principled/output/image/normal-map nodes"]
#[test]
fn golden_012() {
    golden("compat/golden/m2_data_access.py");
}

#[doc = "hb:test=compat/golden/m2_displace.py"]
#[doc = "hb:symbol=bpy.data.textures.new"]
#[doc = "Create a CLOUDS procedural texture"]
#[doc = "hb:symbol=bpy.data.textures.remove"]
#[doc = "Remove textures and unlink modifier users"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.cloud_type"]
#[doc = "GRAYSCALE"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.contrast"]
#[doc = "Texture contrast"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.evaluate"]
#[doc = "Evaluate cell-noise texture at local coordinates"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.intensity"]
#[doc = "Texture brightness"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.name"]
#[doc = "Texture data-block name"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.noise_basis"]
#[doc = "CELL_NOISE evaluation; BLENDER_ORIGINAL default readable"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.noise_depth"]
#[doc = "Noise octaves, 0..30"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.noise_scale"]
#[doc = "Procedural noise scale"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.noise_type"]
#[doc = "SOFT_NOISE or HARD_NOISE"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.type"]
#[doc = "CLOUDS type"]
#[doc = "hb:symbol=bpy.types.CloudsTexture.users"]
#[doc = "Texture user count"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.direction"]
#[doc = "NORMAL, X, Y or Z"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.invert_vertex_group"]
#[doc = "Invert vertex-group influence as 1-weight; ignored when the named group is absent"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.mid_level"]
#[doc = "Neutral intensity"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.show_render"]
#[doc = "Render evaluation flag"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.show_viewport"]
#[doc = "Viewport evaluation flag"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.space"]
#[doc = "LOCAL"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.strength"]
#[doc = "Displacement strength"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.texture"]
#[doc = "Procedural CLOUDS texture or None"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.texture_coords"]
#[doc = "LOCAL"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.type"]
#[doc = "DISPLACE type"]
#[doc = "hb:symbol=bpy.types.DisplaceModifier.vertex_group"]
#[doc = "Vertex-group name controlling displacement strength; missing or empty name means full influence"]
#[test]
fn golden_013() {
    golden("compat/golden/m2_displace.py");
}

#[doc = "hb:test=compat/golden/m2_extrude.py"]
#[doc = "hb:symbol=bmesh.ops.extrude_face_region"]
#[doc = "Extrude manifold face regions or mixed vertices/edges/faces, wire edges and isolated vertices with default flags; mixed faces require one connected region and retained attached caps require flat incident faces; use_keep_orig controls attached input cap removal; return duplicated vertices/edges/caps; stable indices and wall order can differ from Blender"]
#[doc = "hb:symbol=bmesh.types.BMEdge.is_valid"]
#[doc = "Edge handle validity, including after BMesh.free"]
#[doc = "hb:symbol=bmesh.types.BMFace.is_valid"]
#[doc = "Face handle validity, including after BMesh.free"]
#[test]
fn golden_014() {
    golden("compat/golden/m2_extrude.py");
}

#[doc = "hb:test=compat/golden/m2_join.py"]
#[doc = "hb:symbol=bpy.ops.object.join"]
#[doc = "Join selected meshes using world transforms, including reflections, shared data and direct hierarchy relations; update all active-data users, detach removed-source children; UV/material slots retained; no modifiers or other indexed custom attributes"]
#[test]
fn golden_015() {
    golden("compat/golden/m2_join.py");
}

#[doc = "hb:test=compat/golden/m2_light_shapes.py"]
#[doc = "hb:symbol=bpy.types.Light.shape"]
#[doc = "AREA emitter shape: SQUARE, RECTANGLE, DISK or ELLIPSE"]
#[doc = "hb:symbol=bpy.types.Light.size_y"]
#[doc = "Secondary AREA emitter extent"]
#[doc = "hb:symbol=bpy.types.Light.use_shadow"]
#[doc = "Enable or disable shadow casting"]
#[test]
fn golden_016() {
    golden("compat/golden/m2_light_shapes.py");
}

#[doc = "hb:test=compat/golden/m2_mathutils.py"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.to_matrix"]
#[doc = "Object rotation matrix"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.to_quaternion"]
#[doc = "Object rotation quaternion"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.x"]
#[doc = "Mutable X Euler angle"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.y"]
#[doc = "Mutable Y Euler angle"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.z"]
#[doc = "Mutable Z Euler angle"]
#[doc = "hb:symbol=mathutils.Euler"]
#[doc = "Mutable float32 Euler angles, six rotation orders"]
#[doc = "hb:symbol=mathutils.Euler.copy"]
#[doc = "Independent copy"]
#[doc = "hb:symbol=mathutils.Euler.order"]
#[doc = "Rotation order"]
#[doc = "hb:symbol=mathutils.Euler.to_matrix"]
#[doc = "Rotation matrix"]
#[doc = "hb:symbol=mathutils.Euler.to_quaternion"]
#[doc = "Rotation quaternion"]
#[doc = "hb:symbol=mathutils.Euler.x"]
#[doc = "X angle"]
#[doc = "hb:symbol=mathutils.Euler.y"]
#[doc = "Y angle"]
#[doc = "hb:symbol=mathutils.Euler.z"]
#[doc = "Z angle"]
#[doc = "hb:symbol=mathutils.Euler.zero"]
#[doc = "Zero angles"]
#[doc = "hb:symbol=mathutils.Matrix.Diagonal"]
#[doc = "Diagonal matrix"]
#[doc = "hb:symbol=mathutils.Matrix.Identity"]
#[doc = "Identity matrix"]
#[doc = "hb:symbol=mathutils.Matrix.Rotation"]
#[doc = "Axis-angle rotation matrix"]
#[doc = "hb:symbol=mathutils.Matrix.Scale"]
#[doc = "Uniform or directional scaling matrix"]
#[doc = "hb:symbol=mathutils.Matrix.Translation"]
#[doc = "Homogeneous translation matrix"]
#[doc = "hb:symbol=mathutils.Matrix.copy"]
#[doc = "Independent copy"]
#[doc = "hb:symbol=mathutils.Matrix.determinant"]
#[doc = "Matrix determinant"]
#[doc = "hb:symbol=mathutils.Matrix.invert"]
#[doc = "In-place inverse"]
#[doc = "hb:symbol=mathutils.Matrix.inverted"]
#[doc = "Inverse with optional fallback"]
#[doc = "hb:symbol=mathutils.Matrix.to_3x3"]
#[doc = "Resize to 3x3"]
#[doc = "hb:symbol=mathutils.Matrix.to_4x4"]
#[doc = "Resize to 4x4"]
#[doc = "hb:symbol=mathutils.Matrix.to_euler"]
#[doc = "Euler rotation from a matrix"]
#[doc = "hb:symbol=mathutils.Matrix.to_quaternion"]
#[doc = "Rotation quaternion from a matrix"]
#[doc = "hb:symbol=mathutils.Matrix.translation"]
#[doc = "Mutable homogeneous translation vector"]
#[doc = "hb:symbol=mathutils.Matrix.transpose"]
#[doc = "In-place transpose"]
#[doc = "hb:symbol=mathutils.Matrix.transposed"]
#[doc = "Transposed copy"]
#[doc = "hb:symbol=mathutils.Quaternion"]
#[doc = "Float32 quaternion from components or axis and angle"]
#[doc = "hb:symbol=mathutils.Quaternion.conjugate"]
#[doc = "Conjugate in place"]
#[doc = "hb:symbol=mathutils.Quaternion.conjugated"]
#[doc = "Conjugated copy"]
#[doc = "hb:symbol=mathutils.Quaternion.copy"]
#[doc = "Independent copy"]
#[doc = "hb:symbol=mathutils.Quaternion.dot"]
#[doc = "Quaternion dot product"]
#[doc = "hb:symbol=mathutils.Quaternion.invert"]
#[doc = "Invert in place"]
#[doc = "hb:symbol=mathutils.Quaternion.inverted"]
#[doc = "Inverted copy"]
#[doc = "hb:symbol=mathutils.Quaternion.magnitude"]
#[doc = "Quaternion norm"]
#[doc = "hb:symbol=mathutils.Quaternion.normalize"]
#[doc = "Normalize in place"]
#[doc = "hb:symbol=mathutils.Quaternion.normalized"]
#[doc = "Normalized copy"]
#[doc = "hb:symbol=mathutils.Quaternion.to_euler"]
#[doc = "Euler conversion in six orders"]
#[doc = "hb:symbol=mathutils.Quaternion.to_matrix"]
#[doc = "3x3 rotation matrix"]
#[doc = "hb:symbol=mathutils.Quaternion.w"]
#[doc = "Scalar component"]
#[doc = "hb:symbol=mathutils.Quaternion.x"]
#[doc = "X component"]
#[doc = "hb:symbol=mathutils.Quaternion.y"]
#[doc = "Y component"]
#[doc = "hb:symbol=mathutils.Quaternion.z"]
#[doc = "Z component"]
#[doc = "hb:symbol=mathutils.Vector.to_track_quat"]
#[doc = "Track signed local axis toward vector with world Z as up; quaternion signs are rotation-equivalent"]
#[test]
fn golden_017() {
    golden("compat/golden/m2_mathutils.py");
}

#[doc = "hb:test=compat/golden/m2_normals.py"]
#[doc = "hb:symbol=bmesh.ops.recalc_face_normals"]
#[doc = "Orient selected faces using complete connected manifold components with planar faces; closed components use signed volume, open components use extremal-corner orientation; refresh all normals without topology reordering; degenerate/non-orientable/non-manifold inputs rejected"]
#[doc = "hb:symbol=bmesh.types.BMEdge.index"]
#[doc = "Read or write a valid edge index; normal repair refreshes sequential indices without reordering edges"]
#[doc = "hb:symbol=bmesh.types.BMFace.index"]
#[doc = "Read or write a valid face index; normal repair refreshes sequential indices without reordering faces"]
#[test]
fn golden_018() {
    golden("compat/golden/m2_normals.py");
}

#[doc = "hb:test=compat/golden/m2_object_ops.py"]
#[doc = "hb:symbol=bpy.ops.object.camera_add"]
#[doc = "Create a camera in object mode with WORLD alignment; input scale is ignored, matching Blender."]
#[doc = "hb:symbol=bpy.ops.object.empty_add"]
#[doc = "Create non-image empty object display shapes; radius sets display size."]
#[doc = "hb:symbol=bpy.ops.object.light_add"]
#[doc = "Create POINT/SUN/SPOT/AREA lights; AREA radius sets size, input scale is ignored."]
#[doc = "hb:symbol=bpy.types.Object.dimensions"]
#[doc = "Evaluated local bounding-box dimensions multiplied by world-axis scale; assignment preserves scale signs."]
#[doc = "hb:symbol=bpy.types.Object.empty_display_size"]
#[doc = "Persistent empty display radius, clamped at 0.0001."]
#[doc = "hb:symbol=bpy.types.Object.empty_display_type"]
#[doc = "Persistent empty display shape, excluding image empties."]
#[test]
fn golden_019() {
    golden("compat/golden/m2_object_ops.py");
}

#[doc = "hb:test=compat/golden/m2_primitives.py"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_circle_add"]
#[doc = "WORLD/CURSOR circle in object or single-mesh EDIT construction; vertices/radius, NOTHING/NGON/TRIFAN; construction scale ignored; zero radius requires calc_uvs=False"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_cylinder_add"]
#[doc = "WORLD/CURSOR cylinder in object or single-mesh EDIT construction; vertices/radius/depth, NGON/TRIFAN/NOTHING caps, finite degenerate wire geometry; explicit scale including zero; negative scale requires calc_uvs=False"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_plane_add"]
#[doc = "WORLD/CURSOR plane in object or single-mesh EDIT construction; size including zero, location/rotation, optional UVs; construction scale ignored"]
#[test]
fn golden_020() {
    golden("compat/golden/m2_primitives.py");
}

#[doc = "hb:test=compat/golden/m2_round_primitives.py"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_cone_add"]
#[doc = "WORLD/CURSOR cone/frustum in object or single-mesh EDIT construction; vertices/radii/depth and caps, finite degenerate wire geometry; explicit positive/zero scale and optional UVs; negative scale requires calc_uvs=False"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_uv_sphere_add"]
#[doc = "WORLD/CURSOR UV sphere in object or single-mesh EDIT construction; segments/rings/radius, explicit scale including zero; zero radius requires calc_uvs=False and keeps an unmerged quad grid; construction limit 100000 vertices"]
#[test]
fn golden_021() {
    golden("compat/golden/m2_round_primitives.py");
}

#[doc = "hb:test=compat/golden/m2_subsurf.py"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.boundary_smooth"]
#[doc = "ALL or PRESERVE_CORNERS"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.levels"]
#[doc = "Viewport subdivision levels 0..6; two-million evaluated vertex/face limit"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.quality"]
#[doc = "Default quality 3"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.render_levels"]
#[doc = "Render subdivision levels 0..6; two-million evaluated vertex/face limit"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.show_only_control_edges"]
#[doc = "Control edge display flag; does not change exported surface"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.show_render"]
#[doc = "Preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.show_viewport"]
#[doc = "Viewport and glTF evaluation flag"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.subdivision_type"]
#[doc = "CATMULL_CLARK or SIMPLE"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.type"]
#[doc = "SUBSURF"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.use_creases"]
#[doc = "Use edge/vertex creases for geometry; retain crease attributes in either mode"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.use_limit_surface"]
#[doc = "Evaluate the limit surface or finite refinement"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.uv_smooth"]
#[doc = "PRESERVE_BOUNDARIES"]
#[test]
fn golden_022() {
    golden("compat/golden/m2_subsurf.py");
}

#[doc = "hb:test=compat/golden/m2_topology.py"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.merge_threshold"]
#[doc = "Mirror seam distance threshold"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.show_render"]
#[doc = "CPU preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.show_viewport"]
#[doc = "Viewport evaluation flag"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.type"]
#[doc = "MIRROR"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_axis"]
#[doc = "X/Y/Z axis flags; axes applied in order"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_clip"]
#[doc = "Edit-mode clipping flag; no effect on object-mode evaluation"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_mirror_merge"]
#[doc = "Merge matching vertices across the mirror plane"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.material_offset"]
#[doc = "Inner shell material offset"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.material_offset_rim"]
#[doc = "Rim material offset"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.offset"]
#[doc = "Thickness offset -1..1"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.show_render"]
#[doc = "CPU preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.show_viewport"]
#[doc = "Viewport evaluation flag"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.thickness"]
#[doc = "Signed shell thickness"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.type"]
#[doc = "SOLIDIFY"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.use_rim"]
#[doc = "Generate boundary walls"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.use_rim_only"]
#[doc = "Keep original surface and boundary walls; omit the inner shell"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.min_vertices"]
#[doc = "Minimum face vertex count"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.show_render"]
#[doc = "CPU preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.show_viewport"]
#[doc = "Viewport evaluation flag"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.type"]
#[doc = "TRIANGULATE"]
#[test]
fn golden_023() {
    golden("compat/golden/m2_topology.py");
}

#[doc = "hb:test=compat/golden/m2_torus.py"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_torus_add"]
#[doc = "WORLD/CURSOR torus in object or existing single-mesh EDIT context; segments 3..256, MAJOR_MINOR or EXT_INT, 0 <= minor <= major including zero, optional UVs; self-intersecting radii excluded"]
#[test]
fn golden_024() {
    golden("compat/golden/m2_torus.py");
}

#[doc = "hb:test=compat/golden/m2_transform_apply.py"]
#[doc = "hb:symbol=bpy.ops.object.transform_apply"]
#[doc = "Bake selected TRS mesh transforms with nonzero scales, including reflections and child compensation; isolate_users False/True, transform shared data once when all users selected; shared selected users must be unparented without children; no shape keys or reflected packed normals"]
#[test]
fn golden_025() {
    golden("compat/golden/m2_transform_apply.py");
}

#[doc = "hb:test=compat/golden/m2_transform_editing.py"]
#[doc = "hb:symbol=bmesh.ops.create_circle"]
#[doc = "Circle creation with optional 3x3/4x4 matrix; no editable UV layers"]
#[doc = "hb:symbol=bmesh.ops.create_cone"]
#[doc = "Cone creation with optional 3x3/4x4 matrix; no editable UV layers"]
#[doc = "hb:symbol=bmesh.ops.create_cube"]
#[doc = "Cube creation with optional 3x3/4x4 matrix; no editable UV layers"]
#[doc = "hb:symbol=bmesh.ops.create_grid"]
#[doc = "Grid creation with optional 3x3/4x4 matrix; no editable UV layers"]
#[doc = "hb:symbol=bmesh.ops.create_uvsphere"]
#[doc = "UV-sphere creation with optional 3x3/4x4 matrix; no editable UV layers"]
#[doc = "hb:symbol=bmesh.ops.rotate"]
#[doc = "Rotate selected editable vertices about a center with 3x3/4x4 matrices and nonsingular space; use_shapekey optionally transforms all shape layers"]
#[doc = "hb:symbol=bmesh.ops.scale"]
#[doc = "Scale editable vertices in nonsingular 3x3/4x4 space; returns None"]
#[doc = "hb:symbol=bmesh.ops.transform"]
#[doc = "Apply a 3x3/4x4 affine transform in nonsingular space; use_shapekey optionally transforms all shape layers"]
#[doc = "hb:symbol=bmesh.ops.translate"]
#[doc = "Translate editable vertices in nonsingular 3x3/4x4 space; returns None"]
#[test]
fn golden_026() {
    golden("compat/golden/m2_transform_editing.py");
}

#[doc = "hb:test=compat/golden/m2_uv_init.py"]
#[doc = "hb:symbol=bpy.types.Mesh.uv_layers.new"]
#[doc = "new(name=\"UVMap\", do_init=True); initialize triangle/quad/ngon UVs, copy the active layer when present, or zero-fill with do_init=False"]
#[test]
fn golden_027() {
    golden("compat/golden/m2_uv_init.py");
}

#[doc = "hb:test=compat/golden/m2_vectors.py"]
#[doc = "hb:symbol=mathutils.Vector"]
#[doc = "Mutable 2D/3D/4D float32 vector; default is zero 3D"]
#[doc = "hb:symbol=mathutils.Vector.angle"]
#[doc = "Angle in radians, with optional fallback for zero vectors"]
#[doc = "hb:symbol=mathutils.Vector.copy"]
#[doc = "Independent vector copy"]
#[doc = "hb:symbol=mathutils.Vector.cross"]
#[doc = "3D cross product"]
#[doc = "hb:symbol=mathutils.Vector.dot"]
#[doc = "Dot product of equal-sized vectors"]
#[doc = "hb:symbol=mathutils.Vector.length"]
#[doc = "Euclidean length, assignable"]
#[doc = "hb:symbol=mathutils.Vector.length_squared"]
#[doc = "Squared Euclidean length"]
#[doc = "hb:symbol=mathutils.Vector.lerp"]
#[doc = "Linear interpolation"]
#[doc = "hb:symbol=mathutils.Vector.negate"]
#[doc = "Negate in place"]
#[doc = "hb:symbol=mathutils.Vector.normalize"]
#[doc = "Normalize in place; zero vector remains zero"]
#[doc = "hb:symbol=mathutils.Vector.normalized"]
#[doc = "Normalized copy"]
#[doc = "hb:symbol=mathutils.Vector.project"]
#[doc = "Projection onto a vector"]
#[doc = "hb:symbol=mathutils.Vector.reflect"]
#[doc = "Reflection across a normal"]
#[doc = "hb:symbol=mathutils.Vector.to_2d"]
#[doc = "Copy as 2D"]
#[doc = "hb:symbol=mathutils.Vector.to_3d"]
#[doc = "Copy as 3D"]
#[doc = "hb:symbol=mathutils.Vector.to_4d"]
#[doc = "Copy as homogeneous 4D"]
#[doc = "hb:symbol=mathutils.Vector.w"]
#[doc = "W component"]
#[doc = "hb:symbol=mathutils.Vector.x"]
#[doc = "X component"]
#[doc = "hb:symbol=mathutils.Vector.xy"]
#[doc = "Two-component swizzle"]
#[doc = "hb:symbol=mathutils.Vector.xyz"]
#[doc = "Three-component swizzle"]
#[doc = "hb:symbol=mathutils.Vector.y"]
#[doc = "Y component"]
#[doc = "hb:symbol=mathutils.Vector.yxz"]
#[doc = "Swizzle assignment"]
#[doc = "hb:symbol=mathutils.Vector.z"]
#[doc = "Z component"]
#[doc = "hb:symbol=mathutils.Vector.zero"]
#[doc = "Set all components to zero"]
#[test]
fn golden_028() {
    golden("compat/golden/m2_vectors.py");
}

#[doc = "hb:test=compat/golden/m2_weighted_normals.py"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.invert_vertex_group"]
#[doc = "Invert membership filtering; weight magnitude does not scale normals"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.keep_sharp"]
#[doc = "Keep separate smooth fans at flat/smooth and nonmanifold boundaries"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.mode"]
#[doc = "FACE_AREA, CORNER_ANGLE or FACE_AREA_WITH_ANGLE"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.show_render"]
#[doc = "Preview modifier visibility"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.show_viewport"]
#[doc = "Viewport and glTF modifier visibility"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.thresh"]
#[doc = "Finite grouping threshold 0..10, default 0.01"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.type"]
#[doc = "WEIGHTED_NORMAL"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.use_face_influence"]
#[doc = "Use strongest adjacent faces from __mod_weightednormals_faceweight INT FACE (0/1/2)"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.vertex_group"]
#[doc = "Named membership filter, including zero-weight members; missing group leaves all vertices selected"]
#[doc = "hb:symbol=bpy.types.WeightedNormalModifier.weight"]
#[doc = "Integer contrast 1..100, default 50"]
#[test]
fn golden_029() {
    golden("compat/golden/m2_weighted_normals.py");
}

#[doc = "hb:test=compat/golden/m2_weld.py"]
#[doc = "hb:symbol=bpy.types.WeldModifier.name"]
#[doc = "Modifier name"]
#[doc = "hb:symbol=bpy.types.WeldModifier.show_render"]
#[doc = "CPU preview evaluation flag"]
#[doc = "hb:symbol=bpy.types.WeldModifier.show_viewport"]
#[doc = "Viewport query and glTF export evaluation flag"]
#[doc = "hb:symbol=bpy.types.WeldModifier.type"]
#[doc = "WELD"]
#[test]
fn golden_030() {
    golden("compat/golden/m2_weld.py");
}

#[doc = "hb:test=compat/golden/m2_world.py"]
#[doc = "hb:symbol=bpy.context.scene.world"]
#[doc = "Scene world datablock reference"]
#[doc = "hb:symbol=bpy.data.worlds.get"]
#[doc = "Look up a World by name"]
#[doc = "hb:symbol=bpy.data.worlds.new"]
#[doc = "Create a named World with constant-color settings"]
#[doc = "hb:symbol=bpy.data.worlds.remove"]
#[doc = "Remove a World and unlink scene users"]
#[doc = "hb:symbol=bpy.types.World.color"]
#[doc = "Persistent RGB world color"]
#[doc = "hb:symbol=bpy.types.World.name"]
#[doc = "World datablock name"]
#[doc = "hb:symbol=bpy.types.World.use_nodes"]
#[doc = "Read/write node usage; first enable creates Background from world.color; disabling retains nodes and selects constant-color lighting"]
#[doc = "hb:symbol=bpy.types.World.users"]
#[doc = "World scene user count"]
#[test]
fn golden_031() {
    golden("compat/golden/m2_world.py");
}

#[doc = "hb:test=compat/golden/m3_ico_sphere.py"]
#[doc = "hb:symbol=bpy.ops.mesh.primitive_ico_sphere_add"]
#[doc = "WORLD/CURSOR ico sphere in object or single-mesh EDIT construction; subdivisions 1..7, radius including zero, explicit scale including zero, optional seam UVs; equivalent indexed topology"]
#[test]
fn golden_ico_sphere() {
    golden("compat/golden/m3_ico_sphere.py");
}

#[doc = "hb:test=compat/golden/m3_duplicate.py"]
#[doc = "hb:symbol=bpy.ops.object.duplicate"]
#[doc = "Duplicate selected objects with linked=False/True; preserve collection links, copied-data sharing, modifiers and selection, and remap selected parents; default TRANSLATION mode"]
#[test]
fn golden_duplicate() {
    golden("compat/golden/m3_duplicate.py");
}

#[doc = "hb:test=compat/golden/m3_parent_set.py"]
#[doc = "hb:symbol=bpy.ops.object.parent_set"]
#[doc = "Parent selected children to the active object; type=OBJECT, keep_transform False/True, inverse-parent compensation and cycle rejection; nonsingular parent transform"]
#[test]
fn golden_parent_set() {
    golden("compat/golden/m3_parent_set.py");
}

#[doc = "hb:test=compat/golden/m3_origin_set.py"]
#[doc = "hb:symbol=bpy.ops.object.origin_set"]
#[doc = "Selected meshes: ORIGIN_GEOMETRY or GEOMETRY_ORIGIN, MEDIAN or BOUNDS center; preserve dependent children for nonsingular transforms; shift shared mesh data once, leaving unselected users' transforms unchanged"]
#[test]
fn golden_origin_set() {
    golden("compat/golden/m3_origin_set.py");
}

#[doc = "hb:test=compat/golden/m3_import_gltf.py"]
#[doc = "hb:symbol=bpy.ops.import_scene.gltf"]
#[doc = "Import GLB/glTF into the active collection, select imported objects and preserve hierarchy; file vertex indexing, scalar Principled material inputs and native asset bindings; arbitrary generated shader graphs are not reconstructed"]
#[doc = "hb:symbol=bpy.types.Object.rotation_mode"]
#[doc = "Six Euler orders and QUATERNION; Euler order changes retain angles, Euler/quaternion transitions convert orientation"]
#[doc = "hb:symbol=bpy.types.Object.rotation_quaternion"]
#[doc = "Mutable WXYZ quaternion view; used for object transforms in QUATERNION mode"]
#[test]
fn golden_import_gltf() {
    golden("compat/golden/m3_import_gltf.py");
}

#[doc = "hb:test=compat/golden/m3_export_gltf.py"]
#[doc = "hb:symbol=bpy.ops.export_scene.gltf"]
#[doc = "GLB or GLTF_SEPARATE export; selection, applied modifiers, optional cameras/lights; each output file atomically replaced, no cross-file transaction"]
#[test]
fn golden_export_gltf() {
    golden("compat/golden/m3_export_gltf.py");
}

#[doc = "hb:test=compat/golden/m3_import_obj.py"]
#[doc = "hb:symbol=bpy.ops.import_scene.obj"]
#[doc = "Legacy Blender 3.6 OBJ operator: split named objects, declared forward/up axes, faces, UVs, normals, smoothing and scalar MTL; imported selection retains the previous active object"]
#[test]
fn golden_import_obj() {
    golden("compat/golden/m3_import_obj.py");
}

#[doc = "hb:test=compat/golden/m3_export_obj.py"]
#[doc = "hb:symbol=bpy.ops.export_scene.obj"]
#[doc = "Legacy OBJ/MTL mesh export: selection, applied modifiers, normals, UVs, triangulation, signed axis pair and positive scale; scalar Principled factors and base/alpha/normal images; per-file atomic writes"]
#[test]
fn golden_export_obj() {
    golden("compat/golden/m3_export_obj.py");
}

#[doc = "hb:test=compat/golden/m3_render_operator.py"]
#[doc = "hb:symbol=bpy.ops.render.render"]
#[doc = "Current scene camera CPU raster preview; write_still False/True, resolution percentage and pixel aspect, PNG output up to 2048 pixels per axis. No animation/viewport overrides, Blender pixel parity or persistent Render Result datablock"]
#[test]
fn golden_render_operator() {
    golden("compat/golden/m3_render_operator.py");
}

#[doc = "hb:test=compat/golden/m3_inset_region.py"]
#[doc = "hb:symbol=bmesh.ops.inset_region"]
#[doc = "Noncollapsing planar manifold face regions, thickness/depth, boundary and even-offset modes; retain input face handles, return rim faces; no relative offset, edge rail or outset"]
#[test]
fn golden_inset_region() {
    golden("compat/golden/m3_inset_region.py");
}

#[doc = "hb:test=compat/golden/m3_bmesh_bevel.py"]
#[doc = "hb:symbol=bmesh.ops.bevel"]
#[doc = "All edges of a closed convex mesh, OFFSET, profile 0.5, 1..8 segments and nonoverlapping width; canonical cuboids retain uniform-face requirements; return beveled faces/all new edges and vertices, invalidate old handles; no-op empty or zero offset"]
#[test]
fn golden_bmesh_bevel() {
    golden("compat/golden/m3_bmesh_bevel.py");
}

#[doc = "hb:test=compat/golden/m3_remove_doubles.py"]
#[doc = "hb:symbol=bmesh.ops.remove_doubles"]
#[doc = "Merge selected vertices using Blender-compatible float32 spatial representatives and distance boundaries; remove duplicate/collapsed edges and faces, split repeated-corner polygons, retain target coordinates; returns None"]
#[test]
fn golden_remove_doubles() {
    golden("compat/golden/m3_remove_doubles.py");
}

#[doc = "hb:test=compat/golden/m3_subdivide_edges.py"]
#[doc = "hb:symbol=bmesh.ops.subdivide_edges"]
#[doc = "Linear cuts 0..64: complete triangle/quad grids, unfilled whole/one-edge boundaries, adjacent quad corner cuts and wires; preserve original handles and return geom_inner/geom_split/geom; no smoothing/fractal options"]
#[test]
fn golden_subdivide_edges() {
    golden("compat/golden/m3_subdivide_edges.py");
}

#[doc = "hb:test=compat/golden/m3_bisect_plane.py"]
#[doc = "hb:symbol=bmesh.ops.bisect_plane"]
#[doc = "Finite plane, selected vertices/edges/faces, single-segment polygon cuts, snap-center and clear-inner/outer; preserve surviving handles and return geom/geom_cut; 100,000 vertices/faces"]
#[test]
fn golden_bisect_plane() {
    golden("compat/golden/m3_bisect_plane.py");
}

#[doc = "hb:test=compat/golden/m3_bmesh_solidify.py"]
#[doc = "hb:symbol=bmesh.ops.solidify"]
#[doc = "Finite positive/negative/zero thickness; oriented manifold face shells with miter offsets, edge and vertex selections; retain original handles, return new shell vertices/edges/caps; 100,000 vertices/faces"]
#[test]
fn golden_bmesh_solidify() {
    golden("compat/golden/m3_bmesh_solidify.py");
}

#[doc = "hb:test=compat/golden/m3_bmesh_triangulate.py"]
#[doc = "hb:symbol=bmesh.ops.triangulate"]
#[doc = "Planar simple faces, up to 2048 corners: BEAUTY/FIXED/ALTERNATE/SHORT_EDGE/LONG_EDGE quads and BEAUTY/EAR_CLIP n-gons; retain original face handle, copy attributes, return edges/faces/face_map/face_map_double; 100,000 faces"]
#[test]
fn golden_bmesh_triangulate() {
    golden("compat/golden/m3_bmesh_triangulate.py");
}

#[doc = "hb:test=compat/golden/m3_format_obj.py"]
#[doc = "hb:symbol=hb.export.obj"]
#[doc = "CLI hb export and run --out .obj: evaluated linked meshes in Z-up meters, reflected winding, UV/normal corner indices, scalar MTL and PNG image companions; per-file atomic output, preserve revision"]
#[test]
fn format_obj_export() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-obj-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    let result = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
        .arg("run")
        .arg(root.join("compat/golden/m3_format_obj.py"))
        .args(["--out", "scene.obj"])
        .current_dir(&temp)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stdout)
    );
    let obj = std::fs::read_to_string(temp.join("scene.obj")).unwrap();
    assert_eq!(
        obj.lines().filter(|line| line.starts_with("f ")).count(),
        32
    );
    assert!(temp.join("scene.mtl").is_file());
    std::fs::remove_dir_all(temp).unwrap();
}

#[doc = "hb:test=compat/golden/m3_format_usdz.py"]
#[doc = "hb:symbol=hb.export.usdz"]
#[doc = "CLI USDZ: aligned uncompressed USDA/PNG archive, evaluated linked meshes, hierarchy, face materials, UVs/normals/colors, perspective and standard-unit orthographic cameras (warns about Blender 4.5 10x ortho import); POINT/SPOT/SUN/AREA lights; generated float images use 16-bit PNG, byte images 8-bit; warns that World environments are omitted"]
#[test]
fn format_usdz_export() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-usdz-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    let result = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
        .arg("run")
        .arg(root.join("compat/golden/m3_format_usdz.py"))
        .args(["--out", "scene.usdz"])
        .current_dir(&temp)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stdout)
    );
    let bytes = std::fs::read(temp.join("scene.usdz")).unwrap();
    assert!(bytes.starts_with(b"PK\x03\x04"));
    assert!(bytes.windows(9).any(|part| part == b"#usda 1.0"));
    std::fs::remove_dir_all(temp).unwrap();
}

#[doc = "hb:test=compat/fixtures/stl/triangles-ascii.stl"]
#[doc = "hb:symbol=hb.import.stl"]
#[doc = "CLI ASCII and little-endian binary STL: exact-length binary detection including solid headers, finite float32 XYZ in Z-up meters, geometric normals, exact-coordinate welding and duplicate/repeated-vertex triangle cleanup; 100,000 triangles/vertices, 32 MiB input; no facet-normal override or nonstandard facet colors"]
#[test]
fn format_stl_import() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-stl-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    let result = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
        .arg("import")
        .arg(root.join("compat/fixtures/stl/triangles-ascii.stl"))
        .current_dir(&temp)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stdout)
    );
    assert!(temp.join("scene.hb").is_file());
    std::fs::remove_dir_all(temp).unwrap();
}

#[doc = "hb:test=compat/fixtures/ply/ascii.ply"]
#[doc = "hb:symbol=hb.import.ply"]
#[doc = "CLI PLY 1.0 ASCII/little-endian/big-endian: standard 8/16/32-bit integer and float32/64 scalar/list types, XYZ vertices, polygon faces, loose edges, vertex s/t UVs, nonzero normals and uchar/float RGB(A) sRGB conversion; bounded cleanup, warns for ignored attributes; 32 MiB, 100,000 rows/element, 2048 corners/face, four million scalar values"]
#[test]
fn format_ply_import() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-ply-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    let result = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
        .arg("import")
        .arg(root.join("compat/fixtures/ply/ascii.ply"))
        .current_dir(&temp)
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stdout)
    );
    assert!(temp.join("scene.hb").is_file());
    std::fs::remove_dir_all(temp).unwrap();
}

#[doc = "hb:test=compat/golden/m3_array.py"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.use_merge_vertices"]
#[doc = "Weld adjacent copies and caps within merge_threshold; retain target coordinates and corner attributes; remove collapsed/duplicate faces"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.use_object_offset"]
#[doc = "Compose owner-relative offset object affine transform with relative/constant translation"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.offset_object"]
#[doc = "Offset object or None; transforms may rotate, scale or reflect copies"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.start_cap"]
#[doc = "Different evaluated mesh object or None, placed one offset before the source; ignores cap object transform and uses source material slots"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.end_cap"]
#[doc = "Different evaluated mesh object or None, placed one offset after the last copy; ignores cap object transform and uses source material slots"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.merge_threshold"]
#[doc = "Float distance 0..1, default 0.01; at most two million proximity checks and two million evaluated vertices/faces"]
#[doc = "hb:symbol=bpy.types.ArrayModifier.use_merge_vertices_cap"]
#[doc = "Also weld first and last copies when merging is enabled"]
#[test]
fn golden_array_extensions() {
    golden("compat/golden/m3_array.py");
}

#[doc = "hb:test=compat/golden/m3_mirror.py"]
#[doc = "hb:symbol=bpy.types.Object.vertex_groups"]
#[doc = "Named vertex groups on a mesh object; at most 1024 groups"]
#[doc = "hb:symbol=bpy.types.Object.vertex_groups.new"]
#[doc = "new(name=Group), unique UTF-8 names with Blender numeric suffixes"]
#[doc = "hb:symbol=bpy.types.Object.vertex_groups.get"]
#[doc = "Lookup a group by name with an optional fallback"]
#[doc = "hb:symbol=bpy.types.Object.vertex_groups.remove"]
#[doc = "Remove one group and reindex mesh deform memberships"]
#[doc = "hb:symbol=bpy.types.Object.vertex_groups.clear"]
#[doc = "Remove all groups and weights"]
#[doc = "hb:symbol=bpy.types.VertexGroup.name"]
#[doc = "Unique mutable group name"]
#[doc = "hb:symbol=bpy.types.VertexGroup.index"]
#[doc = "Current group index"]
#[doc = "hb:symbol=bpy.types.VertexGroup.add"]
#[doc = "Assign valid vertex indices with REPLACE/ADD/SUBTRACT, weights clamped to 0..1"]
#[doc = "hb:symbol=bpy.types.VertexGroup.remove"]
#[doc = "Remove memberships from valid vertex indices"]
#[doc = "hb:symbol=bpy.types.VertexGroup.weight"]
#[doc = "Read a vertex weight; RuntimeError for a vertex outside this group"]
#[doc = "hb:symbol=bpy.types.MeshVertex.groups"]
#[doc = "Read-only membership sequence"]
#[doc = "hb:symbol=bpy.types.VertexGroupElement.group"]
#[doc = "Membership group index"]
#[doc = "hb:symbol=bpy.types.VertexGroupElement.weight"]
#[doc = "Read-only membership weight"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.mirror_object"]
#[doc = "Object defining affine mirror planes, or None for local axes"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_bisect_axis"]
#[doc = "Three boolean flags: trim the negative half before mirroring that enabled axis"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_bisect_flip_axis"]
#[doc = "Three boolean flags: keep the negative half instead"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.bisect_threshold"]
#[doc = "0..1; snap vertices near the bisect plane, default 0.001"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_mirror_vertex_groups"]
#[doc = "Swap matching side names and average seam weights, default True"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_mirror_u"]
#[doc = "Reflect copied U coordinates"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.use_mirror_v"]
#[doc = "Reflect copied V coordinates"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.offset_u"]
#[doc = "-1..1 offset for copied U coordinates"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.offset_v"]
#[doc = "-1..1 offset for copied V coordinates"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.mirror_offset_u"]
#[doc = "-1..1 additional offset when U reflection is enabled"]
#[doc = "hb:symbol=bpy.types.MirrorModifier.mirror_offset_v"]
#[doc = "-1..1 additional offset when V reflection is enabled"]
#[test]
fn golden_mirror_extensions() {
    golden("compat/golden/m3_mirror.py");
}

#[doc = "hb:test=compat/golden/m3_solidify.py"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.solidify_mode"]
#[doc = "EXTRUDE oriented manifold shells or NON_MANIFOLD radial face fans with consistent plane constraints; planar non-degenerate faces and no loose geometry"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.thickness_clamp"]
#[doc = "0..100 edge-length offset clamp, zero disables clamping"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.use_even_offset"]
#[doc = "Angle-weighted shell correction in EXTRUDE; NON_MANIFOLD solves offset planes"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.use_quality_normals"]
#[doc = "Edge-angle weighted normals in EXTRUDE; NON_MANIFOLD uses face planes"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.vertex_group"]
#[doc = "Thickness influence group name or empty; missing groups leave full thickness"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.thickness_vertex_group"]
#[doc = "Minimum thickness factor 0..1, blended with the group weight"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.invert_vertex_group"]
#[doc = "Invert thickness influence weights"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.shell_vertex_group"]
#[doc = "Existing group receiving generated inner-shell memberships at weight one"]
#[doc = "hb:symbol=bpy.types.SolidifyModifier.rim_vertex_group"]
#[doc = "Existing group receiving boundary rim memberships at weight one"]
#[test]
fn golden_solidify_extensions() {
    golden("compat/golden/m3_solidify.py");
}

#[doc = "hb:test=compat/golden/m3_triangulate.py"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.quad_method"]
#[doc = "BEAUTY, FIXED, FIXED_ALTERNATE, SHORTEST_DIAGONAL, LONGEST_DIAGONAL; BEAUTY requires planar simple faces"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.ngon_method"]
#[doc = "BEAUTY or CLIP on planar simple n-gons with 3..2048 corners"]
#[doc = "hb:symbol=bpy.types.TriangulateModifier.keep_custom_normals"]
#[doc = "True preserves corner normals; False remaps encoded corner normals on flat planar faces; smooth custom normals require True"]
#[doc = "hb:symbol=bpy.types.Mesh.normals_split_custom_set"]
#[doc = "Assign one finite nonzero three-component normal per corner, normalized; all values validated before mutation"]
#[doc = "hb:symbol=bpy.types.Mesh.has_custom_normals"]
#[doc = "Whether stored custom corner normals are present"]
#[test]
fn golden_m3_triangulate() {
    golden("compat/golden/m3_triangulate.py");
}

#[doc = "hb:test=compat/golden/m3_weld.py"]
#[doc = "hb:symbol=bpy.types.WeldModifier.mode"]
#[doc = "ALL greedy proximity groups or CONNECTED edge collapse with updated cluster centers; averaged positions and collapsed/pinched/duplicate-face cleanup"]
#[doc = "hb:symbol=bpy.types.WeldModifier.merge_threshold"]
#[doc = "Local float32 distance; ALL uses strict spatial-partition bounds and zero is a no-op; CONNECTED includes equality and coincident vertices at zero"]
#[doc = "hb:symbol=bpy.types.WeldModifier.loose_edges"]
#[doc = "In CONNECTED mode restrict collapse to edges unused by faces; ignored in ALL mode"]
#[doc = "hb:symbol=bpy.types.WeldModifier.vertex_group"]
#[doc = "Select vertices with nonzero group weight; missing/empty group means all vertices; weights do not scale distance"]
#[doc = "hb:symbol=bpy.types.WeldModifier.invert_vertex_group"]
#[doc = "Select zero or missing group weights; merged memberships are averaged and zero merged memberships removed"]
#[test]
fn golden_m3_weld() {
    golden("compat/golden/m3_weld.py");
}

#[doc = "hb:test=compat/golden/m3_boolean.py"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.solver"]
#[doc = "EXACT, FAST or MANIFOLD on closed oriented solids; shared robust kernel, canonical boundary topology; coplanar partition and collinear vertices may differ; reflected transforms require EXACT/FAST"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.operand_type"]
#[doc = "OBJECT or COLLECTION; at most 64 recursive mesh operands, owner excluded; collection INTERSECT requires EXACT or MANIFOLD"]
#[doc = "hb:symbol=bpy.types.BooleanModifier.collection"]
#[doc = "Collection operand or None; recursive membership, evaluated in owner local coordinates; removing the collection clears references"]
#[doc = "hb:symbol=bpy.types.Mesh.color_attributes"]
#[doc = "One FLOAT_COLOR CORNER attribute; indexing, iteration and length"]
#[doc = "hb:symbol=bpy.types.Mesh.color_attributes.new"]
#[doc = "new(name,type,domain): one FLOAT_COLOR CORNER attribute with a name of 1..63 UTF-8 bytes"]
#[doc = "hb:symbol=bpy.types.Mesh.color_attributes.get"]
#[doc = "Find the single corner color attribute by name"]
#[doc = "hb:symbol=bpy.types.FloatColorAttribute.name"]
#[doc = "Read-only attribute name"]
#[doc = "hb:symbol=bpy.types.FloatColorAttribute.domain"]
#[doc = "CORNER"]
#[doc = "hb:symbol=bpy.types.FloatColorAttribute.data_type"]
#[doc = "FLOAT_COLOR"]
#[doc = "hb:symbol=bpy.types.FloatColorAttribute.data"]
#[doc = "Read/write corner values through index or iteration"]
#[doc = "hb:symbol=bpy.types.FloatColorAttributeValue.color"]
#[doc = "Four finite scene-linear RGBA components; indexed writes and whole-vector assignment"]
#[test]
fn golden_m3_boolean() {
    golden("compat/golden/m3_boolean.py");
}

#[doc = "hb:test=compat/golden/m3_subsurf.py"]
#[doc = "hb:symbol=bpy.types.Mesh.attributes"]
#[doc = "Bounded crease and face-strength attributes; indexing, iteration and length"]
#[doc = "hb:symbol=bpy.types.Mesh.attributes.new"]
#[doc = "Create crease_edge FLOAT EDGE, crease_vert FLOAT POINT or __mod_weightednormals_faceweight INT FACE, initialized to zero; duplicate names rejected"]
#[doc = "hb:symbol=bpy.types.Mesh.attributes.get"]
#[doc = "Find a supported crease or face-strength attribute by name"]
#[doc = "hb:symbol=bpy.types.FloatAttribute.name"]
#[doc = "Read-only crease attribute name"]
#[doc = "hb:symbol=bpy.types.FloatAttribute.domain"]
#[doc = "EDGE or POINT according to the crease attribute"]
#[doc = "hb:symbol=bpy.types.FloatAttribute.data_type"]
#[doc = "FLOAT"]
#[doc = "hb:symbol=bpy.types.FloatAttribute.data"]
#[doc = "Per-element values through index or iteration"]
#[doc = "hb:symbol=bpy.types.FloatAttributeValue.value"]
#[doc = "Read/write finite float32 crease value in 0..1"]
#[doc = "hb:symbol=bpy.types.SubsurfModifier.use_custom_normals"]
#[doc = "True preserves quantized custom normals on flat input faces at levels 1..2; False recomputes geometric normals at all supported levels"]
#[test]
fn golden_m3_subsurf() {
    golden("compat/golden/m3_subsurf.py");
}

#[doc = "hb:test=compat/golden/m3_bevel.py"]
#[test]
fn golden_m3_bevel() {
    golden("compat/golden/m3_bevel.py");
    golden("compat/golden/m3_bevel_uv.py");
}

#[doc = "hb:test=compat/golden/m3_displace.py"]
#[test]
fn golden_m3_displace() {
    golden("compat/golden/m3_displace.py");
}

#[doc = "hb:test=compat/golden/m3_weighted_normals.py"]
#[doc = "hb:symbol=bpy.types.IntAttribute.name"]
#[doc = "Read-only __mod_weightednormals_faceweight"]
#[doc = "hb:symbol=bpy.types.IntAttribute.domain"]
#[doc = "FACE"]
#[doc = "hb:symbol=bpy.types.IntAttribute.data_type"]
#[doc = "INT"]
#[doc = "hb:symbol=bpy.types.IntAttribute.data"]
#[doc = "One value per polygon, accessed by index or iteration"]
#[doc = "hb:symbol=bpy.types.IntAttributeValue.value"]
#[doc = "Read/write strength 0 (weak), 1 (medium) or 2 (strong)"]
#[test]
fn golden_m3_weighted_normals() {
    golden("compat/golden/m3_weighted_normals.py");
}

#[doc = "hb:test=compat/golden/m3_bmesh_data.py"]
#[doc = "hb:symbol=bpy.types.Object.shape_key_add"]
#[doc = "Create a relative zero-influence mesh shape key from current geometry, at most 64; name/from_mix keyword arguments"]
#[doc = "hb:symbol=bpy.types.Mesh.shape_keys"]
#[doc = "Read Key container or None; animation and mixed-key evaluation excluded"]
#[doc = "hb:symbol=bpy.types.Key.key_blocks"]
#[doc = "Read ordered shape-key collection by index or name"]
#[doc = "hb:symbol=bpy.types.ShapeKey.name"]
#[doc = "Read shape-key name"]
#[doc = "hb:symbol=bpy.types.ShapeKey.data"]
#[doc = "Per-vertex shape coordinates"]
#[doc = "hb:symbol=bpy.types.ShapeKeyPoint.co"]
#[doc = "Read/write finite float32 3D shape coordinate and components"]
#[doc = "hb:symbol=bmesh.types.BMesh.loops.layers.uv"]
#[doc = "Up to eight editable corner UV layers"]
#[doc = "hb:symbol=bmesh.types.BMesh.loops.layers.float_color"]
#[doc = "One editable FLOAT_COLOR corner layer"]
#[doc = "hb:symbol=bmesh.types.BMesh.verts.layers.shape"]
#[doc = "Up to 64 relative shape layers; mesh key data requires a target with shape keys"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.new"]
#[doc = "Create a named layer; UV/shape defaults zero, FLOAT_COLOR defaults white; duplicate names rejected"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.get"]
#[doc = "Find a layer by name with optional default"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.keys"]
#[doc = "Ordered layer names"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.active"]
#[doc = "Read active layer or None"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.verify"]
#[doc = "Return active layer or create a default-named layer"]
#[doc = "hb:symbol=bmesh.types.BMLayerCollection.remove"]
#[doc = "Remove this collection layer and invalidate its handle"]
#[doc = "hb:symbol=bmesh.types.BMLayerItem.name"]
#[doc = "Read layer name; reject removed/freed layer handles"]
#[doc = "hb:symbol=bmesh.types.BMFace.loops"]
#[doc = "Ordered face corners"]
#[doc = "hb:symbol=bmesh.types.BMLoop.vert"]
#[doc = "Corner vertex"]
#[doc = "hb:symbol=bmesh.types.BMLoop.edge"]
#[doc = "Corner outgoing edge"]
#[doc = "hb:symbol=bmesh.types.BMLoop.face"]
#[doc = "Owning face"]
#[doc = "hb:symbol=bmesh.types.BMLoopUV.uv"]
#[doc = "Read/write finite float32 UV pair through loop[layer].uv"]
#[test]
fn golden_m3_bmesh_data() {
    golden("compat/golden/m3_bmesh_data.py");
}

#[doc = "hb:test=compat/golden/m3_extrude_mixed.py"]
#[test]
fn golden_m3_extrude_mixed() {
    golden("compat/golden/m3_extrude_mixed.py");
}

#[doc = "hb:test=compat/golden/m3_normal_repair.py"]
#[test]
fn golden_m3_normal_repair() {
    golden("compat/golden/m3_normal_repair.py");
}

#[doc = "hb:test=compat/golden/m3_object_euler.py"]
#[doc = "hb:symbol=bpy.types.Object.rotation_euler.order"]
#[doc = "Read the object Euler order; XYZ while QUATERNION is active; change order through Object.rotation_mode"]
#[test]
fn golden_object_euler() {
    golden("compat/golden/m3_object_euler.py");
}

#[doc = "hb:test=compat/golden/m3_matrix_world.py"]
#[doc = "hb:symbol=bpy.types.Object.matrix_world"]
#[doc = "Read a 4x4 world-matrix snapshot; assign affine matrices with finite input/basis components within 1e6 through parent-inverse and TRS decomposition; six Euler orders or quaternion; nonsingular effective parent required; nested snapshot mutation does not write the object"]
#[test]
fn golden_matrix_world() {
    golden("compat/golden/m3_matrix_world.py");
}

#[doc = "hb:test=compat/golden/m3_assembly.py"]
#[test]
fn golden_assembly_extensions() {
    golden("compat/golden/m3_assembly.py");
}

#[doc = "hb:test=compat/golden/m3_primitive_extensions.py"]
#[doc = "hb:symbol=bpy.ops.object.mode_set"]
#[doc = "Transient OBJECT/EDIT primitive construction on one selected active mesh; toggle=False; return to OBJECT before object operations or script completion; combined edit construction at most 100000 vertices/faces with ordinary geometry/materials/UVs"]
#[doc = "hb:symbol=bpy.context.mode"]
#[doc = "Transient construction context: OBJECT or EDIT_MESH"]
#[doc = "hb:symbol=bpy.types.Object.mode"]
#[doc = "Read OBJECT or EDIT for the transient single edit object"]
#[doc = "hb:symbol=bpy.context.scene.cursor"]
#[doc = "Transient construction cursor; initialized at zero each script run"]
#[doc = "hb:symbol=bpy.types.View3DCursor.location"]
#[doc = "Three finite float32 cursor coordinates; default location for primitive construction"]
#[doc = "hb:symbol=bpy.types.View3DCursor.rotation_euler"]
#[doc = "Three finite XYZ cursor Euler angles; default rotation for CURSOR alignment"]
#[test]
fn golden_primitive_extensions() {
    golden("compat/golden/m3_primitive_extensions.py");
}

#[doc = "hb:test=compat/golden/m3_editmode_toggle.py"]
#[doc = "hb:symbol=bpy.ops.object.editmode_toggle"]
#[doc = "No arguments; toggle OBJECT/EDIT primitive construction on one selected active mesh, returning FINISHED; same geometry/context limits as mode_set; finish in OBJECT mode"]
#[test]
fn golden_editmode_toggle() {
    golden("compat/golden/m3_editmode_toggle.py");
}

#[doc = "hb:test=compat/golden/m3_bmesh_adjacency.py"]
#[doc = "hb:symbol=bmesh.types.BMVert.link_edges"]
#[doc = "Read-only live adjacent-edge view: iteration, length, membership, integer indexing and slices without steps; iteration order is not Blender disk-cycle order; invalidated owners raise ReferenceError"]
#[doc = "hb:symbol=bmesh.types.BMVert.link_faces"]
#[doc = "Read-only live adjacent-face view with iteration, length, membership, integer indexing and slices without steps; no Blender radial/disk ordering guarantee; invalidated owners raise ReferenceError"]
#[doc = "hb:symbol=bmesh.types.BMEdge.link_faces"]
#[doc = "Read-only live radial-face membership, including wire/boundary/nonmanifold edges; iteration, length, membership, integer indexing and slices without steps; no Blender radial ordering guarantee; invalidated owners raise ReferenceError"]
#[test]
fn golden_bmesh_adjacency() {
    golden("compat/golden/m3_bmesh_adjacency.py");
}

#[doc = "hb:test=compat/golden/m3_curves.py"]
#[doc = "hb:symbol=bpy.data.curves"]
#[doc = "Legacy Curve database distinct from meshes; iteration, integer/name lookup, get/new/remove; data persists with evaluated surface cache"]
#[doc = "hb:symbol=bpy.data.curves.new"]
#[doc = "new(name, type=CURVE or FONT); POLY/BEZIER curves require dimensions=3D; FONT is the explicitly loaded static TrueType text subset"]
#[doc = "hb:symbol=bpy.data.curves.get"]
#[doc = "get(name, default=None)"]
#[doc = "hb:symbol=bpy.data.curves.remove"]
#[doc = "Remove curve data with normal data-user unlink semantics"]
#[doc = "hb:symbol=bpy.types.Curve.name"]
#[doc = "UTF-8 datablock name, independent mesh/curve namespaces"]
#[doc = "hb:symbol=bpy.types.Curve.users"]
#[doc = "Object data-user count"]
#[doc = "hb:symbol=bpy.types.Curve.copy"]
#[doc = "Independent control data and evaluated geometry copy"]
#[doc = "hb:symbol=bpy.types.Curve.dimensions"]
#[doc = "Set 3D; 2D fill excluded"]
#[doc = "hb:symbol=bpy.types.Curve.fill_mode"]
#[doc = "FULL only"]
#[doc = "hb:symbol=bpy.types.Curve.twist_mode"]
#[doc = "MINIMUM only; spatial cyclic paths distribute residual frame twist by arc length"]
#[doc = "hb:symbol=bpy.types.Curve.bevel_mode"]
#[doc = "ROUND only"]
#[doc = "hb:symbol=bpy.types.Curve.resolution_u"]
#[doc = "Integer 1..1024; samples each curved Bezier span, leaves POLY and VECTOR spans linear"]
#[doc = "hb:symbol=bpy.types.Curve.bevel_resolution"]
#[doc = "Integer 0..8; 4+2*resolution round-profile vertices"]
#[doc = "hb:symbol=bpy.types.Curve.bevel_depth"]
#[doc = "Finite 0..100; zero depth preserves wire geometry"]
#[doc = "hb:symbol=bpy.types.Curve.extrude"]
#[doc = "Zero only; additional profile extrusion excluded"]
#[doc = "hb:symbol=bpy.types.Curve.use_fill_caps"]
#[doc = "Close open nonzero-radius beveled splines with flat end caps; cyclic splines have no end caps"]
#[doc = "hb:symbol=bpy.types.Curve.materials"]
#[doc = "Material slots: iteration, indexing, assignment, append/clear/pop"]
#[doc = "hb:symbol=bpy.types.Curve.materials.append"]
#[doc = "Append a material datablock"]
#[doc = "hb:symbol=bpy.types.Curve.materials.clear"]
#[doc = "Clear slots and reset spline material indices"]
#[doc = "hb:symbol=bpy.types.Curve.materials.pop"]
#[doc = "pop(index=-1), shifting spline material indices"]
#[doc = "hb:symbol=bpy.types.Curve.splines"]
#[doc = "At most 64 POLY/BEZIER splines; integer indexing and iteration"]
#[doc = "hb:symbol=bpy.types.Curve.splines.new"]
#[doc = "new(type=POLY or BEZIER), initially one point"]
#[doc = "hb:symbol=bpy.types.Curve.splines.clear"]
#[doc = "Remove all splines"]
#[doc = "hb:symbol=bpy.types.Spline.type"]
#[doc = "Read-only POLY or BEZIER"]
#[doc = "hb:symbol=bpy.types.Spline.use_cyclic_u"]
#[doc = "Open or cyclic; cyclic requires at least three points; spatial round bevel uses distributed closure twist"]
#[doc = "hb:symbol=bpy.types.Spline.use_smooth"]
#[doc = "Per-spline smooth face shading"]
#[doc = "hb:symbol=bpy.types.Spline.material_index"]
#[doc = "Material slot index 0..32767"]
#[doc = "hb:symbol=bpy.types.Spline.points"]
#[doc = "Indexing/iteration of at most 4096 points; at most 100000 evaluated vertices/faces per curve"]
#[doc = "hb:symbol=bpy.types.Spline.points.add"]
#[doc = "add(count), nonnegative count; assign coordinates before update or script completion"]
#[doc = "hb:symbol=bpy.types.SplinePoint.co"]
#[doc = "Live four-component coordinate; finite components within +/-10000; POLY ignores W; adjacent separation >=1e-6"]
#[doc = "hb:symbol=bpy.types.SplinePoint.radius"]
#[doc = "Finite bevel radius multiplier 0..100"]
#[doc = "hb:symbol=bpy.types.SplinePoint.tilt"]
#[doc = "Finite rotation about tangent in radians, +/-100; reversing cusps and opposite tangents excluded"]
#[test]
fn golden_curves() {
    golden("compat/golden/m3_curves.py");
}

#[doc = "hb:test=compat/golden/m3_text.py"]
#[doc = "hb:symbol=bpy.data.fonts.load"]
#[doc = "load(filepath, check_existing=False); static glyf-based TrueType <=4 MiB with Unicode cmap format 4; parsed printable ASCII outlines persist once in the scene; CFF/variable/composite glyphs excluded"]
#[doc = "hb:symbol=bpy.types.VectorFont.name"]
#[doc = "Loaded font family/style name with ordinary unique datablock suffixes; default unbundled font name Bfont"]
#[doc = "hb:symbol=bpy.types.VectorFont.users"]
#[doc = "Number of FONT curve datablocks referencing the loaded font"]
#[doc = "hb:symbol=bpy.types.TextCurve.body"]
#[doc = "At most 256 printable ASCII characters and newlines; nonempty text requires an explicitly loaded font; default Bfont rendering excluded"]
#[doc = "hb:symbol=bpy.types.TextCurve.font"]
#[doc = "Assign loaded VectorFont; geometry persists without the source font file"]
#[doc = "hb:symbol=bpy.types.TextCurve.size"]
#[doc = "Finite 0.0001..100 font size, normalized by font bounding-box height"]
#[doc = "hb:symbol=bpy.types.TextCurve.space_character"]
#[doc = "1 only; custom character spacing excluded"]
#[doc = "hb:symbol=bpy.types.TextCurve.space_word"]
#[doc = "1 only; custom word spacing excluded"]
#[doc = "hb:symbol=bpy.types.TextCurve.space_line"]
#[doc = "Finite 0..10 baseline spacing multiplier"]
#[doc = "hb:symbol=bpy.types.TextCurve.align_x"]
#[doc = "LEFT, CENTER or RIGHT using full line advance"]
#[doc = "hb:symbol=bpy.types.TextCurve.align_y"]
#[doc = "TOP_BASELINE only"]
#[doc = "hb:symbol=bpy.types.TextCurve.resolution_u"]
#[doc = "Quadratic outline sampling resolution 1..32; linear contour edges stay linear"]
#[doc = "hb:symbol=bpy.types.TextCurve.bevel_depth"]
#[doc = "0 only; text bevel excluded"]
#[doc = "hb:symbol=bpy.types.TextCurve.extrude"]
#[doc = "Finite 0..100 extrusion on each side of Z=0; total thickness 2*extrude independent of size; closed caps and hole walls; zero preserves flat geometry"]
#[doc = "hb:symbol=bpy.types.TextCurve.offset"]
#[doc = "0 only; glyph offset excluded"]
#[doc = "hb:symbol=bpy.types.TextCurve.materials"]
#[doc = "Material slots; text caps and extrusion walls use slot zero"]
#[doc = "hb:symbol=bpy.types.TextCurve.materials.append"]
#[doc = "Append a material"]
#[doc = "hb:symbol=bpy.types.TextCurve.materials.clear"]
#[doc = "Clear text material slots"]
#[doc = "hb:symbol=bpy.types.TextCurve.materials.pop"]
#[doc = "pop(index=-1), returning removed material"]
#[doc = "hb:symbol=bpy.ops.object.text_add"]
#[doc = "Object-mode Text creation; WORLD/CURSOR alignment, location/rotation and unit construction scale; assign an explicit static TrueType font before update/export/script completion; no edit lifecycle"]
#[test]
fn golden_text() {
    golden("compat/golden/m3_text.py");
}

#[doc = "hb:test=compat/meshopt_check.py"]
#[doc = "hb:symbol=hb.import.meshopt"]
#[doc = "EXT_meshopt_compression for glTF/GLB import: ATTRIBUTES/TRIANGLES/INDICES and NONE/OCTAHEDRAL/QUATERNION/EXPONENTIAL; standard 0xa0/0xe1/0xd1 streams, tagged or untagged required fallback buffers; parent/source layout validation; 32 MiB per compressed/decoded view and 64 MiB decoded total; no encoding, COLOR filter or additional geometry/animation parity"]
#[test]
fn meshopt_import_contract() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let temp = std::env::temp_dir().join(format!("hb-meshopt-contract-{}", std::process::id()));
    std::fs::create_dir_all(&temp).unwrap();
    for mode in ["triangles", "indices"] {
        let result = std::process::Command::new(env!("CARGO_BIN_EXE_hb"))
            .arg("import")
            .arg(root.join(format!("compat/fixtures/meshopt/exponential-{mode}.gltf")))
            .arg("--scene")
            .arg(temp.join(format!("{mode}.hb")))
            .output()
            .unwrap();
        assert!(
            result.status.success(),
            "{} {}",
            String::from_utf8_lossy(&result.stdout),
            String::from_utf8_lossy(&result.stderr)
        );
    }
    std::fs::remove_dir_all(temp).unwrap();
}

#[doc = "hb:test=compat/golden/m3_world_background.py"]
#[doc = "hb:symbol=bpy.types.World.node_tree"]
#[doc = "Persistent Background color/strength and one EQUIRECTANGULAR/Linear Environment Texture; existing World Output wiring. Preview uses constant illumination and the environment solid-angle mean; no directional environment shading."]
#[doc = "hb:symbol=bpy.types.World.node_tree.nodes"]
#[doc = "Named World node lookup, iteration and length"]
#[doc = "hb:symbol=bpy.types.World.node_tree.nodes.get"]
#[doc = "Look up a World node by name"]
#[doc = "hb:symbol=bpy.types.World.node_tree.nodes.new"]
#[doc = "One each: ShaderNodeBackground, ShaderNodeOutputWorld, ShaderNodeTexEnvironment; other World nodes raise UnsupportedError"]
#[doc = "hb:symbol=bpy.types.World.node_tree.nodes.clear"]
#[doc = "Clear World nodes and links"]
#[doc = "hb:symbol=bpy.types.World.node_tree.links.new"]
#[doc = "Environment Color to Background Color; Background to World Output Surface; replaces the input's prior link"]
#[doc = "hb:symbol=bpy.types.World.copy"]
#[doc = "Copy persistent World color, nodes and links; image datablocks remain shared"]
#[doc = "hb:symbol=bpy.types.ShaderNode.projection"]
#[doc = "Environment Texture EQUIRECTANGULAR or Image Texture FLAT only"]
#[doc = "hb:symbol=bpy.types.ShaderNode.interpolation"]
#[doc = "Image and Environment Texture: Linear only"]
#[test]
fn golden_world_background() {
    golden("compat/golden/m3_world_background.py");
}

#[doc = "hb:test=compat/golden/m3_materials.py"]
#[doc = "hb:symbol=bpy.types.NodeSocket.default_value"]
#[doc = "Named Blender 4.5 default-mode Principled scalar/color/radius inputs, including IOR and Transmission Weight: float32 storage, unclamped scalar values, nonnegative RGBA colors. Normal/Tangent/Coat Normal are read-only; hidden Weight/Subsurface IOR excluded. Background color/strength, planar Mapping Location/Rotation/Scale and existing Normal Map strength. Extra scattering inputs persist in hb/glTF extras; fixed preview shading is unchanged."]
#[doc = "hb:symbol=bpy.types.ShaderNode.vector_type"]
#[doc = "Mapping POINT only; one UV chain with XY location/scale and Z rotation, scale Z=1"]
#[doc = "hb:symbol=bpy.types.ShaderNode.object"]
#[doc = "Texture Coordinate read-only default None; object coordinates are outside the UV chain"]
#[doc = "hb:symbol=bpy.types.ShaderNode.from_instancer"]
#[doc = "Texture Coordinate read-only default False"]
#[test]
fn golden_materials() {
    golden("compat/golden/m3_materials.py");
}

#[doc = "hb:test=compat/golden/m3_mathutils.py"]
#[doc = "hb:symbol=mathutils.Matrix"]
#[doc = "Float32 storage with 2..4 rows and 2..4 columns; row read/write, copies, resizing and dimension-compatible Matrix/Vector multiplication. 2x4 @ 3D is excluded (undefined Blender result): use a four-component vector. Nonsquare determinant/inversion/transpose raise ValueError."]
#[doc = "hb:symbol=mathutils.Matrix.decompose"]
#[doc = "4x4 finite components up to magnitude 1e6: location Vector, quaternion and signed scale Vector, including shears, reflections and zero-scale columns. Blender column normalization and quaternion pivot semantics; 2e-6 differential tolerance."]
#[doc = "hb:symbol=mathutils.Quaternion.slerp"]
#[doc = "Quaternion and factor in [0,1]; finite components up to magnitude 1e6. Blender shortest-arc sign convention, no implicit operand/result normalization; zero and nonunit inputs tested."]
#[test]
fn golden_mathutils_lane2() {
    golden("compat/golden/m3_mathutils.py");
}

#[doc = "hb:test=compat/golden/m3_texture_assets.py"]
#[doc = "hb:symbol=bpy.types.ShaderNode.extension"]
#[doc = "Image Texture REPEAT, EXTEND (clamp) and MIRROR; preserved in glTF samplers. CLIP excluded. Advanced texture bindings are asset-only: fixed preview/OBJ/USDZ reject them with a glTF export suggestion."]
#[doc = "hb:symbol=bpy.types.MeshUVLoopLayer.active_render"]
#[doc = "Render UV selection distinct from active editing layer; assigning True selects the layer, False does not unset it. Texture glTF exports use channels 0..7; shared materials with differing render channels require duplication."]
#[test]
fn golden_texture_assets() {
    golden("compat/golden/m3_texture_assets.py");
}

#[doc = "hb:test=compat/golden/modeling_quality_curves.py"]
#[doc = "hb:symbol=bpy.types.Spline.bezier_points"]
#[doc = "BEZIER control points; indexing/iteration, at most 4096 points"]
#[doc = "hb:symbol=bpy.types.Spline.bezier_points.add"]
#[doc = "add(count); nonnegative control-point count"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.co"]
#[doc = "Live three-component coordinate within +/-10000; moving the control point translates both stored handles"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.handle_left"]
#[doc = "Live left handle coordinate within +/-10000; FREE/ALIGNED handles are explicit"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.handle_right"]
#[doc = "Live right handle coordinate within +/-10000; FREE/ALIGNED handles are explicit"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.handle_left_type"]
#[doc = "FREE, VECTOR, AUTO or ALIGNED; ordinary 3D AUTO uses the neighbor chord bisector and Blender length convention, reference-tested on corner and unequal-spacing cases"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.handle_right_type"]
#[doc = "FREE, VECTOR, AUTO or ALIGNED; moving a handle aligns its opposite ALIGNED handle unless either handle is FREE"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.radius"]
#[doc = "Radius multiplier 0..100, linearly interpolated along each span"]
#[doc = "hb:symbol=bpy.types.BezierSplinePoint.tilt"]
#[doc = "Tilt radians +/-100, linearly interpolated along each span"]
#[test]
fn golden_quality_curves() {
    golden("compat/golden/modeling_quality_curves.py");
}

#[doc = "hb:test=compat/golden/modeling_quality_bevel.py"]
#[test]
fn golden_quality_bevel() {
    golden("compat/golden/modeling_quality_bevel.py");
}

#[doc = "hb:test=compat/golden/modeling_quality_text.py"]
#[test]
fn golden_quality_text() {
    golden("compat/golden/modeling_quality_text.py");
}
