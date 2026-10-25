import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def link(obj, material):
    obj.data.materials.append(material)
    return obj


def mesh_from_bmesh(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    return obj


def build_hull(name, length=5.0, beam=1.5, depth=0.85, sections=9, profile_steps=9):
    """Loft half-elliptical cross sections along the keel line into a closed hull."""
    bm = bmesh.new()
    rings = []
    for si in range(sections):
        t = si / (sections - 1)                       # 0 = stern, 1 = bow
        x = -length * 0.5 + t * length
        taper = math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.7   # fine bow, fuller stern
        half_beam = beam * 0.5 * taper
        sec_depth = depth * (0.55 + 0.45 * math.sin(math.pi * (0.15 + 0.85 * t)))
        ring = []
        for pi in range(profile_steps):
            a = -math.pi * 0.5 + math.pi * pi / (profile_steps - 1)
            y = half_beam * math.sin(a)
            z = -sec_depth * math.cos(a) ** 1.4
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    bm.verts.index_update()
    for si in range(sections - 1):
        a, b = rings[si], rings[si + 1]
        for pi in range(profile_steps - 1):
            bm.faces.new((a[pi], a[pi + 1], b[pi + 1], b[pi]))
        bm.faces.new((a[0], b[0], b[-1], a[-1]))       # deck strip (z = 0)
    bm.faces.new(list(reversed(rings[0])))             # transom
    bm.faces.new(list(rings[-1]))                      # stem cap
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bmesh(name, bm)


def add_box(name, center, size, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    return obj


def add_cylinder(name, center, radius, height, rotation=(0.0, 0.0, 0.0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=height,
                                        location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_triangle_sail(name, p0, p1, p2, belly=0.22):
    """Flat triangle nudged sideways at its centre so the sail reads as drawing wind."""
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in (p0, p1, p2)]
    bm.faces.new(verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    center = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    for v in bm.verts:
        edge_dist = min((v.co - Vector(p)).length for p in (p0, p1, p2))
        v.co.y += belly * min(1.0, edge_dist / 1.2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = mesh_from_bmesh(name, bm)
    solid = obj.modifiers.new("Cloth Thickness", 'SOLIDIFY')
    solid.thickness = 0.02
    return obj


def add_camera(location, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.data.lens = 45.0
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

m_hull = make_material("Hull_Paint", (0.05, 0.16, 0.34), roughness=0.25)
m_deck = make_material("Deck_Teak", (0.52, 0.34, 0.16), roughness=0.6)
m_spar = make_material("Spar_Alu", (0.72, 0.73, 0.75), roughness=0.35, metallic=0.9)
m_sail = make_material("Sail_Canvas", (0.92, 0.91, 0.86), roughness=0.8)
m_trim = make_material("Trim_Dark", (0.08, 0.08, 0.09), roughness=0.45)
m_water = make_material("Water", (0.03, 0.12, 0.15), roughness=0.15)

LENGTH, BEAM, DEPTH = 5.0, 1.5, 0.85
link(build_hull("Hull", LENGTH, BEAM, DEPTH), m_hull)

link(add_box("Deck", (0.1, 0.0, 0.01), (LENGTH * 0.94, BEAM * 0.92, 0.04)), m_deck)
link(add_box("Cockpit_Coaming", (-1.15, 0.0, 0.09), (1.5, 0.95, 0.14)), m_trim)
link(add_box("Cabin_Trunk", (0.75, 0.0, 0.16), (1.7, 0.8, 0.30)), m_deck)
link(add_box("Cabin_Roof", (0.75, 0.0, 0.32), (1.8, 0.88, 0.05)), m_trim)
link(add_box("Keel_Fin", (-0.15, 0.0, -1.25), (1.2, 0.14, 0.95)), m_trim)
link(add_box("Ballast_Shoe", (-0.15, 0.0, -1.74), (1.05, 0.24, 0.14)), m_trim)
link(add_box("Rudder_Blade", (-2.45, 0.0, -0.75), (0.26, 0.07, 1.15)), m_trim)
link(add_cylinder("Tiller", (-2.05, 0.0, 0.22), 0.035, 0.9,
                  rotation=(0.0, math.radians(80.0), 0.0)), m_deck)

MAST_H = 6.2
MAST_X = 0.35
link(add_cylinder("Mast", (MAST_X, 0.0, MAST_H * 0.5 - 0.1), 0.075, MAST_H), m_spar)
link(add_cylinder("Boom", (MAST_X - 1.35, 0.0, 0.72), 0.055, 2.6,
                  rotation=(0.0, math.radians(90.0), 0.0)), m_spar)
link(add_cylinder("Gooseneck", (MAST_X - 0.06, 0.0, 0.72), 0.09, 0.16,
                  rotation=(math.radians(90.0), 0.0, 0.0)), m_trim)
link(add_cylinder("Boom_Vang", (MAST_X - 0.75, 0.0, 0.44), 0.02, 0.75,
                  rotation=(0.0, math.radians(55.0), 0.0)), m_trim)

main_head = (MAST_X - 0.08, 0.0, MAST_H - 0.35)
main_tack = (MAST_X - 0.08, 0.0, 0.82)
main_clew = (MAST_X - 2.55, 0.0, 0.86)
link(add_triangle_sail("Mainsail", main_head, main_tack, main_clew, belly=0.30), m_sail)

jib_head = (MAST_X + 0.02, 0.0, MAST_H - 1.55)
jib_tack = (LENGTH * 0.5 - 0.35, 0.0, 0.12)
jib_clew = (MAST_X + 0.55, 0.0, 0.70)
link(add_triangle_sail("Jib", jib_head, jib_tack, jib_clew, belly=0.20), m_sail)
link(add_cylinder("Forestay", ((jib_head[0] + jib_tack[0]) * 0.5, 0.0,
                               (jib_head[2] + jib_tack[2]) * 0.5), 0.012,
                  (Vector(jib_head) - Vector(jib_tack)).length,
                  rotation=(0.0, math.atan2(jib_tack[0] - jib_head[0],
                                            jib_head[2] - jib_tack[2]), 0.0)), m_trim)

for i, side in enumerate((-1, 1)):
    top = Vector((MAST_X, 0.0, MAST_H - 0.8))
    base = Vector((MAST_X - 0.3, side * BEAM * 0.44, 0.05))
    d = base - top
    link(add_cylinder("Shroud_%d" % (i + 1), tuple((top + base) * 0.5), 0.012, d.length,
                      rotation=d.to_track_quat('Z', 'Y').to_euler(), verts=8), m_trim)

link(add_box("Water_Surface", (0.0, 0.0, -0.02), (26.0, 26.0, 0.02)), m_water)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
bpy.context.collection.objects.link(sun)
sun.data.energy = 4.0
sun.location = (6.0, -8.0, 12.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(35.0))

add_camera((9.5, -11.0, 5.2), (0.0, 0.0, 2.2))
