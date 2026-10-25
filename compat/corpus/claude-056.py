"""claude-056 : A simple sailboat with hull, mast and boom."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    scn.render.resolution_x, scn.render.resolution_y = 1600, 1000


def mat(name, color, rough=0.5, metal=0.0, emis=None, estr=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if emis is not None:
        if "Emission Color" in i:
            i["Emission Color"].default_value = (*emis, 1.0)
        i["Emission Strength"].default_value = estr
    if alpha < 1.0:
        i["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = 'BLENDED'
    return m


def finish(ob, material=None, bevel=0.0, seg=2, smooth=False):
    if material:
        ob.data.materials.append(material)
    if bevel > 0.0:
        b = ob.modifiers.new("Bevel", 'BEVEL')
        b.width, b.segments = bevel, seg
        b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(50)
    if smooth:
        shade_smooth(ob)
    return ob


def shade_smooth(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        bpy.ops.object.shade_smooth()


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = name
    ob.data.transform(Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, bevel)


def add_cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), verts=24, material=None,
            r2=None, smooth=True):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d)
    ob = bpy.context.object
    ob.name = name
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, smooth=smooth)


def add_rod(name, p0, p1, r, material=None, verts=12):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    ob = add_cyl(name, r, max(d.length, 1e-5), tuple((p0 + p1) * 0.5),
                 verts=verts, material=material)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def obj_from_bm(name, bm, material=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return finish(ob, material, smooth=smooth)


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
reset_scene()

M_HULL_TOP = mat("HullTopsides", (0.92, 0.92, 0.90), 0.22)
M_HULL_BOT = mat("HullBottom", (0.09, 0.20, 0.38), 0.35)
M_DECK = mat("Teak", (0.52, 0.33, 0.16), 0.55)
M_WOOD = mat("Varnish", (0.42, 0.24, 0.10), 0.28)
M_ALU = mat("Aluminium", (0.72, 0.73, 0.75), 0.28, 1.0)
M_STEEL = mat("Steel", (0.62, 0.63, 0.66), 0.20, 1.0)
M_SAIL = mat("SailCloth", (0.95, 0.94, 0.90), 0.72)
M_ROPE = mat("Rope", (0.30, 0.27, 0.22), 0.85)
M_RED = mat("Boot", (0.55, 0.10, 0.10), 0.35)
M_WATER = mat("Water", (0.02, 0.10, 0.16), 0.06)
M_WATER.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.33

L, B, D = 6.2, 1.10, 0.78
WATERLINE = -0.34

# ------------------------------------------------------------------ hull loft
# (u along length, half beam factor, depth factor, sheer height)
STATIONS = [
    (0.00, 0.60, 0.62, 0.09), (0.07, 0.76, 0.76, 0.065),
    (0.18, 0.91, 0.90, 0.035), (0.30, 0.99, 0.96, 0.015),
    (0.44, 1.00, 1.00, 0.02), (0.56, 0.97, 0.99, 0.045),
    (0.68, 0.88, 0.94, 0.085), (0.78, 0.75, 0.87, 0.14),
    (0.86, 0.60, 0.79, 0.20), (0.92, 0.44, 0.70, 0.26),
    (0.97, 0.24, 0.59, 0.32), (1.00, 0.05, 0.46, 0.36),
]
NSEC = 14


def section(u, hb, dp, sheer):
    x = -L * 0.5 + u * L
    pts = []
    for i in range(NSEC + 1):
        a = (-1.0 + 2.0 * i / NSEC) * math.pi * 0.5
        y = hb * B * math.sin(a)
        z = sheer - dp * D * (math.cos(a) ** 1.35)
        pts.append(Vector((x, y, z)))
    return pts


bm = bmesh.new()
rings = [[bm.verts.new(p) for p in section(*st)] for st in STATIONS]
for r0, r1 in zip(rings, rings[1:]):
    for i in range(NSEC):
        bm.faces.new((r0[i], r0[i + 1], r1[i + 1], r1[i]))
    # deck / sheer strake closing face
    bm.faces.new((r0[-1], r1[-1], r1[0], r0[0]))
bm.faces.new(tuple(rings[0]))          # transom
bm.faces.new(tuple(reversed(rings[-1])))  # stem cap
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.012, segments=2,
                affect='EDGES', profile=0.5)
hull = obj_from_bm("Hull", bm, M_HULL_TOP, smooth=True)
hull.data.materials.append(M_HULL_BOT)
hull.data.materials.append(M_RED)
for poly in hull.data.polygons:
    z = poly.center.z
    if z < WATERLINE - 0.05:
        poly.material_index = 1
    elif z < WATERLINE + 0.04:
        poly.material_index = 2

# deck planking laid slightly proud of the sheer
bm = bmesh.new()
drings = []
for u, hb, dp, sheer in STATIONS:
    x = -L * 0.5 + u * L
    y = hb * B * 0.985
    drings.append((bm.verts.new((x, -y, sheer + 0.012)),
                   bm.verts.new((x, y, sheer + 0.012))))
for (a0, b0), (a1, b1) in zip(drings, drings[1:]):
    bm.faces.new((a0, b0, b1, a1))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
obj_from_bm("Deck", bm, M_DECK)

# ------------------------------------------------------------------ appendages
add_box("KeelFin", (1.5, 0.11, 1.05), (-0.15, 0.0, -1.10), material=M_HULL_BOT,
        bevel=0.03)
bulb = add_cyl("KeelBulb", 0.15, 1.30, (-0.15, 0, -1.62), (0, math.pi / 2, 0),
               verts=20, material=M_STEEL)
bulb.scale = (1.0, 0.72, 1.0)
add_box("Rudder", (0.34, 0.06, 0.90), (-2.72, 0.0, -0.72), (0, math.radians(8), 0),
        material=M_HULL_BOT, bevel=0.02)
add_rod("RudderStock", (-2.62, 0, -0.30), (-2.55, 0, 0.30), 0.030, M_STEEL)
tiller = add_rod("Tiller", (-2.56, 0, 0.30), (-1.75, 0, 0.46), 0.026, M_WOOD)

# cabin trunk, hatch and cockpit
cabin = add_box("CabinTrunk", (1.85, 0.98, 0.34), (0.95, 0.0, 0.24),
                material=M_HULL_TOP, bevel=0.05)
add_box("CabinRoof", (1.90, 1.02, 0.05), (0.95, 0.0, 0.43), material=M_DECK,
        bevel=0.02)
for sgn in (-1, 1):
    add_box("Portlight", (0.52, 0.02, 0.13), (1.05, sgn * 0.50, 0.27),
            material=mat("Glass", (0.05, 0.10, 0.13), 0.08, 0.2))
add_box("Hatch", (0.42, 0.42, 0.06), (1.72, 0.0, 0.46), material=M_ALU, bevel=0.02)
add_box("CockpitSole", (1.55, 0.80, 0.05), (-1.35, 0.0, -0.10), material=M_DECK)
for sgn in (-1, 1):
    add_box("Coaming", (1.60, 0.06, 0.22), (-1.35, sgn * 0.44, 0.14),
            material=M_HULL_TOP, bevel=0.02)
    add_box("Bench", (1.45, 0.30, 0.05), (-1.35, sgn * 0.30, 0.04), material=M_DECK)
add_box("CockpitBulkhead", (0.06, 0.90, 0.30), (-0.58, 0.0, 0.16),
        material=M_HULL_TOP, bevel=0.02)

# ------------------------------------------------------------------ rig
MAST_BASE = Vector((0.70, 0.0, 0.44))
MAST_TOP = Vector((0.46, 0.0, 5.30))
BOOM_FWD = Vector((0.70, 0.0, 1.28))
BOOM_AFT = Vector((-1.95, 0.0, 1.42))

mast = add_rod("Mast", MAST_BASE, MAST_TOP, 0.058, M_ALU, verts=16)
mast.scale = (1.0, 0.72, 1.0)
add_rod("Boom", BOOM_FWD, BOOM_AFT, 0.046, M_ALU, verts=14)
add_rod("Gooseneck", (0.70, 0, 1.24), (0.70, 0, 1.34), 0.055, M_STEEL)
add_cyl("MastStep", 0.10, 0.06, (0.70, 0, 0.46), material=M_STEEL, verts=16)
add_cyl("Masthead", 0.075, 0.10, tuple(MAST_TOP + Vector((0, 0, 0.05))),
        material=M_STEEL, verts=16)
add_rod("WindVane", (0.46, 0, 5.38), (0.46, 0, 5.60), 0.008, M_STEEL, verts=6)
add_box("VaneFin", (0.10, 0.005, 0.07), (0.40, 0, 5.56), material=M_STEEL)

# standing rigging
CHAIN = [Vector((0.72, s * 1.02, 0.10)) for s in (-1, 1)]
for k, cp in enumerate(CHAIN):
    add_rod("Shroud%d" % k, cp, MAST_TOP + Vector((0, 0, -0.35)), 0.010, M_STEEL, 6)
    add_rod("LowerShroud%d" % k, cp + Vector((-0.35, 0, 0)),
            Vector((0.55, 0, 2.90)), 0.009, M_STEEL, 6)
BOW = Vector((2.92, 0.0, 0.52))
STERN = Vector((-3.02, 0.0, 0.18))
add_rod("Forestay", BOW, MAST_TOP, 0.010, M_STEEL, 6)
add_rod("Backstay", STERN, MAST_TOP, 0.010, M_STEEL, 6)
add_rod("BoomVang", (0.72, 0, 0.50), (0.05, 0, 1.34), 0.020, M_STEEL, 8)
add_rod("Mainsheet", tuple(BOOM_AFT + Vector((0.1, 0, -0.04))), (-1.55, 0, -0.06),
        0.010, M_ROPE, 6)


# ------------------------------------------------------------------ sails
def make_sail(name, tack, head, clew, camber=0.16, roach=0.14, nu=12, nv=14):
    tack, head, clew = Vector(tack), Vector(head), Vector(clew)
    leech = head - clew
    perp = Vector((leech.z, 0.0, -leech.x)).normalized()
    if perp.dot(clew - tack) < 0.0:
        perp = -perp
    bm = bmesh.new()
    rows = []
    for i in range(nv):
        t = i / nv
        a = tack.lerp(head, t)
        b = clew.lerp(head, t) + perp * (roach * math.sin(math.pi * t) * (1.0 - t))
        row = []
        for j in range(nu + 1):
            s = j / nu
            p = a.lerp(b, s)
            p.y += camber * math.sin(math.pi * s) * math.sin(math.pi * min(t + 0.12, 1.0)) \
                * (1.0 - 0.30 * t)
            row.append(bm.verts.new(p))
        rows.append(row)
    apex = bm.verts.new(head)
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(nu):
            bm.faces.new((r0[j], r0[j + 1], r1[j + 1], r1[j]))
    for j in range(nu):
        bm.faces.new((rows[-1][j], rows[-1][j + 1], apex))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm(name, bm, M_SAIL, smooth=True)
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.008
    sol.offset = 0.0
    return ob


make_sail("Mainsail",
          (0.74, 0.0, 1.40), (0.50, 0.0, 5.12), (-1.88, 0.0, 1.50),
          camber=0.20, roach=0.22)
make_sail("Jib",
          (2.72, 0.0, 0.62), (0.62, 0.0, 4.42), (1.05, 0.0, 1.35),
          camber=0.14, roach=0.05, nu=10, nv=12)

# ------------------------------------------------------------------ deck detail
for sgn in (-1, 1):
    for u in (0.24, 0.42, 0.60, 0.76, 0.88):
        idx = min(range(len(STATIONS)), key=lambda k: abs(STATIONS[k][0] - u))
        _, hb, _, sheer = STATIONS[idx]
        x = -L * 0.5 + u * L
        y = sgn * hb * B * 0.90
        add_rod("Stanchion", (x, y, sheer), (x, y, sheer + 0.56), 0.014, M_STEEL, 8)
    pts = []
    for u, hb, _, sheer in STATIONS[2:-1]:
        pts.append(Vector((-L * 0.5 + u * L, sgn * hb * B * 0.90, sheer + 0.54)))
    for p0, p1 in zip(pts, pts[1:]):
        add_rod("Lifeline", p0, p1, 0.007, M_STEEL, 6)
    add_cyl("Winch", 0.075, 0.11, (-0.72, sgn * 0.56, 0.24), verts=16,
            material=M_STEEL, r2=0.062)
    add_box("Cleat", (0.14, 0.04, 0.04), (0.30, sgn * 0.82, 0.10), material=M_STEEL,
            bevel=0.012)
add_cyl("BowPulpitBase", 0.05, 0.05, (2.80, 0, 0.50), material=M_STEEL, verts=12)
add_rod("Bowsprit", (2.70, 0, 0.44), (3.20, 0, 0.52), 0.035, M_WOOD, 10)

# ------------------------------------------------------------------ water
bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=80, size=120.0,
                                location=(0, 0, WATERLINE))
water = bpy.context.object
water.name = "Sea"
finish(water, M_WATER, smooth=True)
me = water.data
for v in me.vertices:
    v.co.z += (0.035 * math.sin(v.co.x * 0.9 + 0.4) * math.cos(v.co.y * 0.7)
               + 0.018 * math.sin(v.co.x * 2.3 - v.co.y * 1.7))

# ------------------------------------------------------------------ world / lights
world = bpy.data.worlds.new("SeaWorld")
bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.1
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sun_elevation = math.radians(28)
sky.sun_rotation = math.radians(200)
nt.links.new(sky.outputs[0], bg.inputs["Color"])

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.5
sun_data.angle = math.radians(2.0)
sun_data.color = (1.0, 0.95, 0.86)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (-6, -9, 12)
look_at(sun, (0, 0, 1.5))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 400.0
fill_data.size = 8.0
fill_data.color = (0.62, 0.76, 0.95)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (7, 6, 5)
look_at(fill, (0, 0, 1.5))

# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (8.6, -9.8, 3.9)
look_at(cam, (0.1, 0.0, 2.0))
bpy.context.scene.camera = cam

print("claude-056 sailboat scene built: %d objects" % len(bpy.data.objects))
