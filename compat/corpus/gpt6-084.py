import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=0.4, transmission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.46
    return m

def lathe(name, profile, material, segments=128):
    # Profile travels around the solid cross-section; zero-radius ends are poles.
    verts, rings, faces = [], [], []
    for r, z in profile:
        if r == 0:
            rings.append([len(verts)])
            verts.append((0, 0, z))
        else:
            ring = []
            for j in range(segments):
                a = 2*math.pi*j/segments
                ring.append(len(verts))
                verts.append((r*math.cos(a), r*math.sin(a), z))
            rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for j in range(segments):
            k = (j+1)%segments
            if len(a) == 1:
                faces.append((a[0], b[k], b[j]))
            elif len(b) == 1:
                faces.append((a[j], a[k], b[0]))
            else:
                faces.append((a[j], a[k], b[k], b[j]))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = True
    return ob

def cylinder(name, loc, radius, depth, material, bevel=0.02):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        mod = ob.modifiers.new('Fine edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def box(name, loc, size, material, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    mod = ob.modifiers.new('Rounded panel corners', 'BEVEL')
    mod.width = bevel
    mod.segments = 5
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def text(name, body, loc, size, material):
    c = bpy.data.curves.new(name, 'FONT')
    c.body = body
    c.align_x = 'CENTER'
    c.align_y = 'CENTER'
    c.size = size
    c.extrude = 0.0008
    c.bevel_depth = 0.0003
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2, 0, 0)
    o.data.materials.append(material)

clear = mat('Thick pale champagne glass', (0.97, 0.94, 0.83), 0, 0.08, 1)
liquid = mat('Amber eau de parfum', (0.86, 0.57, 0.18), 0, 0.12, 0.92)
liquid.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.36
absorb = liquid.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
absorb.inputs['Color'].default_value = (0.82, 0.44, 0.1, 1)
absorb.inputs['Density'].default_value = 0.32
liquid.node_tree.links.new(absorb.outputs['Volume'], liquid.node_tree.nodes.get('Material Output').inputs['Volume'])
gold = mat('Brushed pale gold', (0.72, 0.51, 0.23), 0.83, 0.24)
black = mat('Obsidian lacquer cap', (0.018, 0.023, 0.021), 0.25, 0.2)
paper = mat('Ivory label stock', (0.89, 0.84, 0.71), 0, 0.68)
ink = mat('Charcoal typography', (0.025, 0.035, 0.03), 0, 0.55)
floor = mat('Warm beige studio', (0.47, 0.42, 0.34), 0, 0.75)

# Continuous outer wall, lip, inner wall, and heavy bottom: an actual hollow bottle.
lathe('Hollow cylindrical glass bottle', [
    (0, 0.08), (0.72, 0.08), (0.86, 0.1), (0.94, 0.16),
    (0.975, 0.26), (0.98, 0.4), (0.98, 2.62), (0.965, 2.74),
    (0.91, 2.84), (0.73, 2.97), (0.43, 3.03), (0.36, 3.1),
    (0.36, 3.34), (0.32, 3.37), (0.285, 3.34), (0.285, 3.12),
    (0.36, 3.03), (0.69, 2.9), (0.84, 2.77), (0.875, 2.64),
    (0.875, 0.4), (0.84, 0.31), (0.73, 0.28), (0, 0.28)
], clear)
lathe('Perfume with shallow meniscus', [
    (0, 0.295), (0.73, 0.295), (0.83, 0.33), (0.86, 0.41),
    (0.86, 2.44), (0.855, 2.465), (0.83, 2.45), (0, 2.45)
], liquid)
cylinder('Gold neck collar', (0, 0, 3.18), 0.395, 0.22, gold, 0.018)
cylinder('Cap lower gold rim', (0, 0, 3.365), 0.6, 0.085, gold, 0.014)
cylinder('Cylindrical fitted cap', (0, 0, 3.76), 0.59, 0.72, black, 0.065)
cylinder('Cap top inset medallion', (0, 0, 4.123), 0.43, 0.018, gold, 0.012)
for j in range(72):
    a = 2*math.pi*j/72
    cylinder('Fine cap flute', (0.583*math.cos(a), 0.583*math.sin(a), 3.75), 0.008, 0.52, gold, 0.004)

# A shallow rigid label plaque intersects the curved glass at its rear edge.
box('Gold label panel backing', (0, -0.955, 1.66), (1.16, 0.145, 1.34), gold, 0.05)
box('Ivory label panel', (0, -1.035, 1.66), (1.075, 0.018, 1.255), paper, 0.008)
text('House mark', 'A U R E L', (0, -1.05, 2.08), 0.125, ink)
text('Perfume title', 'No. 08', (0, -1.05, 1.78), 0.255, ink)
text('Fragrance note', 'AMBER / IRIS', (0, -1.05, 1.5), 0.088, ink)
text('Concentration', 'EAU DE PARFUM', (0, -1.05, 1.29), 0.073, ink)
text('Volume', '50 ml  /  1.7 fl. oz.', (0, -1.05, 1.13), 0.058, ink)
box('Label rule upper', (0, -1.051, 1.94), (0.71, 0.005, 0.008), gold, 0.002)
box('Label rule lower', (0, -1.051, 1.39), (0.71, 0.005, 0.008), gold, 0.002)
cylinder('Product display dais', (0, 0, -0.035), 1.65, 0.21, floor, 0.06)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.145))
bpy.context.object.data.materials.append(floor)
world = bpy.data.worlds.new('Product studio')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[1].default_value = 0.25
for name, loc, energy, sx, sy in [
    ('Tall left softbox', (-3, -4, 5), 650, 2.0, 5),
    ('Right strip softbox', (3, -1, 4), 850, 1.4, 4),
    ('Back transmission light', (0, 3, 4.5), 1000, 3, 4),
    ('Top highlight', (0, 0, 7), 450, 3, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.shape = 'RECTANGLE'
    o.data.size = sx
    o.data.size_y = sy
    o.rotation_euler = (Vector((0, 0, 2))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(4.1, -10, 5.2))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 5.65
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.cycles.transmission_bounces = 12
scene.cycles.max_bounces = 16
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
