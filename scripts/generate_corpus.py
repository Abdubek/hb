"""Reproducible GPT-authored seed corpus: 25 task families × 8 variants.

These are synthetic task-driven scripts, not independent production samples.
Do not interpret their pass rate as general bpy coverage or a Claude evaluation.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/'compat/seed-corpus'
CORPUS.mkdir(parents=True,exist_ok=True)
COMMON='''import bpy
import math

def box(name, location, dimensions, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions

'''
TASKS={
'desk':'''box('Desktop', (0, 0, .75), (width, .7, .06))
for x in (-width/2+.08, width/2-.08):
    for y in (-.27, .27): box('Leg', (x,y,.36), (.06,.06,.72))''',
'bookcase':'''for x in (-width/2, width/2): box('Side', (x,0,1), (.04,.3,2))
for z in (0,.4,.8,1.2,1.6,2): box('Shelf', (0,0,z), (width,.3,.04))
box('Back', (0,.16,1), (width,.02,2))''',
'staircase':'''for i in range(count): box('Step', (0,i*.28,i*.09), (width,.28,(i+1)*.18))''',
'bench':'''box('Seat', (0,0,.45), (width,.4,.05))
box('Backrest', (0,.18,.7), (width,.04,.5), (math.radians(-10),0,0))
for x in (-width*.4,width*.4): box('Support', (x,0,.21), (.08,.36,.42))''',
'bridge':'''box('Deck',(0,0,1),(width*3,1,.15))
for side in (-.5,.5):
    box('Railing',(0,side,1.5),(width*3,.05,.05))
    for i in range(count): box('Post',((i/(count-1)-.5)*width*3,side,1.25),(.05,.05,.5))''',
'room_shell':'''box('Floor',(0,0,-.05),(width*3,4,.1))
box('BackWall',(0,2,1.4),(width*3,.1,2.8))
for side in (-1,1): box('SideWall',(side*width*1.5,0,1.4),(.1,4,2.8))''',
'city_blocks':'''for x in range(count):
    for y in range(3):
        height=.5+((x*7+y*3)%5)*.4
        box('Building',(x*width,y*width,height/2),(.7,.7,height))''',
'pallet':'''for i in range(count): box('TopSlat',((i/(count-1)-.5)*width,0,.15),(.08,.8,.03))
for y in (-.3,0,.3): box('Runner',(0,y,.07),(width,.06,.12))''',
'shipping_crate':'''box('CrateBody',(0,0,.5),(width,.8,1))
for x in (-width*.4,width*.4): box('Brace',(x,-.42,.5),(.08,.04,1.1))''',
'server_rack':'''for x in (-width/2,width/2): box('Upright',(x,0,1),(.04,.6,2))
for i in range(count): box('Server',(0,0,.15+i*.18),(width-.06,.55,.14))''',
'keyboard':'''box('Base',(0,0,.02),(width,.35,.04))
for x in range(count):
    for y in range(4): box('Key',((x/(count-1)-.5)*(width-.1),(y-1.5)*.075,.06),(.055,.055,.035))''',
'dominoes':'''for i in range(count): box('Domino',(i*.15,0,.15),(.05,width*.1,.3),(0,math.radians(i*2),0))''',
'picture_frame':'''for z in (-.4,.4): box('Horizontal',(0,0,z),(width,.05,.04))
for x in (-width/2,width/2): box('Vertical',(x,0,0),(.04,.05,.8))''',
'cabinet':'''box('Body',(0,0,.5),(width,.5,1))
for x in (-width*.25,width*.25):
    box('Door',(x,-.27,.5),(width*.48,.03,.94))
    box('Handle',(x*.25,-.31,.5),(.025,.035,.2))''',
'pergola':'''for x in (-width,width):
    for y in (-1,1): box('Post',(x,y,1.2),(.1,.1,2.4))
for i in range(count): box('RoofBeam',((i/(count-1)-.5)*width*2,0,2.45),(.08,2.3,.12))''',
'robot_blockout':'''box('Torso',(0,0,1.1),(.5,.3,.6))
box('Head',(0,0,1.6),(.3,.3,.3))
for side in (-1,1):
    box('Arm',(side*.38,0,1.1),(.15,.2,.6))
    box('Leg',(side*.15,0,.5),(.18,.2,.6))''',
'monitor':'''box('Screen',(0,0,.6),(width,.05,width*.5625))
box('Stand',(0,.02,.2),(.06,.06,.4))
box('Foot',(0,0,.025),(.4,.25,.05))''',
'acoustic_panels':'''for x in range(count):
    for z in range(3): box('Panel',((x-count/2)*.32,0,z*.32),(.3,.08,.3),(0,0,math.radians(variant)))''',
'window_grid':'''for x in range(count+1): box('Mullion',((x/count-.5)*width,0,1),(.025,.06,2))
for z in (0,1,2): box('Transom',(0,0,z),(width,.06,.025))''',
'game_console':'''box('Shell',(0,0,.1),(.09,.15,.02))
box('Screen',(0,.025,.112),(.065,.055,.004))
for x,y in ((-.023,-.032),(-.012,-.032),(-.023,-.043)):
    box('Dpad',(x,y,.115),(.01,.01,.005))''',
'rover':'''box('Chassis',(0,0,.3),(width,.5,.15))
for x in (-width*.35,0,width*.35):
    for y in (-.32,.32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.14, depth=.09, location=(x,y,.14), rotation=(math.pi/2,0,0))
        bpy.context.object.name='Wheel' ''',
'product_material':'''box('Product',(0,0,.5),(width,.5,1))
material=bpy.data.materials.new('Enamel')
material.diffuse_color=(.1,.3,.8,1)
bpy.context.object.data.materials.append(material)''',
'product_camera':'''box('Product',(0,0,.5),(width,.5,1))
data=bpy.data.cameras.new('ProductCamera')
camera=bpy.data.objects.new('ProductCamera',data)
bpy.context.collection.objects.link(camera)
camera.location=(3,-4,2)
bpy.context.scene.camera=camera''',
'beveled_case':'''box('Case',(0,0,.1),(width,.7,.2))
modifier=bpy.context.object.modifiers.new('Edge highlights','BEVEL')
modifier.width=.02
modifier.segments=3''',
'sphere_lamp':'''HB_EQUIVALENT_MESH_PREFIXES=('Sphere',)
box('Base',(0,0,.03),(.3,.3,.06))
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.2, location=(0,0,.4))
bpy.context.object.name='Globe'
bpy.ops.object.shade_smooth()''',
}
entries=[]
for task,body in TASKS.items():
    for variant in range(8):
        name=f'{task}_{variant:02}.py'
        source=f'# Task: {task.replace("_", " ")}; design variant {variant+1}.\n'+COMMON+f'variant={variant}\nwidth={1+variant*.1:.2f}\ncount={4+variant}\n'+body+'\n'
        (CORPUS/name).write_text(source)
        entries.append(dict(file=name,family=task,variant=variant,provenance='GPT-authored parameterized seed; generated in this implementation session',expected_m0=task in list(TASKS)[:20]))
(CORPUS/'index.json').write_text(json.dumps({'kind':'synthetic_seed','independent_task_families':len(TASKS),'scripts':entries},indent=2)+'\n')
