import bpy, bmesh, math
from mathutils import Vector

# ----------------------------------------------------------------------------- utils
def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for blk in list(coll):
            if blk.users == 0:
                coll.remove(blk)

def set_in(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value

def add_mat(name, base=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, emit=None,
            emit_str=1.0, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    set_in(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    set_in(bsdf, "Roughness", rough)
    set_in(bsdf, "Metallic", metal)
    set_in(bsdf, "Alpha", alpha)
    set_in(bsdf, "Transmission Weight", transmission)
    if emit is not None:
        set_in(bsdf, "Emission Color", (emit[0], emit[1], emit[2], 1.0))
        set_in(bsdf, "Emission Strength", emit_str)
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat

def link(obj, parent=None):
    bpy.context.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj

def finish(mesh, bm, bevel=0.0, segments=2, smooth=False):
    if bevel > 0.0:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bevel(bm, geom=geom, offset=bevel, segments=segments,
                        affect='EDGES', profile=0.5, clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True

def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bevel=0.0, parent=None):
    """size = full dimensions, centred on the object origin."""
    hx, hy, hz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
             (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if bevel > 0.0:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        finish(mesh, bm, bevel=bevel)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        mesh.materials.append(mat)
    return link(obj, parent)

def tube(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
         segments=16, parent=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    finish(mesh, bm, smooth=True)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        mesh.materials.append(mat)
    return link(obj, parent)

def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    e.location = loc
    return link(e)

# ----------------------------------------------------------------------------- setup
clear_scene()
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128

# carriage dimensions
LEN = 16.0            # along X
HALF_W = 1.45         # inner wall at y = +/- HALF_W
WALL_T = 0.07
SILL_Z = 0.78         # window bottom
HEAD_Z = 1.70         # window top
EAVE_Z = 2.20         # ceiling at the side wall
CROWN_Z = 2.46        # ceiling at centreline
WIN_PITCH = 1.6
WIN_W = 1.2
WIN_X = [-6.4 + i * WIN_PITCH for i in range(9)]
BAY_X = [-5.6, -2.4, 0.8, 4.0]   # facing-seat bay centres

# ----------------------------------------------------------------------------- materials
m_floor   = add_mat("Vinyl.Floor", (0.055, 0.06, 0.07), rough=0.45)
m_runner  = add_mat("Carpet.Runner", (0.09, 0.11, 0.15), rough=0.92)
m_panel   = add_mat("Panel.Wall", (0.72, 0.71, 0.68), rough=0.55)
m_lower   = add_mat("Panel.Lower", (0.20, 0.22, 0.26), rough=0.6)
m_ceiling = add_mat("Panel.Ceiling", (0.86, 0.86, 0.84), rough=0.75)
m_trim    = add_mat("Trim.Anodised", (0.55, 0.56, 0.58), rough=0.32, metal=1.0)
m_steel   = add_mat("Steel.Brushed", (0.72, 0.73, 0.75), rough=0.24, metal=1.0)
m_dark    = add_mat("Plastic.Dark", (0.045, 0.047, 0.05), rough=0.45)
m_glass   = add_mat("Glass.Window", (0.82, 0.87, 0.9), rough=0.03,
                    alpha=0.12, transmission=1.0)
m_fabric  = add_mat("Fabric.Seat", (0.075, 0.13, 0.21), rough=0.9)
m_fabric2 = add_mat("Fabric.Seat.Trim", (0.42, 0.13, 0.16), rough=0.9)
m_head    = add_mat("Fabric.Headrest", (0.30, 0.32, 0.36), rough=0.88)
m_table   = add_mat("Laminate.Table", (0.30, 0.24, 0.18), rough=0.28)
m_lamp    = add_mat("Lamp.Diffuser", (0.95, 0.95, 0.95), rough=0.4,
                    emit=(1.0, 0.94, 0.82), emit_str=6.0)
m_strip   = add_mat("Lamp.Cove", (0.95, 0.95, 0.95), rough=0.4,
                    emit=(1.0, 0.90, 0.76), emit_str=2.5)
m_sky     = add_mat("Backdrop.Sky", (0.5, 0.6, 0.7), rough=1.0,
                    emit=(0.55, 0.70, 0.92), emit_str=3.0)

# ----------------------------------------------------------------------------- shell
root = empty("Carriage")

box("Floor", (LEN, HALF_W * 2, 0.12), (0, 0, -0.06), mat=m_floor, parent=root)
box("Floor.Runner", (LEN - 0.4, 0.72, 0.012), (0, 0, 0.006), mat=m_runner, parent=root)

def build_side(sign):
    y_in = sign * HALF_W
    y_c = sign * (HALF_W + WALL_T * 0.5)
    tag = "L" if sign > 0 else "R"
    grp = empty("Side.%s" % tag)
    grp.parent = root

    # lower body side and upper band above the windows
    box("Wall.Lower.%s" % tag, (LEN, WALL_T, SILL_Z), (0, y_c, SILL_Z * 0.5),
        mat=m_lower, parent=grp)
    box("Wall.Upper.%s" % tag, (LEN, WALL_T, EAVE_Z - HEAD_Z),
        (0, y_c, (EAVE_Z + HEAD_Z) * 0.5), mat=m_panel, parent=grp)
    # window sill / cant rail trims
    box("Sill.%s" % tag, (LEN, 0.09, 0.05), (0, y_in - sign * 0.045, SILL_Z + 0.02),
        mat=m_trim, bevel=0.008, parent=grp)
    box("Cantrail.%s" % tag, (LEN, 0.06, 0.04), (0, y_in - sign * 0.03, HEAD_Z - 0.02),
        mat=m_trim, parent=grp)

    # pillars between the windows (fill the gaps of the glazing band)
    edges = [-LEN * 0.5] + [x for xc in WIN_X for x in (xc - WIN_W * 0.5, xc + WIN_W * 0.5)] \
            + [LEN * 0.5]
    for i in range(0, len(edges) - 1, 2):
        x0, x1 = edges[i], edges[i + 1]
        if x1 - x0 > 1e-4:
            box("Pillar.%s.%02d" % (tag, i), (x1 - x0, WALL_T, HEAD_Z - SILL_Z),
                ((x0 + x1) * 0.5, y_c, (SILL_Z + HEAD_Z) * 0.5), mat=m_panel, parent=grp)

    # glazing
    for i, xc in enumerate(WIN_X):
        box("Glass.%s.%02d" % (tag, i), (WIN_W, 0.012, HEAD_Z - SILL_Z - 0.06),
            (xc, y_in - sign * 0.012, (SILL_Z + HEAD_Z) * 0.5 - 0.01),
            mat=m_glass, parent=grp)
        box("WinFrame.%s.%02d" % (tag, i), (WIN_W + 0.07, 0.035, HEAD_Z - SILL_Z),
            (xc, y_in - sign * 0.03, (SILL_Z + HEAD_Z) * 0.5), mat=m_dark, parent=grp)

    build_rack(sign, grp)
    return grp

def build_rack(sign, grp):
    """Open tubular luggage rack running above the windows."""
    tag = "L" if sign > 0 else "R"
    y_wall = sign * HALF_W
    z0 = HEAD_Z + 0.06
    n_slats = 5
    for i in range(n_slats):
        t = i / float(n_slats - 1)
        y = y_wall - sign * (0.10 + t * 0.46)
        z = z0 + (1.0 - t) * 0.11          # slopes down away from the wall
        tube("Rack.Slat.%s.%d" % (tag, i), 0.016, LEN - 0.9,
             (0, y, z), (0, math.radians(90), 0), mat=m_steel, segments=12, parent=grp)
    # front lip rail
    tube("Rack.Lip.%s" % tag, 0.022, LEN - 0.9,
         (0, y_wall - sign * 0.60, z0 + 0.145), (0, math.radians(90), 0),
         mat=m_steel, segments=14, parent=grp)
    # brackets, aligned with the body pillars
    for i, xc in enumerate(WIN_X + [WIN_X[0] - WIN_PITCH, WIN_X[-1] + WIN_PITCH]):
        xb = xc + WIN_PITCH * 0.5
        if abs(xb) > LEN * 0.5 - 0.6:
            continue
        box("Rack.Arm.%s.%02d" % (tag, i), (0.05, 0.62, 0.035),
            (xb, y_wall - sign * 0.33, z0 + 0.05), (sign * math.radians(-9), 0, 0),
            mat=m_steel, bevel=0.008, parent=grp)
        box("Rack.Stay.%s.%02d" % (tag, i), (0.045, 0.06, 0.34),
            (xb, y_wall - sign * 0.055, z0 + 0.20), mat=m_steel, parent=grp)

build_side(1)
build_side(-1)

# vaulted ceiling ---------------------------------------------------------------
def build_ceiling():
    nx, ny = 24, 16
    mesh = bpy.data.meshes.new("Ceiling")
    bm = bmesh.new()
    grid = []
    for i in range(nx + 1):
        x = -LEN * 0.5 + LEN * i / nx
        row = []
        for j in range(ny + 1):
            y = -HALF_W + 2.0 * HALF_W * j / ny
            t = y / HALF_W
            z = CROWN_Z - (CROWN_Z - EAVE_Z) * (t * t)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # normals must face down into the saloon
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new("Ceiling", mesh)
    mesh.materials.append(m_ceiling)
    return link(obj, root)

build_ceiling()

# end bulkheads with a doorway ---------------------------------------------------
def build_bulkhead(sign):
    x = sign * LEN * 0.5
    tag = "F" if sign > 0 else "B"
    grp = empty("Bulkhead.%s" % tag)
    grp.parent = root
    door_w, door_h = 0.9, 2.02
    for s in (-1, 1):
        w = HALF_W - door_w * 0.5
        box("Bulk.Side.%s%d" % (tag, s), (0.09, w, EAVE_Z),
            (x - sign * 0.045, s * (door_w * 0.5 + w * 0.5), EAVE_Z * 0.5),
            mat=m_panel, parent=grp)
    box("Bulk.Header.%s" % tag, (0.09, door_w, EAVE_Z - door_h),
        (x - sign * 0.045, 0, (EAVE_Z + door_h) * 0.5), mat=m_panel, parent=grp)
    # sliding door leaf, parked half open, with a glazed vision panel
    box("Door.Leaf.%s" % tag, (0.05, door_w * 0.62, door_h),
        (x - sign * 0.11, door_w * 0.30, door_h * 0.5), mat=m_trim,
        bevel=0.01, parent=grp)
    box("Door.Glass.%s" % tag, (0.02, 0.36, 0.9),
        (x - sign * 0.11, door_w * 0.30, 1.42), mat=m_glass, parent=grp)
    # vestibule void beyond, so the doorway does not read as a black hole
    box("Vestibule.%s" % tag, (0.06, HALF_W * 2, EAVE_Z),
        (x + sign * 1.0, 0, EAVE_Z * 0.5), mat=m_lower, parent=grp)
    # grab poles flanking the doorway
    for s in (-1, 1):
        tube("Pole.%s%d" % (tag, s), 0.022, EAVE_Z,
             (x - sign * 0.35, s * 0.62, EAVE_Z * 0.5), mat=m_steel, parent=grp)
    return grp

build_bulkhead(1)
build_bulkhead(-1)

# ----------------------------------------------------------------------------- seating
def build_seat_bank(name, loc, face):
    """A two-place seat bank facing +X in local space."""
    grp = empty(name)
    grp.parent = root
    grp.location = loc
    grp.rotation_euler = (0, 0, 0 if face > 0 else math.pi)
    W = 1.04                       # overall bank width

    box("Base", (0.52, W - 0.06, 0.34), (-0.12, 0, 0.17), mat=m_dark,
        bevel=0.015, parent=grp)
    box("Plinth", (0.44, W - 0.20, 0.06), (-0.12, 0, 0.03), mat=m_steel, parent=grp)

    for s in (-1, 1):
        y = s * W * 0.25
        box("Cushion.%d" % s, (0.56, W * 0.48, 0.13), (0.02, y, 0.435),
            mat=m_fabric, bevel=0.035, parent=grp)
        box("Back.%d" % s, (0.15, W * 0.48, 0.66), (-0.285, y, 0.79),
            (0, math.radians(-8), 0), mat=m_fabric, bevel=0.035, parent=grp)
        box("Headrest.%d" % s, (0.14, W * 0.40, 0.24), (-0.375, y, 1.20),
            (0, math.radians(-8), 0), mat=m_head, bevel=0.03, parent=grp)
        box("Piping.%d" % s, (0.58, 0.025, 0.145), (0.02, s * (W * 0.48), 0.435),
            mat=m_fabric2, parent=grp)

    # centre divider and armrests
    box("Divider", (0.5, 0.04, 0.62), (-0.16, 0, 0.72), mat=m_fabric,
        bevel=0.012, parent=grp)
    for s in (-1, 1):
        box("Armrest.%d" % s, (0.46, 0.075, 0.055), (0.05, s * (W * 0.5 - 0.02), 0.66),
            mat=m_dark, bevel=0.02, parent=grp)
        box("Arm.Stem.%d" % s, (0.07, 0.05, 0.20), (-0.13, s * (W * 0.5 - 0.02), 0.55),
            mat=m_dark, parent=grp)
    # grab rail across the top of the squab
    tube("Grab", 0.017, W - 0.10, (-0.40, 0, 1.35), (math.radians(90), 0, 0),
         mat=m_steel, segments=12, parent=grp)
    return grp

def build_table(loc):
    grp = empty("Table")
    grp.parent = root
    grp.location = loc
    box("Table.Top", (0.62, 1.0, 0.035), (0, 0, 0.72), mat=m_table,
        bevel=0.012, parent=grp)
    box("Table.Edge", (0.64, 1.02, 0.012), (0, 0, 0.700), mat=m_trim, parent=grp)
    tube("Table.Leg", 0.045, 0.70, (0, 0, 0.35), mat=m_steel, segments=14, parent=grp)
    tube("Table.Foot", 0.16, 0.03, (0, 0, 0.015), mat=m_steel, segments=20, parent=grp)
    return grp

SEAT_OFFSET = 1.02      # bank origin distance from the bay centre
for b, xc in enumerate(BAY_X):
    for s in (-1, 1):                       # both sides of the aisle
        y = s * 0.86
        build_seat_bank("Seat.%02d.%d.A" % (b, s), (xc - SEAT_OFFSET, y, 0.0), +1)
        build_seat_bank("Seat.%02d.%d.B" % (b, s), (xc + SEAT_OFFSET, y, 0.0), -1)
        build_table((xc, y, 0.0))

# ----------------------------------------------------------------------------- lighting
lamp_grp = empty("Lighting")
lamp_grp.parent = root

# central ceiling light run: emissive diffusers plus matching area lamps
for i, x in enumerate([-7.0 + i * 1.75 for i in range(9)]):
    z = CROWN_Z - 0.02
    box("Lamp.Diffuser.%02d" % i, (1.45, 0.30, 0.035), (x, 0, z),
        mat=m_lamp, bevel=0.008, parent=lamp_grp)
    box("Lamp.Bezel.%02d" % i, (1.55, 0.38, 0.02), (x, 0, z + 0.03),
        mat=m_trim, parent=lamp_grp)

    ld = bpy.data.lights.new("Ceiling.Light.%02d" % i, 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = 1.4, 0.28
    ld.energy = 55.0
    ld.color = (1.0, 0.94, 0.85)
    lo = bpy.data.objects.new("Ceiling.Light.%02d" % i, ld)
    lo.location = (x, 0, z - 0.04)
    lo.rotation_euler = (math.pi, 0, 0)     # point straight down
    link(lo, lamp_grp)

# cove strips washing the underside of the luggage racks
for s in (-1, 1):
    y = s * (HALF_W - 0.62)
    box("Cove.%d" % s, (LEN - 1.0, 0.06, 0.03), (0, y, HEAD_Z + 0.20),
        mat=m_strip, parent=lamp_grp)
    ld = bpy.data.lights.new("Cove.Light.%d" % s, 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = LEN - 1.0, 0.1
    ld.energy = 40.0
    ld.color = (1.0, 0.90, 0.78)
    lo = bpy.data.objects.new("Cove.Light.%d" % s, ld)
    lo.location = (0, y, HEAD_Z + 0.18)
    lo.rotation_euler = (math.pi, 0, 0)
    link(lo, lamp_grp)

# daylight outside the glazing
for s in (-1, 1):
    box("Backdrop.%d" % s, (LEN + 8.0, 0.05, 9.0), (0, s * 7.0, 2.0),
        mat=m_sky, parent=lamp_grp)

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 2.6
sun_data.angle = math.radians(3.0)
sun_data.color = (1.0, 0.96, 0.90)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(58), 0, math.radians(-130))
link(sun, lamp_grp)

world = bpy.data.worlds.new("World") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.32, 0.40, 0.52, 1.0)
    bg.inputs[1].default_value = 0.5

# ----------------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 24.0
cam_data.sensor_width = 36.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 6.5
cam_data.dof.aperture_fstop = 3.2
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (-7.1, -0.14, 1.62)
cam.rotation_euler = (math.radians(87.0), 0.0, math.radians(-92.0))
link(cam)
scene.camera = cam

print("Railway carriage interior built: %d objects" % len(bpy.data.objects))
