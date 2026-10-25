"""claude-144 -- A small stone chapel.

Pitched-roof nave, square bell tower over the entrance with belfry openings
and a bell, narrow lancet-proportioned windows with glazing, buttresses,
and a flight of entrance steps up to the plinth.

Builds the whole scene headlessly from factory startup. No rendering, no I/O.
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ---------------------------------------------------------------------------
# dimensions (metres)
# ---------------------------------------------------------------------------
GROUND_Z = -0.55           # exterior ground level
HW = 3.0                   # nave half width (outer face)
HL = 5.5                   # nave half length (outer face)
WALL_T = 0.35              # nave wall thickness
WALL_H = 3.9               # eaves / wall top
RIDGE = 5.9                # ridge height
OVER = 0.45                # roof overhang past the wall face
ROOF_T = 0.22              # roof slab thickness (vertical)
EAVE_TOP = WALL_H + 0.15   # roof upper surface where it crosses the wall
SLOPE = (RIDGE - EAVE_TOP) / HW
EAVE_X = HW + OVER
EAVE_Z = RIDGE - SLOPE * EAVE_X

TW = 1.3                   # tower half width (outer face)
TOWER_T = 0.3              # tower wall thickness
T_FRONT = -8.1             # tower front face
T_BACK = -5.5              # tower back face (meets the facade)
T_TOP = 8.4                # top of tower walls
CORN_H = 0.28              # belfry cornice
CORN_HW = 1.45
SPIRE_TOP = T_TOP + CORN_H + 2.95


# ---------------------------------------------------------------------------
# scene helpers
# ---------------------------------------------------------------------------
def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights,
                 bpy.data.cameras, bpy.data.worlds):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.7, metallic=0.0, transmission=0.0,
                  emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        return mat
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    for key in ("Transmission Weight", "Transmission"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = transmission
            break
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.5 if transmission > 0.0 else 1.45
    if emission is not None:
        for key in ("Emission Color", "Emission"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = (emission[0], emission[1],
                                                  emission[2], 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    if transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except (AttributeError, TypeError):
            pass
        if hasattr(mat, "surface_render_method"):
            try:
                mat.surface_render_method = 'BLENDED'
            except TypeError:
                pass
    return mat


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------------------
# geometry builder
# ---------------------------------------------------------------------------
class Builder:
    """Accumulates simple solids into one bmesh, then bakes an object."""

    def __init__(self):
        self.bm = bmesh.new()

    # --- primitives -------------------------------------------------------
    def add_box(self, size, center):
        sx, sy, sz = size
        if min(sx, sy, sz) <= 1e-6:
            return
        res = bmesh.ops.create_cube(self.bm, size=1.0)
        verts = res["verts"]
        bmesh.ops.scale(self.bm, vec=Vector((sx, sy, sz)), verts=verts)
        bmesh.ops.translate(self.bm, vec=Vector(center), verts=verts)

    def add_bounds(self, x0, x1, y0, y1, z0, z1):
        self.add_box((x1 - x0, y1 - y0, z1 - z0),
                     ((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5))

    def add_prism(self, profile, axis, t0, t1):
        """Extrude a 2D profile along `axis`.

        axis 'y': profile points are (x, z);  axis 'x': (y, z);  axis 'z': (x, y).
        """
        def co(p, t):
            if axis == 'y':
                return Vector((p[0], t, p[1]))
            if axis == 'x':
                return Vector((t, p[0], p[1]))
            return Vector((p[0], p[1], t))

        low = [self.bm.verts.new(co(p, t0)) for p in profile]
        high = [self.bm.verts.new(co(p, t1)) for p in profile]
        self.bm.faces.new(low)
        self.bm.faces.new(list(reversed(high)))
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            self.bm.faces.new((low[i], low[j], high[j], high[i]))

    def add_pyramid(self, center_xy, half, z0, z1):
        cx, cy = center_xy
        base = [(cx - half, cy - half), (cx + half, cy - half),
                (cx + half, cy + half), (cx - half, cy + half)]
        verts = [self.bm.verts.new(Vector((x, y, z0))) for x, y in base]
        apex = self.bm.verts.new(Vector((cx, cy, z1)))
        self.bm.faces.new(list(reversed(verts)))
        for i in range(4):
            self.bm.faces.new((verts[i], verts[(i + 1) % 4], apex))

    # --- walls with openings ---------------------------------------------
    def _panel(self, ua, ub, za, zb, v, thick, run):
        if ub - ua <= 1e-6 or zb - za <= 1e-6:
            return
        span = ub - ua
        mid = (ua + ub) * 0.5
        cz = (za + zb) * 0.5
        if run == 'x':
            self.add_box((span, thick, zb - za), (mid, v, cz))
        else:
            self.add_box((thick, span, zb - za), (v, mid, cz))

    def add_wall(self, u0, u1, v, thick, z0, z1, openings, run='x'):
        """Wall slab running along `run` (thickness across it), centred at `v`.

        Each opening is (u_center, u_width, z_bottom, z_top).  Openings may be
        stacked vertically at the same horizontal position; the wall is split
        into vertical columns and each column is filled between its gaps.
        """
        cuts = {u0, u1}
        for uc, uw, _za, _zb in openings:
            cuts.add(uc - uw * 0.5)
            cuts.add(uc + uw * 0.5)
        edges = sorted(u for u in cuts if u0 - 1e-9 <= u <= u1 + 1e-9)
        for ua, ub in zip(edges[:-1], edges[1:]):
            if ub - ua <= 1e-6:
                continue
            mid = (ua + ub) * 0.5
            gaps = sorted((max(za, z0), min(zb, z1)) for uc, uw, za, zb in openings
                          if uc - uw * 0.5 < mid < uc + uw * 0.5)
            cursor = z0
            for za, zb in gaps:
                self._panel(ua, ub, cursor, za, v, thick, run)
                cursor = max(cursor, zb)
            self._panel(ua, ub, cursor, z1, v, thick, run)

    # --- output -----------------------------------------------------------
    def to_object(self, name, material, smooth=False):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        self.bm = None
        if smooth:
            for poly in me.polygons:
                poly.use_smooth = True
        me.materials.append(material)
        obj = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(obj)
        return obj


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
reset_scene()
scene = bpy.context.scene

mat_stone = make_material("Chapel_Stone", (0.74, 0.70, 0.62), roughness=0.78)
mat_dressed = make_material("Dressed_Stone", (0.82, 0.79, 0.72), roughness=0.62)
mat_roof = make_material("Slate_Roof", (0.13, 0.14, 0.16), roughness=0.52)
mat_wood = make_material("Oak_Door", (0.20, 0.10, 0.05), roughness=0.55)
mat_metal = make_material("Bell_Bronze", (0.55, 0.38, 0.16), roughness=0.32,
                          metallic=1.0)
mat_glass = make_material("Window_Glass", (0.32, 0.45, 0.55), roughness=0.08,
                          transmission=0.9, emission=(0.9, 0.75, 0.45),
                          emission_strength=0.35)
mat_grass = make_material("Ground", (0.20, 0.26, 0.13), roughness=0.9)

# window schedule: nave side lancets, facade lancets, apse window, tower slits
NAVE_WIN = [(-2.6, 0.7, 1.4, 3.4), (0.0, 0.7, 1.4, 3.4), (2.6, 0.7, 1.4, 3.4)]
FACADE_WIN = [(-2.05, 0.55, 1.9, 3.3), (2.05, 0.55, 1.9, 3.3)]
BACK_WIN = [(0.0, 1.0, 1.5, 3.5)]
TOWER_SLIT = [(-6.8, 0.35, 3.8, 4.8)]
BELFRY = (0.0, 1.1, 6.5, 7.9)
DOOR = (0.0, 1.4, 0.0, 2.6)
NAVE_DOORWAY = (0.0, 1.4, 0.0, 2.7)

# --- masonry ---------------------------------------------------------------
stone = Builder()

# plinth under the nave and under the tower
stone.add_bounds(-HW - 0.2, HW + 0.2, -HL - 0.2, HL + 0.2, GROUND_Z, 0.0)
stone.add_bounds(-TW - 0.2, TW + 0.2, T_FRONT - 0.2, T_BACK, GROUND_Z, 0.0)

# nave long walls (three lancets each)
for sign in (-1.0, 1.0):
    stone.add_wall(-HL, HL, sign * (HW - WALL_T * 0.5), WALL_T, 0.0, WALL_H,
                   NAVE_WIN, run='y')

# facade (doorway through into the tower porch) and rear wall
stone.add_wall(-HW, HW, -(HL - WALL_T * 0.5), WALL_T, 0.0, WALL_H,
               [NAVE_DOORWAY] + FACADE_WIN, run='x')
stone.add_wall(-HW, HW, HL - WALL_T * 0.5, WALL_T, 0.0, WALL_H,
               BACK_WIN, run='x')

# gable triangles, tucked just under the roof slabs
GABLE_APEX = RIDGE - 0.24
gable = [(-HW, WALL_H), (HW, WALL_H), (0.0, GABLE_APEX)]
stone.add_prism(gable, 'y', -HL, -HL + WALL_T)
stone.add_prism(gable, 'y', HL - WALL_T, HL)

# string course below the eaves
stone.add_bounds(-HW - 0.12, HW + 0.12, -HL - 0.12, HL + 0.12, 3.72, 3.86)

# buttresses between the lancets
for sy in (-3.9, -1.3, 1.3, 3.9):
    for sx in (-1.0, 1.0):
        stone.add_box((0.32, 0.55, 3.3), (sx * (HW + 0.14), sy, 1.65))
        stone.add_prism([(-0.275, 3.3), (0.275, 3.3), (0.275, 3.05)], 'x',
                        sx * (HW - 0.02), sx * (HW + 0.3))

# window sills and hood mouldings (nave sides)
for sign in (-1.0, 1.0):
    for uc, uw, za, zb in NAVE_WIN:
        stone.add_box((0.26, uw + 0.3, 0.12), (sign * (HW + 0.05), uc, za - 0.06))
        stone.add_box((0.22, uw + 0.4, 0.14), (sign * (HW + 0.03), uc, zb + 0.07))
for uc, uw, za, zb in FACADE_WIN:
    stone.add_box((uw + 0.3, 0.24, 0.12), (uc, -(HL + 0.04), za - 0.06))
for uc, uw, za, zb in BACK_WIN:
    stone.add_box((uw + 0.34, 0.26, 0.12), (uc, HL + 0.05, za - 0.06))
    stone.add_box((uw + 0.44, 0.22, 0.14), (uc, HL + 0.03, zb + 0.07))

# --- bell tower ------------------------------------------------------------
# front wall: door, slit, belfry opening stacked on the same centre line
stone.add_wall(-TW, TW, T_FRONT + TOWER_T * 0.5, TOWER_T, 0.0, T_TOP,
               [DOOR, (0.0, 0.35, 3.4, 4.4), BELFRY], run='x')
# back wall: sits against the facade, doorway aligned with the nave doorway
stone.add_wall(-TW, TW, T_BACK - TOWER_T * 0.5, TOWER_T, 0.0, T_TOP,
               [DOOR, BELFRY], run='x')
# side walls
for sign in (-1.0, 1.0):
    stone.add_wall(T_FRONT, T_BACK, sign * (TW - TOWER_T * 0.5), TOWER_T,
                   0.0, T_TOP, TOWER_SLIT + [BELFRY], run='y')

TOWER_CY = (T_FRONT + T_BACK) * 0.5
# belfry cornice and a lower offset band
stone.add_box((2 * CORN_HW, 2 * CORN_HW, CORN_H), (0.0, TOWER_CY, T_TOP + CORN_H * 0.5))
stone.add_box((2 * TW + 0.16, 2.6 + 0.16, 0.16), (0.0, TOWER_CY, 6.24))
stone.add_box((2 * TW + 0.2, 2.6 + 0.2, 0.18), (0.0, TOWER_CY, 0.09))
# belfry opening surrounds
for sign in (-1.0, 1.0):
    stone.add_box((0.18, BELFRY[1] + 0.4, 0.14),
                  (sign * (TW + 0.02), TOWER_CY, BELFRY[3] + 0.07))
    stone.add_box((BELFRY[1] + 0.4, 0.18, 0.14),
                  (0.0, TOWER_CY + sign * (1.3 + 0.02), BELFRY[3] + 0.07))

# --- entrance steps --------------------------------------------------------
for i, (half_w, tread) in enumerate(((1.5, 1.25), (1.35, 0.85), (1.2, 0.45))):
    top = GROUND_Z + 0.1375 * (i + 1)
    stone.add_bounds(-half_w, half_w, T_FRONT - tread, T_FRONT + 0.05,
                     GROUND_Z - 0.05, top)

stone_obj = stone.to_object("Chapel_Masonry", mat_stone)

# --- roof, spire, ridge ----------------------------------------------------
roof = Builder()
roof_profile = [
    (-EAVE_X, EAVE_Z), (0.0, RIDGE), (EAVE_X, EAVE_Z),
    (EAVE_X, EAVE_Z - ROOF_T), (0.0, RIDGE - ROOF_T), (-EAVE_X, EAVE_Z - ROOF_T),
]
roof.add_prism(roof_profile, 'y', -HL, HL + OVER)
# fascia boards along the eaves
for sign in (-1.0, 1.0):
    roof.add_box((0.1, 2 * HL + OVER, 0.2),
                 (sign * (EAVE_X + 0.05), (-HL + HL + OVER) * 0.5, EAVE_Z - 0.13))
# ridge cap
roof.add_box((0.3, 2 * HL + OVER, 0.14), (0.0, OVER * 0.5, RIDGE + 0.04))
# tower spire and its finial base
roof.add_pyramid((0.0, TOWER_CY), CORN_HW, T_TOP + CORN_H, SPIRE_TOP)
roof_obj = roof.to_object("Chapel_Roof", mat_roof)

# --- glazing ---------------------------------------------------------------
glass = Builder()
for sign in (-1.0, 1.0):
    for uc, uw, za, zb in NAVE_WIN:
        glass.add_box((0.07, uw - 0.06, zb - za - 0.06),
                      (sign * (HW - WALL_T * 0.5), uc, (za + zb) * 0.5))
for uc, uw, za, zb in FACADE_WIN:
    glass.add_box((uw - 0.06, 0.07, zb - za - 0.06),
                  (uc, -(HL - WALL_T * 0.5), (za + zb) * 0.5))
for uc, uw, za, zb in BACK_WIN:
    glass.add_box((uw - 0.06, 0.07, zb - za - 0.06),
                  (uc, HL - WALL_T * 0.5, (za + zb) * 0.5))
for sign in (-1.0, 1.0):
    for uc, uw, za, zb in TOWER_SLIT:
        glass.add_box((0.06, uw - 0.05, zb - za - 0.05),
                      (sign * (TW - TOWER_T * 0.5), uc, (za + zb) * 0.5))
glass.add_box((0.3, 0.06, 0.95), (0.0, T_FRONT + TOWER_T * 0.5, 3.9))
glass_obj = glass.to_object("Chapel_Glazing", mat_glass)

# --- oak door, mullions, bell yoke ----------------------------------------
wood = Builder()
DOOR_Y = T_FRONT + TOWER_T * 0.5
wood.add_box((1.32, 0.09, 2.5), (0.0, DOOR_Y, 1.25))
for gx in (-0.44, 0.0, 0.44):                      # plank grooves
    wood.add_box((0.035, 0.05, 2.44), (gx, DOOR_Y - 0.06, 1.25))
for uc, uw, za, zb in NAVE_WIN:                    # window mullions
    for sign in (-1.0, 1.0):
        wood.add_box((0.09, 0.06, zb - za - 0.06),
                     (sign * (HW - WALL_T * 0.5), uc, (za + zb) * 0.5))
        wood.add_box((0.09, uw - 0.06, 0.06),
                     (sign * (HW - WALL_T * 0.5), uc, za + (zb - za) * 0.62))
wood.add_box((1.05, 0.14, 0.14), (0.0, TOWER_CY, 7.66))   # bell yoke
wood_obj = wood.to_object("Chapel_Joinery", mat_wood)

# --- ironmongery and the cross --------------------------------------------
metal = Builder()
for z in (0.62, 1.92):
    metal.add_box((1.28, 0.12, 0.11), (0.0, DOOR_Y - 0.01, z))
metal.add_box((0.09, 0.16, 0.28), (0.5, DOOR_Y - 0.09, 1.25))   # handle plate
metal.add_box((0.09, 0.09, 0.22), (0.0, TOWER_CY, 7.48))        # bell hanger
metal.add_box((0.1, 0.1, 1.1), (0.0, TOWER_CY, SPIRE_TOP + 0.55))
metal.add_box((0.5, 0.09, 0.1), (0.0, TOWER_CY, SPIRE_TOP + 0.78))
metal_obj = metal.to_object("Chapel_Ironwork", mat_metal)

# --- bell (lathe-like body from a truncated cone) -------------------------
bpy.ops.mesh.primitive_cone_add(vertices=28, radius1=0.36, radius2=0.15,
                                depth=0.52, location=(0.0, TOWER_CY, 7.2))
bell = bpy.context.active_object
bell.name = "Bell"
bell.data.materials.append(mat_metal)
for poly in bell.data.polygons:
    poly.use_smooth = True

bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.155,
                                     location=(0.0, TOWER_CY, 7.44))
crown = bpy.context.active_object
crown.name = "Bell_Crown"
crown.scale = (1.0, 1.0, 0.55)
crown.data.materials.append(mat_metal)
for poly in crown.data.polygons:
    poly.use_smooth = True

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.085,
                                     location=(0.0, TOWER_CY, 7.02))
clapper = bpy.context.active_object
clapper.name = "Bell_Clapper"
clapper.data.materials.append(mat_metal)
for poly in clapper.data.polygons:
    poly.use_smooth = True

# --- ground ----------------------------------------------------------------
ground = Builder()
ground.add_box((70.0, 70.0, 0.3), (0.0, 0.0, GROUND_Z - 0.15))
ground_obj = ground.to_object("Ground", mat_grass)

# a modest gravel path leading away from the steps
path = Builder()
path.add_box((2.6, 9.0, 0.06), (0.0, T_FRONT - 5.6, GROUND_Z + 0.02))
path_obj = path.to_object("Path", mat_dressed)

# ---------------------------------------------------------------------------
# lighting
# ---------------------------------------------------------------------------
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun_data.angle = math.radians(1.5)
sun_data.color = (1.0, 0.94, 0.84)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(54.0), math.radians(6.0), math.radians(38.0))
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("SkyFill", type='AREA')
fill_data.energy = 900.0
fill_data.shape = 'RECTANGLE'
fill_data.size = 16.0
fill_data.size_y = 10.0
fill_data.color = (0.72, 0.82, 1.0)
fill = bpy.data.objects.new("SkyFill", fill_data)
fill.location = (-13.0, -13.0, 11.0)
bpy.context.collection.objects.link(fill)
look_at(fill, (0.0, -2.5, 3.5))

warm_data = bpy.data.lights.new("InteriorGlow", type='POINT')
warm_data.energy = 220.0
warm_data.color = (1.0, 0.72, 0.42)
warm_data.shadow_soft_size = 0.8
warm = bpy.data.objects.new("InteriorGlow", warm_data)
warm.location = (0.0, 1.0, 2.2)
bpy.context.collection.objects.link(warm)

world = bpy.data.worlds.new("ChapelWorld")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.42, 0.56, 0.78, 1.0)
    bg.inputs["Strength"].default_value = 1.0
scene.world = world

# ---------------------------------------------------------------------------
# camera
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam_data.clip_end = 400.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (12.5, -16.5, 7.6)
bpy.context.collection.objects.link(cam)
look_at(cam, (0.0, -3.2, 3.8))
scene.camera = cam

print("Chapel scene built: %d objects" % len(bpy.data.objects))
