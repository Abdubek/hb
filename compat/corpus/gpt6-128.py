import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
def box(n,l,s,m,b=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=l); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Molded radii','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def rod(n,a,b,r,m,v=32):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    mod=o.modifiers.new('Edge rounding','BEVEL'); mod.width=0.008; mod.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o
def cable(n,pts,r,m):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4; c.resolution_u=24; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)
def txt(t,l,size,m,rot=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=l,rotation=rot); o=bpy.context.object; o.name='Legend '+t; o.data.body=t; o.data.size=size; o.data.extrude=0.0004; o.data.materials.append(m); return o
cream=mat('Aged ivory ABS',(0.65,0.61,0.48)); edge=mat('Warm shell edge',(0.47,0.44,0.35)); dark=mat('Charcoal plastic',(0.055,0.061,0.05)); keymat=mat('Keycaps',(0.75,0.72,0.59)); orange=mat('Orange function keys',(0.77,0.23,0.05)); metal=mat('Connector metal',(0.46,0.48,0.44),0.8); rubber=mat('Cable rubber',(0.025,0.03,0.022),0,0.8); screen=mat('Phosphor glass',(0.012,0.045,0.026),0.2,0.18); green=mat('Green phosphor',(0.18,0.9,0.35)); p=green.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(0.15,1,0.34,1); p.inputs['Emission Strength'].default_value=2.3
# CRT enclosure tapered toward its rear, with a broad molded front bezel.
verts=[(-1.52,-0.76,0.72),(1.52,-0.76,0.72),(1.52,-0.76,3.04),(-1.52,-0.76,3.04),(-1.21,1.35,0.91),(1.21,1.35,0.91),(1.21,1.35,2.77),(-1.21,1.35,2.77)]
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
me=bpy.data.meshes.new('Tapered CRT shell'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Deep CRT enclosure',me); bpy.context.collection.objects.link(o); o.data.materials.append(cream); b=o.modifiers.new('Large molded corners','BEVEL'); b.width=0.13; b.segments=5; o.modifiers.new('Shell normals','WEIGHTED_NORMAL')
box('Monitor tilt pedestal',(0,0.17,0.52),(1.23,1.1,0.43),edge,0.11)
box('Monitor foot',(0,0.12,0.28),(1.8,1.48,0.16),dark,0.08)
box('Bezel left',(-1.35,-0.835,1.94),(0.35,0.23,2.12),cream,0.09)
box('Bezel right controls',(1.26,-0.835,1.94),(0.52,0.23,2.12),cream,0.09)
box('Bezel top',(-0.11,-0.835,2.91),(2.52,0.23,0.28),cream,0.07)
box('Bezel lower',(-0.11,-0.835,0.97),(2.52,0.23,0.46),cream,0.07)
box('Black CRT gasket',(-0.14,-0.892,2.005),(2.27,0.11,1.65),dark,0.17)
# Subtly convex screen built as a rounded superellipse grid.
v=[]; f=[]; nx=40; nz=30
for j in range(nz+1):
    t=-1+2*j/nz
    for i in range(nx+1):
        s=-1+2*i/nx; x=1.055*s*(1-0.07*abs(t)**8); z=0.735*t*(1-0.09*abs(s)**8)
        y=-0.963-0.085*(1-s*s)*(1-t*t); v.append((x-0.14,y,z+2.01))
for j in range(nz):
    for i in range(nx):
        a=j*(nx+1)+i; f.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Convex CRT glass'); me.from_pydata(v,[],f); me.materials.append(screen); ob=bpy.data.objects.new('Curved green CRT screen',me); bpy.context.collection.objects.link(ob)
for p in me.polygons: p.use_smooth=True
# A sparse boot screen sits just ahead of the curved glass.
lines=['FIELD SYSTEMS / VT-82','MEMORY CHECK ........ OK','LINK 03: CONNECTED','', 'RESEARCH ARCHIVE', '  01  SENSOR LOGS', '  02  TELEMETRY', '', 'READY.', '> _']
for i,line in enumerate(lines):
    if line: txt(line,(-1.01,-1.057,2.59-i*0.126),0.084,green)
for i in range(48):
    z=1.36+i*0.027
    box('Faint horizontal scanline',(-0.14,-1.051,z),(1.93,0.001,0.0018),screen,0)
txt('DATA GENERAL',(-1.1,-0.969,0.967),0.13,dark)
txt('VT-82', (0.57,-0.969,0.967),0.13,dark)
for z,label in [(2.38,'BRIGHT'),(1.88,'CONTRAST')]:
    rod('Knob backing',(1.26,-0.943,z),(1.26,-0.972,z),0.155,edge)
    rod('Knurled adjustment knob',(1.26,-0.97,z),(1.26,-1.08,z),0.12,dark)
    box('Knob indicator',(1.26,-1.088,z+0.062),(0.015,0.01,0.055),keymat,0.003)
    txt(label,(1.055,-0.963,z-0.23),0.058,dark)
    for k in range(16):
        a=k*math.tau/16; rod('Knob grip flute',(1.26+0.117*math.cos(a),-1.01,z+0.117*math.sin(a)),(1.26+0.117*math.cos(a),-1.067,z+0.117*math.sin(a)),0.009,edge,8)
rod('Power indicator',(1.26,-0.95,1.37),(1.26,-0.978,1.37),0.034,green,20)
box('Power switch',(1.26,-0.973,1.16),(0.19,0.055,0.11),dark,0.016)
# Side vents follow the taper of the shell.
for i in range(12):
    y=-0.25+i*0.113; x=1.52-(y+0.76)*0.31/2.11
    box('Right shell vent',(x+0.006,y,2.29),(0.019,0.053,0.43),dark,0.018)
# Separate low wedge keyboard.
verts=[(-1.65,-2.8,0.14),(1.65,-2.8,0.14),(1.65,-1.37,0.14),(-1.65,-1.37,0.14),(-1.65,-2.8,0.32),(1.65,-2.8,0.32),(1.65,-1.37,0.53),(-1.65,-1.37,0.53)]
me=bpy.data.meshes.new('Keyboard wedge'); me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]); me.update(); o=bpy.data.objects.new('Separate keyboard case',me); bpy.context.collection.objects.link(o); o.data.materials.append(cream); b=o.modifiers.new('Keyboard bevel','BEVEL'); b.width=0.065; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
slope=0.21/1.43; angle=math.atan(slope)
def key(legend,x,y,w=0.185,m=keymat):
    z=0.32+(y+2.8)*slope+0.055
    o=box('Key '+legend,(x,y,z),(w,0.185,0.1),m,0.021); o.rotation_euler.x=angle
    t=txt(legend,(x-w*0.32,y-0.031,z+0.057),0.058,dark,(angle,0,0)); return o
rows=['1234567890-=', 'QWERTYUIOP[]', 'ASDFGHJKL;:/', 'ZXCVBNM,./']
for r,row in enumerate(rows):
    y=-1.71-r*0.226
    for c,ch in enumerate(row): key(ch,-1.42+c*0.224+(0.035 if r%2 else 0),y)
for i in range(6): key('F'+str(i+1),-1.42+i*0.35,-1.46,0.29,orange if i==0 else dark)
key('SPACE',-0.28,-2.615,1.38)
key('CTRL',-1.3,-2.615,0.37); key('ENTER',1.26,-2.16,0.38,orange)
for x,y,t in [(1.25,-1.7,'7'),(1.25,-1.93,'4'),(1.25,-2.39,'1'),(0.7,-2.615,'<'),(0.98,-2.615,'v'),(1.26,-2.615,'>')]: key(t,x,y,0.21)
# Plugged-in side connectors with visible collars and strain reliefs.
for y,z in [(0.62,1.35),(0.99,1.35)]:
    x=1.52-(y+0.76)*0.31/2.11
    box('Port mounting plate',(x+0.015,y,z),(0.045,0.28,0.3),metal,0.016)
    rod('Socket collar',(x,y,z),(x+0.12,y,z),0.09,dark)
    rod('Cable plug',(x+0.1,y,z),(x+0.29,y,z),0.075,metal)
    rod('Strain relief',(x+0.27,y,z),(x+0.49,y,z),0.053,rubber)
    for k in range(5): rod('Strain relief rib',(x+0.28+k*0.037,y,z),(x+0.295+k*0.037,y,z),0.06,dark)
cable('Keyboard cable',[(1.84,0.62,1.35),(2.03,0.6,1.1),(2.1,0.2,0.16),(1.97,-0.82,0.11),(0.65,-1.17,0.17),(0.65,-1.37,0.37)],0.035,rubber)
cable('Trailing communications cable',[(1.77,0.99,1.35),(2.04,1.03,1.23),(2.3,1.5,0.2),(2,2.3,0.07),(0.7,2.6,0.07),(-0.2,2.25,0.07)],0.037,rubber)
box('Desk surface',(0,0,-0.07),(200,200,0.12),mat('Desk laminate',(0.16,0.2,0.18)),0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.35
for loc,power,size in [((-3,-4,7),950,5),((4,-1,5),700,4),((1,5,6),1000,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5.6,-8,4.9)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-0.25,1.4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.7; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
