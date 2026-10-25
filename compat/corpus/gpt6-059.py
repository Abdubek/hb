import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge softness','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

def tube(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=5; s=cu.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

oak=mat('Natural oak',(0.47,0.29,0.14)); stone=mat('Warm limestone',(0.77,0.74,0.65),rough=0.55); ceramic=mat('Glazed porcelain',(0.91,0.94,0.90),rough=0.19); brass=mat('Satin brass',(0.62,0.42,0.16),0.8,0.27); dark=mat('Dark gaps',(0.035,0.041,0.035)); wall=mat('Warm plaster',(0.79,0.77,0.68),rough=0.85); tile=mat('Sage tile',(0.40,0.52,0.46),rough=0.26); towel=mat('Cotton towel',(0.89,0.83,0.68),rough=0.95); amber=mat('Amber soap bottle',(0.27,0.11,0.035),rough=0.23)
# Procedural oak grain without image assets.
p=oak.node_tree.nodes.get('Principled BSDF'); ns=oak.node_tree.nodes; links=oak.node_tree.links
tex=ns.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=4; tex.inputs['Detail'].default_value=2
coord=ns.new('ShaderNodeTexCoord'); mapping=ns.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(8,8,0.6); links.new(coord.outputs['Generated'],mapping.inputs[0]); links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp=ns.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.22,0.105,0.035,1); ramp.color_ramp.elements[1].color=(0.57,0.37,0.18,1); links.new(tex.outputs['Fac'],ramp.inputs[0]); links.new(ramp.outputs['Color'],p.inputs['Base Color'])
box('Floor',(0,-0.4,-0.055),(7,7,0.10),stone,0)
box('Back wall',(0,0.61,1.7),(5.4,0.12,3.4),wall,0)
for ix in range(-7,8):
    for iz in range(4): box('Backsplash tile',(ix*0.245,0.533,0.83+iz*0.17),(0.237,0.025,0.162),tile,0.007)
# Floating cabinet with drawer reveal gaps and fluted fronts.
box('Vanity carcass',(0,0.03,0.65),(1.94,0.98,0.63),oak,0.025)
box('Shadow behind drawers',(0,-0.468,0.65),(1.85,0.02,0.56),dark,0.008)
for x in [-0.474,0.474]:
    for z in [0.51,0.80]:
        box('Drawer front',(x,-0.495,z),(0.926,0.055,0.266),oak,0.012)
        for i in range(18): box('Fluted timber',(x-0.438+i*0.0515,-0.53,z),(0.028,0.028,0.245),oak,0.012)
        for dx in [-0.13,0.13]: rod('Handle mounting',(x+dx,-0.54,z+0.065),(x+dx,-0.58,z+0.065),0.01,brass)
        rod('Drawer pull',(x-0.16,-0.588,z+0.065),(x+0.16,-0.588,z+0.065),0.014,brass)
box('Countertop',(0,0.015,1.003),(2.06,1.075,0.09),stone,0.023)
# Watertight elliptical vessel sink: outer underside, outer wall, rounded rim, inner bowl, floor.
profile=[(0.0,1.051),(0.48,1.051),(0.66,1.08),(0.88,1.20),(1.0,1.31),(0.998,1.332),(0.95,1.341),(0.918,1.31),(0.80,1.205),(0.58,1.115),(0.26,1.09),(0.0,1.09)]
N=96; verts=[]
for r,z in profile:
    for i in range(N):
        a=i*math.tau/N; verts.append((0.57*r*math.cos(a),-0.045+0.37*r*math.sin(a),z))
faces=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(profile)-1) for i in range(N)]
me=bpy.data.meshes.new('Vessel sink shell'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Oval ceramic basin',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(ceramic)
for p in me.polygons: p.use_smooth=True
rod('Drain shadow',(0,-0.045,1.091),(0,-0.045,1.094),0.049,dark)
rod('Pop-up drain',(0,-0.045,1.094),(0,-0.045,1.106),0.040,brass)
# Tall faucet rises behind the vessel and curves over the bowl.
rod('Faucet mounting plate',(0,0.397,1.05),(0,0.397,1.064),0.065,brass)
tube('Gooseneck faucet',[(0,0.397,1.065),(0,0.397,1.49),(0,0.355,1.60),(0,0.22,1.64),(0,0.075,1.60),(0,0.04,1.52)],0.026,brass)
rod('Aerator',(0,0.04,1.509),(0,0.04,1.529),0.021,dark)
rod('Mixer valve',(-0.04,0.397,1.24),(0.07,0.397,1.24),0.035,brass)
rod('Mixer lever',(0.068,0.397,1.24),(0.068,0.397,1.37),0.012,brass)
# Round mirror, normal facing toward the room (-Y).
rod('Mirror frame',(0,0.485,2.17),(0,0.532,2.17),0.69,brass)
mirror=mat('Silver mirror',(0.93,0.95,0.96),1.0,0.018)
rod('Mirror glass',(0,0.472,2.17),(0,0.486,2.17),0.652,mirror)
# Wall sconces, warm emissive diffusers and practical lights.
glow=mat('Opal light',(0.96,0.88,0.67),rough=0.3); p=glow.node_tree.nodes['Principled BSDF']; p.inputs['Emission Color'].default_value=(1.0,0.78,0.47,1); p.inputs['Emission Strength'].default_value=2.0
for x in [-0.96,0.96]:
    box('Sconce backplate',(x,0.49,2.16),(0.13,0.10,0.35),brass)
    rod('Sconce diffuser',(x,0.375,1.94),(x,0.375,2.38),0.045,glow)
    for z in [1.925,2.395]: rod('Sconce cap',(x,0.375,z-0.015),(x,0.375,z+0.015),0.051,brass)
    bpy.ops.object.light_add(type='POINT',location=(x,0.27,2.17)); bpy.context.object.data.energy=22; bpy.context.object.data.color=(1,0.78,0.52); bpy.context.object.data.shadow_soft_size=0.15
rod('Soap bottle',(-0.79,0.18,1.053),(-0.79,0.18,1.25),0.066,amber)
rod('Pump neck',(-0.79,0.18,1.25),(-0.79,0.18,1.30),0.022,brass)
box('Pump',(-0.77,0.18,1.31),(0.105,0.038,0.024),brass,0.009)
box('Soap label',(-0.79,0.112,1.15),(0.075,0.009,0.084),towel,0.006)
box('Towel tray',(0.78,0.02,1.064),(0.35,0.44,0.025),brass,0.018)
for k in range(3): box('Folded hand towel',(0.78,0.02,1.092+k*0.045),(0.30,0.37,0.047),towel,0.023)
for y in [-0.12,-0.09]: box('Towel woven border',(0.78,y,1.207),(0.27,0.009,0.006),stone,0.002)
box('Bath mat',(0,-1.10,0.014),(1.65,0.77,0.025),towel,0.07)
for i in range(25): box('Bath mat rib',(-0.76+i*0.063,-1.10,0.030),(0.025,0.66,0.011),towel,0.005)
world=bpy.data.worlds.new('Room ambient'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=0.35
for loc,power,size in [((-3,-4,4.5),650,3),((2,-1,4),350,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.2,-5.4,3.2)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=3.9
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1100; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
