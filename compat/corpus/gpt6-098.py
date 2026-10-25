import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.3):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dim,m,b=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Rounded edges','BEVEL'); mod.width=b; mod.segments=4
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,r,d,m,direction=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    mod=o.modifiers.new('Polished edges','BEVEL'); mod.width=min(0.007,d*0.16); mod.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for f in o.data.polygons: f.use_smooth=True
    return o

def torus(name,loc,r,t,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=16,major_radius=r,minor_radius=t,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

def lathe(name,profile,sx,sy,center,m):
    n=96; verts=[]; faces=[]
    for r,z in profile:
        for j in range(n):
            a=math.tau*j/n
            verts.append((center[0]+sx*r*math.cos(a),center[1]+sy*r*math.sin(a),z))
    for i in range(len(profile)-1):
        for j in range(n):
            k=i*n+j; q=i*n+(j+1)%n
            faces.append((k,q,q+n,k+n))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    for f in mesh.polygons: f.use_smooth=True
    return o

def tube(name,points,r,m):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.resolution_u=24
    curve.bevel_depth=r; curve.bevel_resolution=5; curve.use_fill_caps=True
    sp=curve.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for bp,co in zip(sp.bezier_points,points):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    return o

ceramic=mat('Glazed porcelain',(0.91,0.94,0.92),0,0.16)
chrome=mat('Chrome',(0.64,0.72,0.76),0.95,0.14)
dark=mat('Drain recess',(0.015,0.025,0.028),0.15,0.55)
wallmat=mat('Sage wall',(0.32,0.43,0.40),0,0.8)
floormat=mat('Limestone floor',(0.46,0.44,0.39),0,0.65)
grout=mat('Grout',(0.25,0.27,0.25),0,0.85)
blue=mat('Cold marker',(0.04,0.22,0.6),0,0.3)
red=mat('Hot marker',(0.68,0.055,0.035),0,0.3)
soap=mat('Soft amber soap',(0.73,0.49,0.20),0,0.45)

# Continuous thick porcelain section: underside, outer wall, rounded lip,
# then concave inner bowl descending to an actual drain opening.
profile=[(0.105,0.67),(0.28,0.675),(0.48,0.70),(0.68,0.745),(0.85,0.805),(0.96,0.862),(1.0,0.898),(0.998,0.913),(0.982,0.924),(0.95,0.925),(0.918,0.914),(0.89,0.892),(0.82,0.846),(0.69,0.793),(0.53,0.751),(0.36,0.728),(0.19,0.718),(0.105,0.716)]
lathe('Sculpted oval basin',profile,0.51,0.365,(0,-0.04),ceramic)
# Pedestal flares gently into the underside of the bowl.
ped=[(0,0.025),(0.16,0.025),(0.181,0.037),(0.183,0.058),(0.172,0.085),(0.139,0.13),(0.119,0.25),(0.105,0.45),(0.111,0.58),(0.142,0.665),(0.19,0.701),(0,0.708)]
lathe('Flared ceramic pedestal',ped,1,0.85,(0,0.07),ceramic)
box('Rear faucet deck',(0,0.283,0.883),(0.76,0.21,0.072),ceramic,0.035)
box('Porcelain backsplash',(0,0.375,0.95),(0.79,0.05,0.15),ceramic,0.023)
# Waste fitting with a dark inset and visible perforations.
cylinder('Dark waste opening',(0,-0.04,0.714),0.047,0.012,dark)
torus('Chrome drain flange',(0,-0.04,0.721),0.044,0.007,chrome)
cylinder('Drain strainer',(0,-0.04,0.718),0.037,0.008,chrome)
for j in range(8):
    a=j*math.tau/8
    cylinder('Strainer perforation',(0.025*math.cos(a),-0.04+0.025*math.sin(a),0.7224),0.0042,0.001,dark)
cylinder('Central drain screw',(0,-0.04,0.724),0.006,0.003,chrome)
box('Screw slot',(0,-0.04,0.726),(0.008,0.0015,0.001),dark,0.0005)
# Overflow on the inner rear slope, aimed upward and into the bowl.
normal=Vector((0,-0.68,0.73)).normalized()
cylinder('Overflow dark aperture',(0,0.263,0.864),0.021,0.006,dark,normal)
o=torus('Overflow chrome bezel',(0,0.261,0.867),0.021,0.0035,chrome)
o.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
# Arched mixer spout reaches forward over the drain.
cylinder('Faucet foot',(0,0.281,0.929),0.049,0.023,chrome)
cylinder('Faucet body',(0,0.281,1.005),0.031,0.14,chrome)
tube('Curved swan neck',[(0,0.281,1.035),(0,0.281,1.16),(0,0.24,1.228),(0,0.145,1.249),(0,0.045,1.218),(0,-0.005,1.16)],0.024,chrome)
cylinder('Spout aerator collar',(0,-0.005,1.154),0.027,0.026,chrome)
cylinder('Aerator mesh',(0,-0.005,1.140),0.021,0.002,dark)
for x,m in ((-0.18,red),(0.18,blue)):
    cylinder('Tap base',(x,0.281,0.933),0.045,0.019,chrome)
    cylinder('Tap stem',(x,0.281,0.965),0.024,0.055,chrome)
    cylinder('Cross handle horizontal',(x,0.281,1.0),0.010,0.11,chrome,(1,0,0))
    cylinder('Cross handle longitudinal',(x,0.281,1.0),0.010,0.09,chrome,(0,1,0))
    cylinder('Temperature marker',(x,0.281,1.012),0.014,0.006,m)
box('Soap dish',(0.31,0.282,0.931),(0.15,0.10,0.017),chrome,0.018)
box('Bar of soap',(0.31,0.282,0.951),(0.116,0.071,0.031),soap,0.015)
box('Bathroom wall',(0,0.46,1.5),(200,0.08,3),wallmat,0)
box('Stone floor',(0,0,-0.025),(200,200,0.04),floormat,0)
for x in range(-4,5): box('Floor joint',(x*0.5,0,-0.003),(0.004,12,0.001),grout,0)
for y in range(-10,2): box('Floor joint',(0,y*0.5,-0.002),(12,0.004,0.001),grout,0)
box('Wall skirting',(0,0.406,0.065),(12,0.035,0.13),ceramic,0.005)

world=bpy.context.scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[1].default_value=0.35
for loc,power,size in [((2,-3,4),450,3),((-3,-1,2.5),300,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object; o.data.energy=power; o.data.size=size
    o.rotation_euler=(Vector((0,0,0.65))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.8,-2.8,2.0))
cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,0.66))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=1.75
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1100; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
