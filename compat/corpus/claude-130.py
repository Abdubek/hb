import bpy, bmesh, math
from mathutils import Vector, Matrix

# =============================================================== scene helpers
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 128


def mat_pbr(name, color, metallic=0.0, rough=0.5, emis=None, emis_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if emis is not None:
        b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    return m


class Builder:
    """Accumulates primitive members into a single bmesh (one per material)."""

    def __init__(self, name, material):
        self.name = name
        self.material = material
        self.bm = bmesh.new()

    def cyl(self, p1, p2, r, seg=10):
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        L = d.length
        if L < 1e-6:
            return
        m = Matrix.Translation((p1 + p2) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r, depth=L, matrix=m)

    def cone(self, p1, p2, r1, r2, seg=24):
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        L = d.length
        if L < 1e-6:
            return
        m = Matrix.Translation((p1 + p2) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=L, matrix=m)

    def box(self, center, size, rot_z=0.0):
        m = (Matrix.Translation(Vector(center))
             @ Matrix.Rotation(rot_z, 4, 'Z')
             @ Matrix.Diagonal((size[0], size[1], size[2], 1.0)))
        bmesh.ops.create_cube(self.bm, size=1.0, matrix=m)

    def ball(self, center, r, subd=2):
        bmesh.ops.create_icosphere(self.bm, subdivisions=subd, radius=r,
                                   matrix=Matrix.Translation(Vector(center)))

    def finish(self):
        me = bpy.data.meshes.new(self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(self.name, me)
        me.materials.append(self.material)
        bpy.context.scene.collection.objects.link(ob)
        return ob


# =============================================================== tower profile
MODULE_H = 4.0
N_MOD = 8
H = MODULE_H * N_MOD          # 32 m to the top of the lattice
BASE_HW = 3.2                 # half width of the leg square at grade
TOP_HW = 1.2
TAPER_TOP = 24.0              # tapers to here, then runs parallel


def half_width(z):
    if z <= TAPER_TOP:
        return BASE_HW + (TOP_HW - BASE_HW) * (z / TAPER_TOP)
    return TOP_HW


def leg_radius(z):
    return 0.15 - 0.06 * (z / H)


def corners(z):
    h = half_width(z)
    return [Vector((h, h, z)), Vector((-h, h, z)),
            Vector((-h, -h, z)), Vector((h, -h, z))]


# =============================================================== sub assemblies
def build_lattice(steel):
    """Legs, horizontal belts and X / K bracing, module by module."""
    for m in range(N_MOD):
        zb = m * MODULE_H
        zt = zb + MODULE_H
        cb, ct = corners(zb), corners(zt)
        r = leg_radius((zb + zt) * 0.5)

        # leg segments with a small flanged joint at every module split
        for i in range(4):
            steel.cyl(cb[i], ct[i], r, 12)
            steel.cyl(ct[i] - Vector((0, 0, 0.09)), ct[i] + Vector((0, 0, 0.09)),
                      r * 1.55, 12)

        # horizontal belt at the top of the module
        for i in range(4):
            steel.cyl(ct[i], ct[(i + 1) % 4], 0.07, 8)

        # face bracing
        for i in range(4):
            j = (i + 1) % 4
            b0, b1, t0, t1 = cb[i], cb[j], ct[i], ct[j]
            steel.cyl(b0, t1, 0.05, 8)
            steel.cyl(b1, t0, 0.05, 8)
            if m < 5:                                     # secondary bracing low down
                mi = (b0 + t0) * 0.5
                mj = (b1 + t1) * 0.5
                steel.cyl(mi, mj, 0.042, 8)
                x = (b0 + b1 + t0 + t1) * 0.25
                steel.cyl(x, (b0 + b1) * 0.5, 0.036, 8)
                steel.cyl(x, (t0 + t1) * 0.5, 0.036, 8)

        # plan bracing (hip) inside the tower at every second level
        if m % 2 == 1:
            steel.cyl(ct[0], ct[2], 0.04, 8)
            steel.cyl(ct[1], ct[3], 0.04, 8)

    # base beams and gusset stubs just above the pads
    c = corners(0.55)
    for i in range(4):
        steel.cyl(c[i], c[(i + 1) % 4], 0.08, 8)


def build_foundations(steel, concrete):
    for c in corners(0.0):
        concrete.box((c.x, c.y, 0.05), (1.5, 1.5, 1.1))
        steel.box((c.x, c.y, 0.64), (0.95, 0.95, 0.07))
        for sx in (-1, 1):
            for sy in (-1, 1):
                steel.cyl((c.x + 0.35 * sx, c.y + 0.35 * sy, 0.60),
                          (c.x + 0.35 * sx, c.y + 0.35 * sy, 0.80), 0.03, 6)


def build_platform(steel, grating, z):
    """Ring walkway around the legs with outriggers and railing."""
    h = half_width(z)
    inner = h - 0.40
    outer = h + 1.05
    band = (outer - inner)
    mid = (outer + inner) * 0.5
    zz = z + 0.06

    # four grating slabs forming a ring
    grating.box((0, mid, zz), (2 * outer, band, 0.11))
    grating.box((0, -mid, zz), (2 * outer, band, 0.11))
    grating.box((mid, 0, zz), (band, 2 * inner, 0.11))
    grating.box((-mid, 0, zz), (band, 2 * inner, 0.11))

    # perimeter kerb angle
    pts = [Vector((outer, outer, z)), Vector((-outer, outer, z)),
           Vector((-outer, -outer, z)), Vector((outer, -outer, z))]
    for i in range(4):
        steel.cyl(pts[i], pts[(i + 1) % 4], 0.055, 8)

    # outriggers: corners and mid-sides braced back down to the legs
    legs = corners(z)
    below = corners(z - 1.5)
    for i in range(4):
        steel.cyl(pts[i], below[i], 0.05, 8)
        steel.cyl(pts[i], legs[i], 0.05, 8)
        a, b = pts[i], pts[(i + 1) % 4]
        ma = (a + b) * 0.5
        la = (legs[i] + legs[(i + 1) % 4]) * 0.5
        steel.cyl(ma, la, 0.045, 8)
        steel.cyl(ma, la - Vector((0, 0, 1.4)), 0.045, 8)

    build_railing(steel, z, outer, gap_face=0)


def build_railing(steel, z, out, gap_face=0):
    pts = [Vector((out, out, z)), Vector((-out, out, z)),
           Vector((-out, -out, z)), Vector((out, -out, z))]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        segs = [(a, b)]
        if i == gap_face:                                  # ladder access opening
            d = (b - a).normalized()
            L = (b - a).length
            segs = [(a, a + d * (L * 0.5 - 0.65)),
                    (a + d * (L * 0.5 + 0.65), b)]
        for p, q in segs:
            for hgt in (1.10, 0.60):
                steel.cyl(p + Vector((0, 0, hgt)), q + Vector((0, 0, hgt)), 0.028, 8)
            L = (q - p).length
            n = max(2, int(L / 1.3) + 1)
            step = (q - p) / (n - 1)
            for k in range(n):
                base = p + step * k
                steel.cyl(base + Vector((0, 0, 0.08)),
                          base + Vector((0, 0, 1.16)), 0.030, 8)


def build_climb_ladder(steel, z0, z1):
    """Caged climbing ladder on the +Y face, following the taper."""
    step = 1.0
    z = z0
    while z < z1 - 1e-6:
        zt = min(z + step, z1)
        for sx in (-0.32, 0.32):
            steel.cyl((sx, half_width(z) + 0.62, z),
                      (sx, half_width(zt) + 0.62, zt), 0.035, 8)
        z = zt
    # rungs
    z = z0 + 0.3
    while z < z1:
        y = half_width(z) + 0.62
        steel.cyl((-0.32, y, z), (0.32, y, z), 0.018, 6)
        z += 0.35
    # hoops of the safety cage every 1.4 m
    z = z0 + 1.2
    while z < z1:
        y = half_width(z) + 0.62
        n = 9
        prev = None
        for k in range(n):
            a = math.pi * (k / (n - 1)) - math.pi * 0.5
            p = Vector((0.62 * math.sin(a), y + 0.62 * math.cos(a) * 0.9, z))
            if prev is not None:
                steel.cyl(prev, p, 0.016, 6)
            prev = p
        z += 1.4
    # standoff brackets tying the ladder to the legs
    z = z0 + 0.6
    while z < z1:
        y = half_width(z) + 0.62
        steel.cyl((0.32, y, z), (half_width(z), half_width(z), z), 0.024, 6)
        steel.cyl((-0.32, y, z), (-half_width(z), half_width(z), z), 0.024, 6)
        z += 2.8


def build_cable_ladder(steel, cable, z0, z1):
    """Cable ladder (tray) on the +X face carrying feeder bundles."""
    step = 1.0
    z = z0
    while z < z1 - 1e-6:
        zt = min(z + step, z1)
        for sy in (-0.30, 0.30):
            steel.cyl((half_width(z) + 0.50, sy, z),
                      (half_width(zt) + 0.50, sy, zt), 0.032, 8)
        z = zt
    z = z0
    while z < z1:
        x = half_width(z) + 0.50
        steel.cyl((x, -0.30, z), (x, 0.30, z), 0.016, 6)
        if abs((z - z0) % 2.4) < 0.3:                      # tray brackets
            steel.cyl((x, 0.30, z), (half_width(z), half_width(z) * 0.55, z), 0.024, 6)
            steel.cyl((x, -0.30, z), (half_width(z), -half_width(z) * 0.55, z), 0.024, 6)
        z += 0.45

    # feeder bundles clipped to the tray, dropping to the ice bridge at the base
    for k, sy in enumerate((-0.20, -0.07, 0.07, 0.20, 0.0)):
        top = min(z1, 12.0 + 8.0 * (k % 3))
        r = 0.045 if k < 4 else 0.055
        z = z0
        while z < top - 1e-6:
            zt = min(z + step, top)
            cable.cyl((half_width(z) + 0.36 + 0.02 * k, sy, z),
                      (half_width(zt) + 0.36 + 0.02 * k, sy, zt), r, 8)
            z = zt
        # gentle bend down to the horizontal run
        x0 = half_width(z0) + 0.36 + 0.02 * k
        n = 8
        prev = Vector((x0, sy, z0))
        for i in range(1, n + 1):
            t = i / n
            p = Vector((x0 + 1.1 * math.sin(t * math.pi * 0.5),
                        sy,
                        z0 - 1.1 * (1 - math.cos(t * math.pi * 0.5))))
            cable.cyl(prev, p, r, 8)
            prev = p
        cable.cyl(prev, Vector((9.4, sy, prev.z)), r, 8)


def build_ice_bridge(steel, x0, x1, z):
    """Horizontal cable bridge from the tower base to the equipment shelter."""
    for sy in (-0.45, 0.45):
        steel.cyl((x0, sy, z), (x1, sy, z), 0.04, 8)
        steel.cyl((x0, sy, z + 0.45), (x1, sy, z + 0.45), 0.03, 8)
    x = x0
    while x <= x1 + 1e-6:
        steel.cyl((x, -0.45, z), (x, 0.45, z), 0.016, 6)
        x += 0.5
    for xp in (x0 + 1.6, x0 + 4.2):
        for sy in (-0.45, 0.45):
            steel.cyl((xp, sy, 0.0), (xp, sy, z), 0.045, 8)
        steel.cyl((xp, -0.45, z), (xp, 0.45, z + 0.45), 0.025, 6)


def build_sector(steel, white, dark, z, az, panel_h=1.35):
    """Mount pipe with a panel antenna, RRU and tilt bracket at one azimuth."""
    d = Vector((math.cos(az), math.sin(az), 0.0))
    t = Vector((-d.y, d.x, 0.0))
    h = half_width(z)
    rad = h + 1.35
    base = Vector((d.x * rad, d.y * rad, z - 0.5))
    top = base + Vector((0, 0, 3.1))
    steel.cyl(base, top, 0.06, 10)                          # mounting pipe

    # tie-back arms into the tower belt
    inner = Vector((d.x * h * 0.9, d.y * h * 0.9, z))
    steel.cyl(base + Vector((0, 0, 0.6)), inner, 0.04, 8)
    steel.cyl(top - Vector((0, 0, 0.5)), inner + Vector((0, 0, 1.1)), 0.04, 8)

    # panel antenna, slightly downtilted
    pc = base + Vector((0, 0, 1.85)) + d * 0.30
    tilt = math.radians(6.0)
    rot = (Matrix.Translation(pc)
           @ Matrix.Rotation(az, 4, 'Z')
           @ Matrix.Rotation(tilt, 4, 'Y'))
    bmesh.ops.create_cube(white.bm, size=1.0,
                          matrix=rot @ Matrix.Diagonal((0.13, 0.32, panel_h, 1.0)))
    # radome cap details
    for sz in (-1, 1):
        bmesh.ops.create_cube(white.bm, size=1.0,
                              matrix=(rot @ Matrix.Translation((0, 0, sz * panel_h * 0.5))
                                      @ Matrix.Diagonal((0.15, 0.34, 0.05, 1.0))))
    # bracket
    steel.cyl(pc - d * 0.34, pc, 0.028, 6)
    steel.cyl(pc - d * 0.34 + Vector((0, 0, 0.45)), pc + Vector((0, 0, 0.45)), 0.028, 6)

    # remote radio unit behind the panel
    rc = base + Vector((0, 0, 1.2)) - d * 0.24
    dark.box((rc.x, rc.y, rc.z), (0.22, 0.30, 0.55), rot_z=az)
    for k in range(4):
        dark.box((rc.x - d.x * 0.13, rc.y - d.y * 0.13, rc.z - 0.18 + k * 0.12),
                 (0.05, 0.28, 0.05), rot_z=az)
    # jumpers from RRU up to the panel
    dark.cyl(rc + t * 0.12, pc - d * 0.20 + t * 0.10, 0.02, 6)


def build_dish(steel, white, z, az, dia=1.3):
    d = Vector((math.cos(az), math.sin(az), 0.0))
    h = half_width(z)
    mount = Vector((d.x * (h + 0.15), d.y * (h + 0.15), z))
    hub = mount + d * 0.85
    steel.cyl(mount, hub, 0.055, 10)
    white.cone(hub, hub + d * 0.42, 0.14, dia * 0.5, 28)     # reflector
    white.cyl(hub + d * 0.42, hub + d * 0.55, dia * 0.5, 28)  # shroud lip
    steel.cyl(hub + d * 0.42, hub + d * 0.85, 0.035, 8)       # feed boom
    steel.ball(hub + d * 0.88, 0.09)
    # elevation bracket
    steel.cyl(mount + Vector((0, 0, -0.45)), hub, 0.035, 8)
    steel.cyl(mount + Vector((0, 0, 0.45)), hub, 0.035, 8)


def build_mast(steel, red, white, lights):
    """Red/white banded top mast with whip antennas and warning light."""
    z = H
    seg = 1.0
    k = 0
    while z < H + 7.0 - 1e-6:
        zt = min(z + seg, H + 7.0)
        tgt = red if k % 2 == 0 else white
        tgt.cyl((0, 0, z), (0, 0, zt), 0.085, 12)
        z = zt
        k += 1
    # transition frame from the four legs to the single mast
    top = corners(H)
    for i in range(4):
        steel.cyl(top[i], (0, 0, H + 1.6), 0.045, 8)

    # whip antennas on a small crossarm
    ca = H + 5.6
    steel.cyl((-0.75, 0, ca), (0.75, 0, ca), 0.035, 8)
    steel.cyl((0, -0.75, ca), (0, 0.75, ca), 0.035, 8)
    for p in ((0.72, 0), (-0.72, 0), (0, 0.72), (0, -0.72)):
        steel.cyl((p[0], p[1], ca - 0.1), (p[0], p[1], ca + 2.3), 0.018, 6)
        steel.ball((p[0], p[1], ca + 2.32), 0.035, 1)

    # aviation obstruction lights
    for zl in (H + 7.05, H * 0.55):
        lights.ball((0, 0, zl) if zl > H else (half_width(zl) + 0.2, 0, zl), 0.14, 2)


def build_shelter(dark, light_grey, steel):
    cx, cy = 12.6, -1.4
    light_grey.box((cx, cy, 1.35), (4.6, 3.4, 2.7))
    light_grey.box((cx, cy, 2.78), (5.0, 3.8, 0.16))          # roof overhang
    dark.box((cx - 2.32, cy + 0.5, 1.05), (0.10, 1.0, 2.1))   # door
    dark.box((cx + 0.4, cy - 1.75, 2.0), (1.4, 0.35, 0.9))    # HVAC unit
    for k in range(6):
        steel.box((cx + 0.4, cy - 1.94, 1.72 + k * 0.11), (1.3, 0.05, 0.05))
    steel.cyl((cx - 2.4, cy + 1.9, 0.0), (cx - 2.4, cy + 1.9, 3.6), 0.06, 8)
    dark.box((cx - 2.4, cy + 1.9, 3.0), (0.4, 0.3, 0.5))      # small light pole head
    light_grey.box((cx, cy, 0.06), (5.4, 4.2, 0.14))          # slab


# =============================================================== assemble scene
def main():
    clean_scene()

    m_steel = mat_pbr("Galvanised_Steel", (0.62, 0.64, 0.66), 1.0, 0.42)
    m_grating = mat_pbr("Grating", (0.20, 0.21, 0.22), 0.85, 0.60)
    m_white = mat_pbr("Antenna_Radome", (0.88, 0.88, 0.85), 0.0, 0.35)
    m_red = mat_pbr("Mast_Red", (0.55, 0.05, 0.04), 0.0, 0.40)
    m_dark = mat_pbr("Equipment_Grey", (0.10, 0.10, 0.11), 0.35, 0.50)
    m_cable = mat_pbr("Feeder_Cable", (0.045, 0.045, 0.05), 0.0, 0.65)
    m_conc = mat_pbr("Concrete", (0.56, 0.55, 0.52), 0.0, 0.85)
    m_ground = mat_pbr("Gravel_Ground", (0.30, 0.29, 0.26), 0.0, 0.95)
    m_light = mat_pbr("Warning_Light", (0.6, 0.03, 0.03), 0.0, 0.3,
                      emis=(1.0, 0.06, 0.03), emis_str=28.0)

    steel = Builder("Tower_Steel", m_steel)
    grating = Builder("Platform_Grating", m_grating)
    white = Builder("Antennas_White", m_white)
    red = Builder("Mast_Bands_Red", m_red)
    dark = Builder("Equipment", m_dark)
    cable = Builder("Feeder_Cables", m_cable)
    conc = Builder("Foundations", m_conc)
    lights = Builder("Warning_Lights", m_light)

    build_lattice(steel)
    build_foundations(steel, conc)

    platform_levels = [12.0, 20.0, 28.0]
    for z in platform_levels:
        build_platform(steel, grating, z)

    build_climb_ladder(steel, 0.9, H + 0.6)
    build_cable_ladder(steel, cable, 1.4, 29.0)
    build_ice_bridge(steel, half_width(2.4) + 0.4, 10.2, 2.4)

    # antenna sectors: three per platform, rotated per level
    for li, z in enumerate(platform_levels):
        for s in range(3):
            az = math.radians(120.0 * s + 30.0 * li)
            build_sector(steel, white, dark, z + 0.15, az,
                         panel_h=1.55 if li == len(platform_levels) - 1 else 1.30)

    # microwave links
    build_dish(steel, white, 22.6, math.radians(75.0), dia=1.5)
    build_dish(steel, white, 25.4, math.radians(215.0), dia=1.1)
    build_dish(steel, white, 14.2, math.radians(300.0), dia=0.8)

    build_mast(steel, red, white, lights)
    build_shelter(dark, conc, steel)

    for b in (steel, grating, white, red, dark, cable, conc, lights):
        b.finish()

    # ground
    gb = Builder("Ground", m_ground)
    gb.box((0, 0, -0.06), (120, 120, 0.12))
    gb.finish()

    # ------------------------------------------------------------- lighting
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 4.0
    sun_data.angle = math.radians(1.2)
    sun_data.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(56.0), 0.0, math.radians(38.0))
    bpy.context.scene.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("Fill", type='AREA')
    fill_data.energy = 3000.0
    fill_data.size = 30.0
    fill_data.color = (0.72, 0.80, 1.0)
    fill = bpy.data.objects.new("Fill", fill_data)
    fill.location = (-30.0, -26.0, 24.0)
    d = Vector((6.0, 4.0, 12.0)) - fill.location
    fill.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(fill)

    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(34.0)
    sky.sun_rotation = math.radians(38.0)
    sky.location = (-300, 0)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.9
    out = nt.nodes.new("ShaderNodeOutputWorld")
    out.location = (200, 0)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # ------------------------------------------------------------- camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 40.0
    cam_data.clip_end = 500.0
    cam_data.dof.use_dof = True
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (26.0, -32.0, 15.0)
    target = Vector((0.0, 0.0, 16.5))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.focus_distance = (target - cam.location).length
    cam_data.dof.aperture_fstop = 8.0
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    bpy.context.view_layer.update()


if __name__ == "__main__":
    main()
