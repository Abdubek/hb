import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(n,c,metal=0,rough=.5,emit=0):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    return m

def box(n,p,s,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Rounded edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(n,a,b,r,m,v=20):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=n
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge rounding','BEVEL'); q.width=min(.012,r*.2); q.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def area(n,p,target,power,size,c):
    bpy.ops.object.light_add(type='AREA',location=p); o=bpy.context.object; o.name=n; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=c
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def label(body,loc,size,material,rotation=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rotation); o=bpy.context.object; o.name='Sign '+body; o.data.body=body; o.data.size=size; o.data.extrude=.001; o.data.materials.append(material)

ivory=mat('Warm ivory panels',(.76,.75,.65)); teal=mat('Woven blue upholstery',(.045,.20,.24),rough=.88)
piping=mat('Seat piping',(.13,.36,.38)); navy=mat('Dark seat shells',(.035,.07,.085)); metal=mat('Satin aluminum',(.55,.62,.65),.8,.28)
floor=mat('Rubber flooring',(.12,.15,.16)); wood=mat('Walnut trim',(.27,.13,.065)); black=mat('Gaskets',(.018,.023,.026))
glass=mat('Pale window glass',(.39,.63,.72),rough=.24,emit=.35); white=mat('Warm luminous panels',(1,.86,.65),emit=4)
red=mat('Emergency red',(.65,.055,.03)); leather=mat('Ochre luggage',(.49,.25,.075)); paper=mat('Cream signage',(.92,.91,.78))
# Full floor and rear wall, open near side and roof center for a dollhouse view.
box('Carriage underfloor',(0,0,-.14),(10.4,3.9,.26),navy)
box('Cabin rubber floor',(0,0,.015),(10.1,3.64,.07),floor)
for x in [-4,-2,0,2,4]: box('Floor joint',(x,0,.055),(.014,3.6,.008),black,0)
for y in [-.35,.35]: box('Aisle inlay',(0,y,.059),(10,.025,.009),metal,.003)
box('Rear lower wall',(0,1.89,.64),(10.3,.16,1.28),ivory)
box('Rear upper wall',(0,1.89,3.06),(10.3,.16,.46),ivory)
for x in [-5.04,-2.52,0,2.52,5.04]: box('Window pillar',(x,1.89,2.04),(.18,.16,1.80),ivory)
for x in [-3.78,-1.26,1.26,3.78]:
    box('Window gasket',(x,1.875,2.02),(2.36,.085,1.59),black,.12)
    box('Window glass',(x,1.82,2.02),(2.20,.025,1.44),glass,.10)
    box('Window bottom rail',(x,1.72,1.26),(2.40,.16,.065),metal)
    box('Window horizontal divider',(x,1.785,2.49),(2.20,.025,.035),metal,.008)
box('Rear walnut waist rail',(0,1.74,1.16),(10.15,.08,.12),wood)
# End vestibule wall and recessed door.
box('Left end wall',(-5.16,0,1.66),(.18,3.86,3.33),ivory)
box('Vestibule door frame',(-5.04,0,1.43),(.10,1.15,2.79),metal)
box('Vestibule sliding door',(-4.976,0,1.43),(.055,1.02,2.67),wood)
box('Door window gasket',(-4.933,0,1.95),(.035,.68,.95),black,.06)
box('Door window',(-4.906,0,1.95),(.021,.57,.83),glass,.04)
rod('Door handle',(-4.88,-.36,1.12),(-4.88,-.36,1.45),.023,metal)
# Cutaway far end represented by sill and corner post.
box('Right end threshold',(5.12,0,.15),(.18,3.82,.25),ivory)
box('Far corner upright',(5.10,1.84,1.72),(.15,.15,3.2),ivory)
# Facing seat pairs arranged around two bays; aisle runs down the middle.
for x,direction in [(-4.05,1),(-.98,-1),(.98,1),(4.05,-1)]:
    for y in [-1.08,1.08]:
        box('Seat pedestal',(x,y,.37),(.52,.64,.63),metal,.055)
        box('Seat pan shell',(x,y,.70),(.88,1.08,.18),navy,.09)
        box('Upholstered seat cushion',(x+direction*.045,y,.83),(.85,.97,.22),teal,.09)
        bx=x-direction*.40
        shell=box('Curved-edge back shell',(bx,y,1.30),(.19,1.08,1.16),navy,.075); shell.rotation_euler.y=-direction*.10
        back=box('Back cushion',(bx+direction*.12,y,1.31),(.19,.96,1.0),teal,.075); back.rotation_euler.y=-direction*.10
        box('Headrest',(bx+direction*.14,y,1.76),(.23,.77,.25),teal,.085)
        box('Headrest cloth',(bx+direction*.265,y,1.77),(.014,.55,.20),paper,.015)
        for offset in [-.49,.49]:
            rod('Armrest support',(x-.15*direction,y+offset,.77),(x-.15*direction,y+offset,1.08),.027,metal)
            box('Arm pad',(x+.04*direction,y+offset,1.11),(.65,.10,.09),navy,.04)
        for offset in [-.30,0,.30]: box('Seat stitched channel',(x+.05*direction,y+offset,.944),(.60,.012,.008),piping,.003)
        # Small mesh pocket on the exterior of each back.
        for off in [-.32,-.16,0,.16,.32]: rod('Seatback pocket wire',(bx-direction*.12,y+off,.97),(bx-direction*.12,y+off,1.24),.008,metal,8)
        rod('Pocket top rim',(bx-direction*.13,y-.35,1.24),(bx-direction*.13,y+.35,1.24),.012,metal)
# Window-side tables between facing seats.
for x in [-2.52,2.52]:
    rod('Table pedestal',(x,1.16,.07),(x,1.16,1.08),.055,metal)
    box('Bay table',(x,1.13,1.13),(1.20,.88,.09),ivory,.065)
    box('Table edge',(x,1.13,1.075),(1.22,.90,.035),wood,.03)
    rod('Cup',(x-.25,1.15,1.18),(x-.25,1.15,1.34),.062,paper,24)
    rod('Cup coffee',(x-.25,1.15,1.342),(x-.25,1.15,1.345),.051,wood,24)
# Open tubular luggage racks along both sides.
for y in [-1.43,1.43]:
    for yy in [y-.25,y+.25]: rod('Rack outer longitudinal rail',(-4.84,yy,2.69),(4.89,yy,2.69),.031,metal)
    for i in range(42):
        x=-4.78+i*.235; rod('Rack transverse slat',(x,y-.25,2.69),(x,y+.25,2.69),.013,metal,10)
    for x in [-4.75,-2.5,0,2.5,4.75]:
        rod('Rack riser',(x,y+.22,2.70),(x,y+.22,3.16),.024,metal)
        rod('Rack bracket',(x,y+.22,3.10),(x,y-.24,2.69),.023,metal)
# Suitcases with contrasting straps and handles.
for x,y in [(-3.3,1.43),(1.5,1.43),(3.2,-1.43)]:
    box('Stowed suitcase',(x,y,2.93),(.87,.43,.43),leather,.075)
    for xx in [x-.27,x+.27]: box('Luggage leather strap',(xx,y,2.93),(.055,.447,.446),wood,.025)
    rod('Suitcase handle',(x-.13,y,3.17),(x+.13,y,3.17),.024,navy)
# Roof edge coves and suspended luminous longitudinal fittings.
for y in [-1.82,1.82]: box('Ceiling edge cove',(0,y,3.30),(10.3,.26,.22),ivory,.075)
for x in [-3.65,-1.2,1.2,3.65]:
    box('Overhead fixture housing',(x,0,3.39),(1.90,.42,.12),metal,.045)
    box('Overhead opal light',(x,0,3.318),(1.75,.31,.025),white,.025)
    for dx in [-.65,.65]: rod('Fixture hanger',(x+dx,0,3.42),(x+dx,0,3.65),.014,metal)
    area('Ceiling light',(x,0,3.27),(x,0,0),100,1.4,(1,.87,.68))
label('SECOND CLASS',(1.8,1.786,3.04),.15,navy)
label('24 - 31',(-3.95,1.786,3.04),.13,navy)
box('Emergency panel',(-4.58,1.76,1.0),(.23,.08,.28),red)
area('Daylight through glazing',(0,1.3,4.6),(0,0,.5),800,5,(.70,.84,1))
area('Open side fill',(1,-5,6),(0,0,1),1200,7,(1,.89,.75))
scene=bpy.context.scene; scene.world.color=(.18,.18,.18)
bpy.ops.object.camera_add(location=(11,-13,9)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.55))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=13.8; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
