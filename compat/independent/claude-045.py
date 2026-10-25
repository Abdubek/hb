"""L-shaped staircase with landing and handrails (Blender 4.5 LTS)."""
import bpy
from mathutils import Vector

RISE, RUN, WIDTH = 0.18, 0.28, 1.2
STEPS = 8
HALF = WIDTH * 0.5
LANDING_Z = STEPS * RISE
LANDING_Y0 = STEPS * RUN
RAIL_H = 0.95


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, center, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, p0, p1, radius, mat, verts=12):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length,
                                        location=(p0 + p1) * 0.5)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(mat)
    return ob


def build_flight(prefix, origin, direction, mat_tread, mat_riser):
    """Steps marching from `origin` along horizontal unit vector `direction`."""
    o = Vector(origin)
    d = Vector(direction)
    side = Vector((d.y, d.x, 0.0))  # perpendicular in plan
    for i in range(STEPS):
        z = o.z + (i + 1) * RISE
        c = o + d * ((i + 0.5) * RUN)
        tsize = (abs(d.x) * RUN + abs(side.x) * WIDTH + 0.02,
                 abs(d.y) * RUN + abs(side.y) * WIDTH + 0.02, 0.05)
        add_box("%s_Tread_%02d" % (prefix, i + 1), tsize, (c.x, c.y, z - 0.025), mat_tread)
        rc = o + d * (i * RUN)
        rsize = (abs(d.x) * 0.04 + abs(side.x) * WIDTH,
                 abs(d.y) * 0.04 + abs(side.y) * WIDTH, RISE)
        add_box("%s_Riser_%02d" % (prefix, i + 1), rsize,
                (rc.x + d.x * 0.02, rc.y + d.y * 0.02, z - RISE * 0.5), mat_riser)


def build_railing(prefix, points, mat_rail, mat_post, spacing=0.85):
    """Balusters along a polyline plus a continuous top rail above it."""
    pts = [Vector(p) for p in points]
    n_post = 0
    for a, b in zip(pts, pts[1:]):
        seg = b - a
        count = max(1, int(round(seg.length / spacing)))
        for k in range(count):
            base = a + seg * (k / count)
            n_post += 1
            add_cylinder("%s_Post_%02d" % (prefix, n_post), base,
                         base + Vector((0, 0, RAIL_H)), 0.022, mat_post)
        add_cylinder("%s_Rail_%02d" % (prefix, len(pts)),
                     a + Vector((0, 0, RAIL_H)), b + Vector((0, 0, RAIL_H)), 0.04, mat_rail)
    last = pts[-1]
    add_cylinder("%s_Post_End" % prefix, last, last + Vector((0, 0, RAIL_H)), 0.03, mat_post)


def add_camera(location, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 35
    bpy.context.scene.camera = cam


def main():
    clear_scene()
    tread_mat = make_material("OakTread", (0.55, 0.36, 0.19), roughness=0.45)
    riser_mat = make_material("PaintedRiser", (0.90, 0.89, 0.86), roughness=0.6)
    slab_mat = make_material("ConcreteSlab", (0.62, 0.61, 0.59), roughness=0.85)
    steel_mat = make_material("BrushedSteel", (0.72, 0.73, 0.75), roughness=0.3, metallic=1.0)
    rail_mat = make_material("WalnutHandrail", (0.30, 0.18, 0.10), roughness=0.35)

    add_box("GroundSlab", (7.0, 8.0, 0.2), (1.6, 2.2, -0.1), slab_mat)

    build_flight("LowerFlight", (0, 0, 0), (0, 1, 0), tread_mat, riser_mat)

    landing_c = (0.0, LANDING_Y0 + WIDTH * 0.5, LANDING_Z - 0.03)
    add_box("Landing_Deck", (WIDTH + 0.04, WIDTH, 0.06), landing_c, tread_mat)
    add_box("Landing_Apron", (WIDTH + 0.04, WIDTH, 0.14),
            (landing_c[0], landing_c[1], LANDING_Z - 0.13), riser_mat)
    for sx in (-1, 1):
        add_box("Landing_Column_%s" % ("E" if sx > 0 else "W"), (0.14, 0.14, LANDING_Z - 0.2),
                (sx * (HALF - 0.07), LANDING_Y0 + WIDTH - 0.07, (LANDING_Z - 0.2) * 0.5), steel_mat)

    upper_origin = (HALF, LANDING_Y0 + WIDTH * 0.5, LANDING_Z)
    build_flight("UpperFlight", upper_origin, (1, 0, 0), tread_mat, riser_mat)

    top_z = LANDING_Z + STEPS * RISE
    top_x = HALF + STEPS * RUN
    add_box("UpperFloor", (1.6, 3.0, 0.22), (top_x + 0.8, LANDING_Y0 + WIDTH * 0.5, top_z - 0.11),
            slab_mat)

    # Stringers under both flights
    for sx in (-1, 1):
        st = add_box("LowerStringer_%s" % ("E" if sx > 0 else "W"),
                     (0.06, STEPS * RUN * 1.06, 0.28),
                     (sx * HALF, LANDING_Y0 * 0.5, LANDING_Z * 0.5 - 0.12), slab_mat)
        st.rotation_euler = (-1.0 * (RISE / RUN) ** 0.0 * 0.0, 0, 0)
        st.rotation_euler.x = -0.0 - (RISE and __import__("math").atan2(LANDING_Z, LANDING_Y0))

    # Continuous outer handrail: up the lower flight, across the landing, up the upper flight
    outer = [(-HALF, 0.0, RISE),
             (-HALF, LANDING_Y0, LANDING_Z),
             (-HALF, LANDING_Y0 + WIDTH, LANDING_Z),
             (HALF, LANDING_Y0 + WIDTH, LANDING_Z),
             (top_x, LANDING_Y0 + WIDTH, top_z)]
    build_railing("OuterRailing", outer, rail_mat, steel_mat)

    inner = [(HALF, 0.0, RISE),
             (HALF, LANDING_Y0, LANDING_Z),
             (top_x, LANDING_Y0, top_z)]
    build_railing("InnerRailing", inner, rail_mat, steel_mat)

    key = bpy.data.objects.new("KeyLight", bpy.data.lights.new("KeyLight", 'AREA'))
    bpy.context.collection.objects.link(key)
    key.data.energy = 900.0
    key.data.size = 4.0
    key.location = (5.0, -3.0, 6.0)
    key.rotation_euler = (0.9, 0.2, 0.9)

    fill = bpy.data.objects.new("FillSun", bpy.data.lights.new("FillSun", 'SUN'))
    bpy.context.collection.objects.link(fill)
    fill.data.energy = 1.5
    fill.rotation_euler = (1.0, 0.0, -1.2)

    add_camera((7.5, -6.0, 5.0), (1.2, 2.0, 1.3))


main()
