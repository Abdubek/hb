"""claude-015 - Three-story building facade with balconies (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

TAU = 2.0 * math.pi


# --------------------------------------------------------------------- helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    try:
        s.cycles.samples = 128
    except Exception:
        pass
    s.render.resolution_x, s.render.resolution_y = 1600, 1200
    return s


def sky_world(top=(0.20, 0.34, 0.58), strength=1.6):
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs[1].default_value = strength
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = 'EASING'
    grad.location = (-600, 0)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-380, 0)
    ramp.color_ramp.elements[0].color = (0.55, 0.55, 0.52, 1.0)
    ramp.color_ramp.elements[1].color = (top[0], top[1], top[2], 1.0)
    tex = nt.nodes.new("ShaderNodeTexCoord")
    tex.location = (-800, 0)
    map_r = nt.nodes.new("ShaderNodeMapping")
    map_r.location = (-720, -200)
    nt.links.new(tex.outputs["Generated"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs[0])
    bpy.context.scene.world = w


def mat(name, col, rough=0.5, metal=0.0, alpha=1.0, ior=1.45, trans=0.0, coat=0.0,
        emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in (("IOR", ior), ("Alpha", alpha), ("Transmission Weight", trans),
                 ("Coat Weight", coat)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    if emit is not None and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        b.inputs["Emission Strength"].default_value = estr
    if alpha < 1.0 or trans > 0.0:
        for attr, val in (("blend_method", 'BLEND'), ("surface_render_method", 'BLENDED')):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    return m


def _x(bm, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    M = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector(scale)).to_4x4())
    for v in bm.verts:
        v.co = M @ v.co
    return bm


def box(size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, seg=1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=seg, affect='EDGES', profile=0.5,
                        clamp_overlap=True)
    return _x(bm, loc, rot)


def span(x0, x1, y0, y1, z0, z1, bevel=0.0, seg=1):
    """Axis-aligned box from opposite corners."""
    return box((x1 - x0, y1 - y0, z1 - z0),
               ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), bevel=bevel, seg=seg)


def cyl(r, d, seg=16, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=d)
    if smooth:
        for f in bm.faces:
            if abs(f.normal.z) < 0.9:
                f.smooth = True
    return _x(bm, loc, rot)


def ball(r, loc=(0, 0, 0), sub=2, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for f in bm.faces:
        f.smooth = True
    return _x(bm, loc, (0, 0, 0), scale)


def prism(bw, bd, tw, td, h, loc=(0, 0, 0), rot=(0, 0, 0)):
    bm = bmesh.new()
    q = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    b = [bm.verts.new((x * bw / 2, y * bd / 2, -h / 2)) for x, y in q]
    t = [bm.verts.new((x * tw / 2, y * td / 2, h / 2)) for x, y in q]
    bm.faces.new(b)
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([b[i], b[j], t[j], t[i]])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return _x(bm, loc, rot)


def join(bm, tmp, mi=0):
    tmp.verts.index_update()
    vs = [bm.verts.new(v.co) for v in tmp.verts]
    for f in tmp.faces:
        try:
            nf = bm.faces.new([vs[v.index] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = f.smooth
        nf.material_index = mi
    tmp.free()


def obj(name, bm, mats, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.validate()
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]):
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    return o


def cam(loc, tgt, lens=40.0, fstop=None, shift_y=0.0):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cd.shift_y = shift_y
    c = bpy.data.objects.new("Camera", cd)
    c.location = loc
    d = Vector(tgt) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if fstop:
        cd.dof.use_dof = True
        cd.dof.focus_distance = d.length
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.collection.objects.link(c)
    bpy.context.scene.camera = c
    return c


def sun(name, energy, rot, col=(1.0, 0.95, 0.88), angle=0.02):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = energy
    ld.color = col
    ld.angle = angle
    o = bpy.data.objects.new(name, ld)
    o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    return o


def area(name, loc, tgt, size, energy, col=(1, 1, 1), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = col
    if size_y:
        ld.shape = 'RECTANGLE'
        ld.size_y = size_y
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(o)
    return o


# ---------------------------------------------------------------- scene layout
W = 12.0            # facade width
T = 0.40            # wall thickness (front face at y = 0, interior at y = +T)
FH = 3.40           # floor height
NFL = 3
H = FH * NFL
XS = (-4.8, -2.4, 0.0, 2.4, 4.8)


def opening_list():
    """(x0, x1, z0, z1, kind, xc, floor) for every void in the wall."""
    out = []
    for fl in range(NFL):
        fz = fl * FH
        for xc in XS:
            if fl == 0 and abs(xc) < 0.01:
                w, z0, z1, kind = 1.90, 0.0, 2.80, 'door'
            elif (fl == 1 and abs(xc) < 2.5) or (fl == 2 and abs(xc) > 3.0):
                w, z0, z1, kind = 1.30, fz + 0.25, fz + 2.60, 'french'
            else:
                w, z0, z1, kind = 1.30, fz + 0.95, fz + 2.60, 'window'
            out.append((xc - w / 2.0, xc + w / 2.0, z0, z1, kind, xc, fl))
    return out


def build_wall(bm, ops):
    """Sweep unique x columns and fill the gaps between openings with wall boxes."""
    xs = sorted(set([-W / 2.0, W / 2.0] + [o[0] for o in ops] + [o[1] for o in ops]))
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        if x1 - x0 < 1e-4:
            continue
        xc = (x0 + x1) / 2.0
        col = sorted([o for o in ops if o[0] <= xc <= o[1]], key=lambda o: o[2])
        z = 0.0
        for o in col:
            if o[2] - z > 1e-4:
                join(bm, span(x0, x1, 0.0, T, z, o[2]), 0)
            z = max(z, o[3])
        if H - z > 1e-4:
            join(bm, span(x0, x1, 0.0, T, z, H), 0)


def frame(bm, x0, x1, z0, z1, w, y0, y1, mi=0):
    join(bm, span(x0, x1, y0, y1, z0, z0 + w), mi)
    join(bm, span(x0, x1, y0, y1, z1 - w, z1), mi)
    join(bm, span(x0, x0 + w, y0, y1, z0 + w, z1 - w), mi)
    join(bm, span(x1 - w, x1, y0, y1, z0 + w, z1 - w), mi)


def balcony(name, xc, width, fz, m_stone, m_metal):
    bm = bmesh.new()
    sw = width + 0.50
    top = fz + 0.22
    join(bm, span(xc - sw / 2, xc + sw / 2, -1.25, 0.05, top - 0.16, top), 0)
    join(bm, span(xc - sw / 2 - 0.05, xc + sw / 2 + 0.05, -1.32, 0.05,
                  top - 0.22, top - 0.16), 0)
    for f in (-0.36, 0.0, 0.36):
        join(bm, prism(0.26, 0.62, 0.20, 0.30, 0.44,
                       (xc + f * sw, -0.30, top - 0.44)), 0)
    rh = 1.05
    x0, x1 = xc - sw / 2 + 0.05, xc + sw / 2 - 0.05
    yb, yf = 0.02, -1.18
    for px, py in ((x0, yb), (x0, yf), (x1, yf), (x1, yb)):
        join(bm, box((0.07, 0.07, rh), (px, py, top + rh / 2.0)), 1)
    for zr, rr in ((top + rh, 0.032), (top + 0.10, 0.024)):
        join(bm, span(x0, x1, yf - rr, yf + rr, zr - rr, zr + rr), 1)
        for px in (x0, x1):
            join(bm, span(px - rr, px + rr, yf, yb, zr - rr, zr + rr), 1)
    step = 0.155
    n = max(2, int((x1 - x0) / step))
    for i in range(1, n):
        bx = x0 + (x1 - x0) * i / n
        join(bm, cyl(0.017, rh - 0.10, seg=10, loc=(bx, yf, top + 0.10 + (rh - 0.10) / 2)), 1)
    m = max(2, int((yb - yf) / step))
    for px in (x0, x1):
        for i in range(1, m):
            by = yf + (yb - yf) * i / m
            join(bm, cyl(0.017, rh - 0.10, seg=10,
                         loc=(px, by, top + 0.10 + (rh - 0.10) / 2)), 1)
    return obj(name, bm, [m_stone, m_metal])


def main():
    reset()
    sky_world()

    m_stucco = mat("Stucco", (0.60, 0.55, 0.47), 0.72)
    m_stone = mat("Limestone", (0.72, 0.70, 0.64), 0.60)
    m_trim = mat("PaintedTrim", (0.88, 0.87, 0.83), 0.45, coat=0.15)
    m_frame = mat("WindowFrame", (0.16, 0.17, 0.16), 0.40, coat=0.2)
    m_glass = mat("Glazing", (0.10, 0.16, 0.20), 0.05, alpha=0.45, trans=0.7, ior=1.52)
    m_int = mat("Interior", (0.02, 0.02, 0.025), 0.8)
    m_metal = mat("Ironwork", (0.045, 0.048, 0.05), 0.30, metal=0.9)
    m_door = mat("DoorWood", (0.085, 0.035, 0.028), 0.35, coat=0.35)
    m_brass = mat("Brass", (0.62, 0.48, 0.20), 0.25, metal=1.0)
    m_lamp = mat("Sconce", (0.9, 0.8, 0.6), 0.3, emit=(1.0, 0.82, 0.55), estr=18.0)
    m_leaf = mat("Planting", (0.10, 0.28, 0.11), 0.65)
    m_pave = mat("Pavement", (0.24, 0.235, 0.23), 0.72)
    m_road = mat("Asphalt", (0.09, 0.09, 0.095), 0.65)

    ops = opening_list()

    # ----------------------------------------------------------------- ground
    obj("Road", box((80.0, 80.0, 0.20), (0, -20.0, -0.10)), m_road)
    obj("Sidewalk", box((60.0, 6.0, 0.22), (0, -3.0, -0.11)), m_pave)
    obj("Curb", box((60.0, 0.30, 0.34), (0, -6.0, -0.03)), m_stone)

    # ------------------------------------------------------------------- wall
    bm = bmesh.new()
    build_wall(bm, ops)
    for sx in (-1, 1):
        join(bm, span(sx * (W / 2 - 0.35), sx * W / 2, T, 3.2, 0.0, H), 0)
    join(bm, span(-W / 2, W / 2, T, 3.2, H - 0.35, H), 0)
    obj("Facade_Wall", bm, m_stucco)

    # ------------------------------------------------- plinth, courses, cornice
    dx0, dx1 = -0.95, 0.95
    bm = bmesh.new()
    join(bm, span(-W / 2 - 0.10, dx0 - 0.28, -0.10, 0.05, 0.0, 0.72), 0)
    join(bm, span(dx1 + 0.28, W / 2 + 0.10, -0.10, 0.05, 0.0, 0.72), 0)
    for fl in (1, 2):
        join(bm, span(-W / 2 - 0.12, W / 2 + 0.12, -0.16, 0.05,
                      fl * FH - 0.12, fl * FH + 0.10), 0)
    join(bm, span(-W / 2 - 0.18, W / 2 + 0.18, -0.22, 0.05, H - 0.10, H + 0.16), 0)
    join(bm, span(-W / 2 - 0.30, W / 2 + 0.30, -0.36, 0.05, H + 0.16, H + 0.36), 0)
    join(bm, span(-W / 2 - 0.05, W / 2 + 0.05, -0.10, T + 0.02, H + 0.36, H + 1.18), 0)
    join(bm, span(-W / 2 - 0.14, W / 2 + 0.14, -0.20, T + 0.10, H + 1.18, H + 1.30), 0)
    # quoin blocks at both corners
    z = 0.75
    i = 0
    while z < H - 0.4:
        bw = 0.62 if i % 2 == 0 else 0.42
        for sx in (-1, 1):
            join(bm, span(sx * W / 2 - bw if sx > 0 else -W / 2,
                          sx * W / 2 if sx > 0 else -W / 2 + bw,
                          -0.09, 0.05, z, z + 0.42), 0)
        z += 0.46
        i += 1
    obj("Facade_Stonework", bm, m_stone)

    # ------------------------------------------------- windows, doors, dressing
    bm_fr = bmesh.new()
    bm_tr = bmesh.new()
    bm_gl = bmesh.new()
    bm_in = bmesh.new()
    for x0, x1, z0, z1, kind, xc, fl in ops:
        if kind == 'door':
            continue
        frame(bm_fr, x0 + 0.02, x1 - 0.02, z0 + 0.02, z1 - 0.02, 0.10, -0.03, 0.16)
        mz = z0 + (z1 - z0) * (0.62 if kind == 'window' else 0.70)
        join(bm_fr, span(xc - 0.028, xc + 0.028, -0.01, 0.14, z0 + 0.10, z1 - 0.10), 0)
        join(bm_fr, span(x0 + 0.10, x1 - 0.10, -0.01, 0.14, mz - 0.030, mz + 0.030), 0)
        join(bm_gl, span(x0 + 0.10, x1 - 0.10, 0.10, 0.13, z0 + 0.10, z1 - 0.10), 0)
        join(bm_in, span(x0 + 0.04, x1 - 0.04, T - 0.03, T, z0 + 0.04, z1 - 0.04), 0)
        # sill / threshold and architrave with keystone
        if kind == 'window':
            join(bm_tr, span(x0 - 0.20, x1 + 0.20, -0.22, 0.06, z0 - 0.10, z0 + 0.02), 0)
            join(bm_tr, span(x0 - 0.26, x1 + 0.26, -0.26, 0.06, z0 - 0.16, z0 - 0.10), 0)
        else:
            join(bm_tr, span(x0 - 0.06, x1 + 0.06, -0.12, 0.06, z0 - 0.06, z0 + 0.02), 0)
        join(bm_tr, span(x0 - 0.22, x1 + 0.22, -0.18, 0.06, z1 - 0.02, z1 + 0.16), 0)
        join(bm_tr, span(xc - 0.13, xc + 0.13, -0.24, 0.06, z1 - 0.06, z1 + 0.30), 0)
    obj("Window_Frames", bm_fr, m_frame)
    obj("Window_Dressing", bm_tr, m_trim)
    obj("Glazing", bm_gl, m_glass)
    obj("Interiors", bm_in, m_int)

    # ------------------------------------------------------------ entrance door
    bm = bmesh.new()
    frame(bm, dx0 - 0.02, dx1 + 0.02, 0.0, 2.86, 0.16, -0.10, 0.20, 0)
    join(bm, span(dx0 + 0.14, dx1 - 0.14, -0.02, 0.06, 2.06, 2.18), 0)
    obj("Door_Frame", bm, m_trim)

    bm = bmesh.new()
    for sx in (-1, 1):
        cx = sx * 0.44
        join(bm, box((0.84, 0.07, 1.92), (cx, 0.09, 1.05), bevel=0.01), 0)
        for pz, ph in ((0.50, 0.62), (1.42, 0.76)):
            join(bm, box((0.56, 0.075, ph), (cx, 0.055, pz), bevel=0.02), 0)
    obj("Door_Leaves", bm, m_door)

    bm = bmesh.new()
    for sx in (-1, 1):
        join(bm, cyl(0.022, 0.20, seg=14, loc=(sx * 0.10, -0.02, 1.05),
                     rot=(0, math.pi / 2, 0)), 0)
        join(bm, ball(0.05, (sx * 0.16, 0.02, 1.05), sub=2), 0)
    obj("Door_Hardware", bm, m_brass)
    join_bm = bmesh.new()
    join(join_bm, span(dx0 + 0.16, dx1 - 0.16, 0.06, 0.10, 2.20, 2.80), 0)
    obj("Fanlight_Glass", join_bm, m_glass)
    bm = bmesh.new()
    for i in range(5):
        a = math.pi * (0.12 + 0.19 * i)
        join(bm, cyl(0.022, 0.60, seg=8, loc=(math.cos(a) * 0.30, 0.08, 2.22 + math.sin(a) * 0.28),
                     rot=(0, a - math.pi / 2, 0)), 0)
    join(bm, span(dx0 + 0.16, dx1 - 0.16, 0.05, 0.11, 2.20, 2.24), 0)
    obj("Fanlight_Bars", bm, m_frame)

    bm = bmesh.new()
    for i, (w, d, h) in enumerate(((3.00, 0.36, 0.16), (3.30, 0.30, 0.14))):
        join(bm, span(-1.50, 1.50, -1.30 - i * 0.10, 0.05, 3.02 + i * 0.16,
                      3.02 + i * 0.16 + h), 0)
    for sx in (-1, 1):
        join(bm, prism(0.18, 0.90, 0.14, 0.24, 0.70, (sx * 1.20, -0.45, 2.66)), 0)
    for i in range(3):
        join(bm, span(-1.75 + i * 0.0, 1.75, -0.05, 0.05, 0.0, 0.0), 0)
    obj("Door_Canopy", bm, m_stone)

    bm = bmesh.new()
    for i, w in enumerate((3.10, 3.34, 3.58)):
        join(bm, span(-w / 2, w / 2, -0.55 - i * 0.34, 0.02,
                      0.30 - i * 0.155, 0.455 - i * 0.155), 0)
    obj("Entrance_Steps", bm, m_stone)

    bm = bmesh.new()
    for sx in (-1, 1):
        join(bm, box((0.12, 0.12, 0.34), (sx * 1.28, -0.10, 2.52)), 0)
        join(bm, prism(0.30, 0.30, 0.16, 0.16, 0.36, (sx * 1.28, -0.22, 2.32)), 0)
    obj("Sconce_Bodies", bm, m_metal)
    bm = bmesh.new()
    for sx in (-1, 1):
        join(bm, ball(0.09, (sx * 1.28, -0.22, 2.26), sub=2), 0)
    obj("Sconce_Lamps", bm, m_lamp)

    # ------------------------------------------------------------- balconies
    for i, (xc, wid, fl) in enumerate([(-2.4, 2.0, 1), (0.0, 2.0, 1), (2.4, 2.0, 1),
                                       (-4.8, 2.2, 2), (4.8, 2.2, 2)]):
        balcony("Balcony_%d" % i, xc, wid, fl * FH, m_stone, m_metal)

    # ----------------------------------------------- ground-floor window boxes
    bm_b = bmesh.new()
    bm_p = bmesh.new()
    for xc in (-4.8, 4.8):
        join(bm_b, span(xc - 0.75, xc + 0.75, -0.48, -0.06, 0.72, 1.06), 0)
        for k in range(7):
            px = xc - 0.62 + k * 0.205
            join(bm_p, ball(0.15, (px, -0.27, 1.10), sub=2, scale=(1.0, 1.0, 0.7)), 0)
    obj("WindowBoxes", bm_b, m_stone)
    obj("WindowBox_Planting", bm_p, m_leaf)

    # -------------------------------------------------------- camera and lights
    cam((-9.5, -20.0, 6.2), (0.0, 0.6, 5.2), lens=42.0, fstop=11.0)
    sun("Sun", 4.2, (math.radians(56.0), math.radians(14.0), math.radians(-118.0)),
        (1.0, 0.94, 0.84), angle=math.radians(1.2))
    area("SkyFill", (-6.0, -22.0, 14.0), (0, 0, 5.0), 18.0, 4000.0, (0.72, 0.82, 1.0))
    area("Bounce", (2.0, -12.0, 1.2), (0, 0, 3.0), 14.0, 1200.0, (1.0, 0.93, 0.82))


main()
