import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0,roughness=0.6):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name,loc,size,material,bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft edges','BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def tube(name,points,radius,material):
    c = bpy.data.curves.new(name,'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 2
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points):
        p.co = (*co,1)
    o = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    c.materials.append(material)
    return o

def cylinder(name,loc,radius,depth,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    b = o.modifiers.new('Rim rounding','BEVEL')
    b.width = min(0.009,radius/4)
    b.segments = 2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

cream = mat('Natural ivory canvas',(0.93,0.86,0.67),roughness=0.93)
colors = [mat('Lagoon turquoise canvas',(0.025,0.48,0.49),roughness=0.87),mat('Coral canvas',(0.91,0.23,0.13),roughness=0.87),mat('Golden canvas',(0.95,0.61,0.07),roughness=0.87)]
wood = mat('Oiled beech poles',(0.55,0.33,0.13),roughness=0.48)
frame = mat('White enamel chair tubing',(0.89,0.91,0.87),0.35,0.35)
ribmat = mat('Umbrella ribs',(0.35,0.30,0.22),0.55,0.46)
rubber = mat('Chair foot caps',(0.11,0.13,0.12),roughness=0.86)
sand = mat('Fine warm sand',(0.71,0.57,0.37),roughness=0.98)
# Procedural sand and subtle canvas grain require no image files.
n,l = sand.node_tree.nodes,sand.node_tree.links
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 150
noise.inputs['Detail'].default_value = 2
bump = n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.25
bump.inputs['Distance'].default_value = 0.025
l.new(noise.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
for m in [cream]+colors:
    n,l = m.node_tree.nodes,m.node_tree.links
    noise = n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 170
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.13
    bump.inputs['Distance'].default_value = 0.001
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
box('Beach sand',(0,0,-0.11),(200,200,0.20),sand,0)

# Eight independently colored, curved canopy gores with scalloped valances.
def umbrella(cx,cy,index):
    radius,peak = 1.43,2.73
    cylinder('Beech umbrella mast',(cx,cy,1.37),0.027,2.75,wood)
    cylinder('Sliding rib hub',(cx,cy,2.12),0.064,0.105,ribmat)
    def canopy_point(r,t):
        return (cx+r*math.cos(t),cy+r*math.sin(t),peak-0.57*(r/radius)**0.72)
    for sector in range(8):
        a0 = sector*math.tau/8
        material = colors[index] if sector%2==0 else cream
        verts = [(cx,cy,peak)]
        faces = []
        nr,nt = 10,8
        for j in range(1,nr+1):
            r = radius*j/nr
            for k in range(nt+1):
                t = a0+math.tau/8*k/nt
                x,y,z = canopy_point(r,t)
                z -= 0.038*math.sin(math.pi*k/nt)*(r/radius)**1.6
                verts.append((x,y,z))
        for k in range(nt):
            faces.append((0,1+k,2+k))
        for j in range(nr-1):
            a = 1+j*(nt+1)
            b = a+nt+1
            for k in range(nt):
                faces.append((a+k,b+k,b+k+1,a+k+1))
        edge = 1+(nr-1)*(nt+1)
        lower = len(verts)
        for k in range(nt+1):
            x,y,z = verts[edge+k]
            verts.append((x,y,z-0.075-0.075*math.sin(math.pi*k/nt)))
        for k in range(nt):
            faces.append((edge+k,lower+k,lower+k+1,edge+k+1))
        mesh = bpy.data.meshes.new('Curved canopy panel mesh')
        mesh.from_pydata(verts,[],faces)
        mesh.update()
        o = bpy.data.objects.new('Umbrella %d panel %d' % (index+1,sector+1),mesh)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(material)
        for f in mesh.polygons:
            f.use_smooth = True
        s = o.modifiers.new('Canvas thickness','SOLIDIFY')
        s.thickness = 0.002
        seam = [canopy_point(radius*j/20,a0) for j in range(21)]
        tube('Canopy stitched seam',seam,0.004,cream)
        tube('Underside radial rib',[(x,y,z-0.014) for x,y,z in seam],0.007,ribmat)
        x,y,z = canopy_point(radius*0.55,a0)
        tube('Rib supporting strut',[(cx,cy,2.12),(x,y,z-0.025)],0.007,ribmat)
        tube('Scalloped canopy hem',verts[lower:lower+nt+1],0.004,cream)
    cylinder('Top finial',(cx,cy,peak+0.046),0.046,0.10,wood)

# Reclining sling chairs have articulated profiles, leg frames and striped fabric.
def lounge(cx,cy,angle,index):
    def p(x,y,z):
        return (cx+x*math.cos(angle)-y*math.sin(angle),cy+x*math.sin(angle)+y*math.cos(angle),z)
    profile = [(-1.0,0.32),(-0.72,0.36),(0.20,0.38),(0.47,0.60),(0.88,1.08)]
    for side in (-1,1):
        tube('Lounge side rail',[p(side*0.34,y,z) for y,z in profile],0.022,frame)
        tube('Folding front leg',[p(side*0.30,-0.75,0.02),p(side*0.31,-0.55,0.35),p(side*0.31,0.10,0.10)],0.019,frame)
        tube('Folding rear leg',[p(side*0.30,0.73,0.025),p(side*0.31,0.35,0.52),p(side*0.31,-0.25,0.10)],0.019,frame)
        tube('Backrest adjustment stay',[p(side*0.32,0.70,0.16),p(side*0.32,0.66,0.82)],0.014,frame)
        for yy in (-0.75,0.73):
            o = box('Non-slip chair foot',p(side*0.30,yy,0.025),(0.075,0.09,0.045),rubber,0.01)
            o.rotation_euler.z = angle
    for y,z in (profile[0],profile[2],profile[-1]):
        tube('Chair transverse frame',[p(-0.34,y,z),p(0.34,y,z)],0.021,frame)
    for j in range(8):
        xa,xb = -0.31+0.62*j/8,-0.31+0.62*(j+1)/8
        vertices = []
        for y,z in profile:
            vertices.extend([p(xa,y,z+0.006),p(xb,y,z+0.006)])
        faces = [(2*k,2*k+1,2*k+3,2*k+2) for k in range(len(profile)-1)]
        mesh = bpy.data.meshes.new('Striped sling mesh')
        mesh.from_pydata(vertices,[],faces)
        mesh.update()
        o = bpy.data.objects.new('Lounge canvas stripe',mesh)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(cream if j%2==0 else colors[index])
        s = o.modifiers.new('Sling fabric thickness','SOLIDIFY')
        s.thickness = 0.006
    y,z = 0.745,0.94
    pillow = box('Padded head cushion',p(0,y-0.028,z+0.035),(0.48,0.22,0.075),cream,0.032)
    pillow.rotation_euler = (math.atan2(0.48,0.41),0,angle)

for i,x in enumerate((-3.5,0,3.5)):
    umbrella(x,0.45,i)
    lounge(x-0.64,-0.57,-0.10,i)
    lounge(x+0.64,-0.57,0.10,i)
    cylinder('Round side table top',(x,-1.08,0.43),0.22,0.035,frame)
    cylinder('Side table stem',(x,-1.08,0.23),0.025,0.37,frame)
    cylinder('Side table foot',(x,-1.08,0.055),0.15,0.045,frame)
    cylinder('Reusable beach tumbler',(x,-1.08,0.515),0.037,0.13,colors[i])
    cylinder('Tumbler lid',(x,-1.08,0.584),0.040,0.01,cream)
    tube('Drinking straw',[(x,-1.08,0.59),(x,-1.08,0.70),(x+0.035,-1.08,0.72)],0.0035,cream)

world = bpy.data.worlds.new('Seaside daylight')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.60,0.77,0.94,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN',location=(0,0,10))
bpy.context.object.rotation_euler = (0.35,-0.45,-0.35)
bpy.context.object.data.energy = 2.5
bpy.context.object.data.angle = 0.12
bpy.ops.object.light_add(type='AREA',location=(-2,-5,7))
bpy.context.object.data.energy = 1200
bpy.context.object.data.size = 7
bpy.ops.object.camera_add(location=(8,-14,8))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 12.5
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1700
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
