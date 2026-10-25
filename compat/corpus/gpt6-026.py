import bpy, math, random
from mathutils import Vector
random.seed(26)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=.5, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def wood(name, color):
    m=mat(name,color,.75); n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    t=n.new('ShaderNodeTexCoord'); v=n.new('ShaderNodeVectorMath'); v.operation='MULTIPLY'; v.inputs[1].default_value=(2,65,12)
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3; noise.inputs['Detail'].default_value=2
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(*(c*.55 for c in color),1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(*(min(c*1.25,1) for c in color),1)
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.025
    l.new(t.outputs['Generated'],v.inputs[0]); l.new(v.outputs['Vector'],noise.inputs['Vector']); l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],p.inputs['Base Color']); l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],p.inputs['Normal'])
    return m

def box(name, loc, size, material, bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel: b=o.modifiers.new('Worn edges','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def nail(loc):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.012,location=loc); o=bpy.context.object; o.name='Recessed nail head'; o.scale=(1,.35,1); o.data.materials.append(steel)

def text(body,loc,size,material):
    c=bpy.data.curves.new('Shipping stencil','FONT'); c.body=body; c.align_x='CENTER'; c.align_y='CENTER'; c.size=size; c.extrude=.0005
    o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); c.materials.append(material)

pine=[wood('Pine tone %d'%i,(.43+.025*i,.24+.018*i,.105+.011*i)) for i in range(5)]
palletwood=wood('Weathered pallet oak',(.32,.22,.12)); steel=mat('Dark nail steel',(.12,.13,.14),.48,.7); paper=mat('Ivory shipping labels',(.88,.84,.67),.9); ink=mat('Stencil charcoal',(.045,.055,.05),.8)
# Standard open pallet construction: bottom runners, nine blocks, crossboards, top deck.
for y in [-.75,0,.75]:
    box('Bottom runner',(0,y,.07),(3.3,.19,.12),palletwood)
    for x in [-1.4,0,1.4]: box('Pallet spacer block',(x,y,.22),(.25,.22,.2),palletwood)
for x in [-1.4,0,1.4]: box('Bearer',(x,0,.35),(.23,1.94,.08),palletwood)
for i in range(7): box('Top deck board %02d'%i,(0,-.84+i*.28,.435),(3.3,.245,.09),pine[i%5])
# Exactly six separate crates: three columns, two levels.
for row in range(2):
    for col in range(3):
        x=(col-1)*1.065; z0=.49+row*.93; cy=0; w=.99; d=1.54; h=.88; number=row*3+col+1
        for k in range(4):
            z=z0+.12+k*.205
            for y in [-d/2,d/2]: box('Crate %02d horizontal face plank'%number,(x,y,z),(w,.055,.193),random.choice(pine))
            for side in [-1,1]: box('Crate side plank',(x+side*(w/2-.028),cy,z),(.055,d-.08,.193),random.choice(pine))
        for k in range(5):
            yy=-.6+k*.3
            for zz in [z0+.025,z0+h-.025]: box('Crate lid or base plank',(x,yy,zz),(w,.287,.05),random.choice(pine),.006)
        for side in [-1,1]:
            for y in [-d/2-.038,d/2+.038]:
                xx=x+side*.375; box('Vertical reinforcing batten',(xx,y,z0+h/2),(.105,.065,h+.015),random.choice(pine))
                if y<0:
                    for zz in [z0+.09,z0+.31,z0+.57,z0+.79]: nail((xx,y-.035,zz))
        # Small dark recesses suggest hand slots on exposed sides.
        for side in [-1,1]: box('Side lifting recess',(x+side*(w/2+.002),.0,z0+.65),(.008,.30,.055),ink,.02)
        front=-d/2-.033
        box('Crate %02d label'%number,(x,front-.007,z0+.45),(.52,.012,.35),paper,.005)
        text('CARGO %02d'%number,(x,front-.015,z0+.525),.075,ink)
        text('DRY GOODS',(x,front-.015,z0+.44),.043,ink)
        text('LOT 26 / 2026',(x,front-.015,z0+.38),.036,ink)
        for k in range(23):
            xx=x-.19+k*.017
            box('Printed barcode',(xx,front-.016,z0+.32),(.004 if k%3 else .009,.001,.044),ink,0)
        text('UP',(x+.28,front-.01,z0+.73),.05,ink)
        box('Up arrow stem',(x+.28,front-.01,z0+.67),(.012,.003,.065),ink,0)

floor=mat('Warm concrete',(.26,.28,.28),.9); box('Floor',(0,0,-.045),(200,200,.08),floor,.0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.40,.48,1); world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in [('Key',(1,-4,7),1400,5),('Fill',(-4,-1,4),800,4),('Rim',(2,4,5),1100,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,4.5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.3
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
