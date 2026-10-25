import bpy
import bmesh
import math
from mathutils import Vector

# --- Museum display case ------------------------------------------------
# Tapered stone pedestal carrying a framed glass vitrine over a ceramic vase.

CASE_Z0 = 1.09      # glass starts here (top of the base rail)
CASE_Z1 = 1.94      # glass ends here
HALF = 0.46         # glass footprint half-width


def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def set_input(bsdf, names, value):
    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def material(name, color, roughness=0.5, metallic=0.0, glass=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    set_input(bsdf, ["Base Color"], (*color, 1.0))
    set_input(bsdf, ["Roughness"], roughness)
    set_input(bsdf, ["Metallic"], metallic)
    if glass:
        set_input(bsdf, ["Transmission Weight", "Transmission"], 1.0)
        set_input(bsdf, ["IOR"], 1.45)
        set_input(bsdf, ["Alpha"], 0.2)
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        mat.diffuse_color = (*color, 0.2)
    else:
        mat.diffuse_color = (*color, 1.0)
    return mat


def finish(name, bm, mat, location=(0, 0, 0), rotation=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def box(name, size, location, mat, rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return finish(name, bm, mat, location, rotation)


def tapered_column(name, mat, half_low, half_high, z0, z1):
    bm = bmesh.new()
    low = [bm.verts.new(v) for v in ((-half_low, -half_low, z0), (half_low, -half_low, z0),
                                     (half_low, half_low, z0), (-half_low, half_low, z0))]
    high = [bm.verts.new(v) for v in ((-half_high, -half_high, z1), (half_high, -half_high, z1),
                                      (half_high, half_high, z1), (-half_high, half_high, z1))]
    bm.faces.new(low)
    bm.faces.new(high)
    for i in range(4):
        bm.faces.new((low[i], low[(i + 1) % 4], high[(i + 1) % 4], high[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, mat)


def lathe(name, profile, mat, location, steps=40):
    """Revolve a 2D (radius, height) profile around Z."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, axis=(0.0, 0.0, 1.0), cent=(0.0, 0.0, 0.0),
                   dvec=(0.0, 0.0, 0.0), angle=2.0 * math.pi, steps=steps, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, mat, location, smooth=True)


def add_light(name, kind, energy, location, rotation=(0, 0, 0), size=2.0, spot_size=0.8):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    if kind == 'AREA':
        data.size = size
    elif kind == 'SPOT':
        data.spot_size = spot_size
        data.spot_blend = 0.35
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


def add_camera(location, target):
    data = bpy.data.cameras.new("Camera")
    data.lens = 45.0
    cam = bpy.data.objects.new("Camera", data)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()

stone = material("MAT_PedestalStone", (0.82, 0.80, 0.76), roughness=0.55)
plinth_mat = material("MAT_PedestalPlinth", (0.24, 0.23, 0.22), roughness=0.6)
steel = material("MAT_CaseFrameSteel", (0.58, 0.59, 0.61), roughness=0.3, metallic=1.0)
glass = material("MAT_VitrineGlass", (0.85, 0.90, 0.90), roughness=0.03, glass=True)
ceramic = material("MAT_ArtifactCeramic", (0.72, 0.36, 0.19), roughness=0.34)
felt = material("MAT_RiserFelt", (0.10, 0.09, 0.13), roughness=0.9)
plaque_mat = material("MAT_LabelPlaque", (0.74, 0.60, 0.28), roughness=0.35, metallic=1.0)
floor_mat = material("MAT_GalleryFloor", (0.36, 0.34, 0.32), roughness=0.5)
wall_mat = material("MAT_GalleryWall", (0.70, 0.69, 0.67), roughness=0.85)

box("Gallery_Floor", (9.0, 9.0, 0.08), (0.0, 0.0, -0.04), floor_mat)
box("Gallery_WallBack", (9.0, 0.12, 3.4), (0.0, 2.6, 1.7), wall_mat)

# Pedestal
box("Pedestal_Plinth", (1.14, 1.14, 0.08), (0.0, 0.0, 0.04), plinth_mat)
tapered_column("Pedestal_Column", stone, 0.50, 0.43, 0.08, 0.98)
box("Pedestal_Cap", (1.06, 1.06, 0.06), (0.0, 0.0, 1.01), stone)

# Vitrine frame
box("Case_BaseRail", (0.99, 0.99, 0.05), (0.0, 0.0, 1.065), steel)
box("Case_TopRail", (0.99, 0.99, 0.05), (0.0, 0.0, 1.975), steel)
mid_z = 0.5 * (CASE_Z0 + CASE_Z1)
height = CASE_Z1 - CASE_Z0
for sx in (-1, 1):
    for sy in (-1, 1):
        box("Case_CornerPost_%s%s" % ("XP" if sx > 0 else "XN", "YP" if sy > 0 else "YN"),
            (0.035, 0.035, height), (sx * HALF, sy * HALF, mid_z), steel)

# Glass panes
pane_w = 2.0 * HALF - 0.05
box("Glass_PaneFront", (pane_w, 0.012, height), (0.0, -HALF, mid_z), glass)
box("Glass_PaneBack", (pane_w, 0.012, height), (0.0, HALF, mid_z), glass)
box("Glass_PaneLeft", (0.012, pane_w, height), (-HALF, 0.0, mid_z), glass)
box("Glass_PaneRight", (0.012, pane_w, height), (HALF, 0.0, mid_z), glass)
box("Glass_PaneTop", (pane_w, pane_w, 0.012), (0.0, 0.0, CASE_Z1 + 0.006), glass)

# Artifact on its riser
box("Artifact_Riser", (0.32, 0.32, 0.06), (0.0, 0.0, 1.12), felt)
vase_profile = [
    (0.000, 0.00), (0.095, 0.00), (0.108, 0.03), (0.125, 0.11), (0.152, 0.21),
    (0.148, 0.29), (0.118, 0.37), (0.086, 0.43), (0.078, 0.48), (0.092, 0.52),
    (0.084, 0.525),
]
lathe("Artifact_AmphoraVase", vase_profile, ceramic, (0.0, 0.0, 1.15))
for sign, ang in ((-1, 0.0), (1, 0.0)):
    box("Artifact_Handle_%s" % ("L" if sign < 0 else "R"),
        (0.022, 0.022, 0.13), (sign * 0.115, 0.0, 1.55), ceramic,
        rotation=(ang, sign * math.radians(28.0), 0.0))

# Interpretive label on the pedestal face
box("Label_Plaque", (0.36, 0.20, 0.012), (0.0, -0.505, 0.78), plaque_mat,
    rotation=(math.radians(-72.0), 0.0, 0.0))

add_light("Vitrine_Spot", 'SPOT', 900.0, (0.6, -1.0, 3.3),
          rotation=(math.radians(28.0), 0.0, math.radians(30.0)), spot_size=math.radians(48.0))
add_light("Gallery_Fill", 'AREA', 200.0, (-2.2, -2.0, 2.8),
          rotation=(math.radians(52.0), 0.0, math.radians(-45.0)), size=3.5)
add_light("Gallery_Ambient", 'SUN', 1.1, (0.0, -3.0, 4.0),
          rotation=(math.radians(50.0), 0.0, math.radians(15.0)))

add_camera((2.15, -2.75, 2.05), (0.0, 0.0, 1.35))
