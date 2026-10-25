import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.4; return m
def box(n,p,s,m,b=.05):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if b: mod=o.modifiers.new('Edge bevel','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
case=mat('Midnight aluminum',(.035,.055,.09),.65); plate=mat('Switch plate',(.095,.12,.15),.7); switches=mat('Switch housings',(.025,.03,.04)); legends=mat('Cream legends',(.96,.95,.87)); coral=mat('Coral',(.82,.19,.16)); gold=mat('Ochre',(.82,.48,.10)); green=mat('Sage',(.24,.46,.33)); teal=mat('Teal',(.06,.37,.45)); blue=mat('Blue',(.16,.29,.52)); purple=mat('Plum',(.38,.23,.43)); floor=mat('Desk',(.23,.25,.28)); silver=mat('Hardware',(.5,.55,.6),.8)
unit=.48; total=15*unit
box('Keyboard lower case',(0,0,.23),(7.65,3.15,.46),case,.16); box('Upper case rim',(0,0,.45),(7.61,3.11,.16),case,.10); box('Recessed metal plate',(0,0,.541),(7.36,2.88,.045),plate,.07)
# A complete 60 percent layout, with standard stagger and variable-width modifiers.
rows=[
 [('Esc',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1),('Back',2)],
 [('Tab',1.5),('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1),('\\',1.5)],
 [('Caps',1.75),('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),("'",1),('Enter',2.25)],
 [('Shift',2.25),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),('.',1),('/',1),('Shift',2.75)],
 [('Ctrl',1.25),('Win',1.25),('Alt',1.25),('',6.25),('Alt',1.25),('Fn',1.25),('Menu',1.25),('Ctrl',1.25)]
]
colors=[coral,gold,green,teal,blue]
def keycap(label,x,y,w,ma,row):
 width=w*unit-.042; depth=.445; base=.60; top=.87+row*.008
 # Tapered skirt and a shallow dished top surface with a regular grid.
 verts=[(x-width/2,y-depth/2,base),(x+width/2,y-depth/2,base),(x+width/2,y+depth/2,base),(x-width/2,y+depth/2,base)]
 nx=12 if w>2 else 6; ny=6; tw=width-.055; td=depth-.055
 for j in range(ny+1):
  v=j/ny*2-1
  for i in range(nx+1):
   u=i/nx*2-1; dish=.018*(1-u*u)*(1-v*v); verts.append((x+u*tw/2,y+v*td/2,top-dish))
 def idx(i,j): return 4+j*(nx+1)+i
 faces=[(3,2,1,0)]
 for j in range(ny):
  for i in range(nx): faces.append((idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)))
 faces.extend([tuple([0,1]+[idx(i,0) for i in range(nx,-1,-1)]),tuple([1,2]+[idx(nx,j) for j in range(ny,-1,-1)]),tuple([2,3]+[idx(i,ny) for i in range(nx+1)]),tuple([3,0]+[idx(0,j) for j in range(ny+1)])])
 me=bpy.data.meshes.new('Sculpted keycap mesh'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Key '+(label or 'Space'),me); bpy.context.collection.objects.link(ob); ob.data.materials.append(ma); mod=ob.modifiers.new('Key edge rounding','BEVEL'); mod.width=.018; mod.segments=3; ob.modifiers.new('Key normals','WEIGHTED_NORMAL')
 box('Mechanical switch',(x,y,.585),(.29,.29,.10),switches,.025)
 if label:
  bpy.ops.object.text_add(location=(x,y-.015,top+.006)); txt=bpy.context.object; txt.name='Legend '+label; txt.data.body=label; txt.data.align_x='CENTER'; txt.data.align_y='CENTER'; txt.data.size=.145 if len(label)==1 else .092; txt.data.extrude=.0006; txt.data.materials.append(legends)
 if label in ['F','J']: box('Homing bar',(x,y-.135,top+.012),(.10,.018,.015),legends,.006)
for row,items in enumerate(rows):
 x=-total/2; y=1.01-row*.505
 for label,w in items:
  keycap(label,x+w*unit/2,y,w,purple if label in ['Esc','Enter'] else colors[row],row); x+=w*unit
for x in [-3.59,3.59]:
 for y in [-1.37,1.37]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.039,depth=.014,location=(x,y,.547)); bpy.context.object.name='Case screw'; bpy.context.object.data.materials.append(silver); box('Screw slot',(x,y,.556),(.045,.010,.005),switches,.002)
box('USB C recess',(2.6,1.577,.27),(.37,.014,.13),switches,.045); box('USB C tongue',(2.6,1.588,.27),(.22,.01,.034),silver,.01)
for x in [-2.9,2.9]:
 for y in [-1.0,1.0]: box('Rubber foot',(x,y,-.013),(.62,.30,.07),switches,.08)
box('Desk',(0,0,-.105),(200,200,.1),floor,0)
bpy.context.scene.world.color=(.22,.22,.22)
for loc,e,size in [((0,-3,8),1100,6),((3,4,5),900,5)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=e; o.data.size=size; o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-9,12)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.3))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10; bpy.context.scene.camera=cam
s=bpy.context.scene; s.render.engine='CYCLES'; s.render.resolution_x=1500; s.render.resolution_y=1000; s.render.resolution_percentage=100
