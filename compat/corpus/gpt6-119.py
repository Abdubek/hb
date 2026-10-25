import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
case=mat('Charcoal enclosure',(.035,.045,.055),.1,.64); metal=mat('Perforated powder coated steel',(.23,.28,.32),.8,.34); rubber=mat('Rubber gasket',(.012,.015,.018),0,.8); cone=mat('Speaker cones',(.055,.06,.065),.1,.72); screwmat=mat('Screw heads',(.48,.51,.53),.9,.28); floor=mat('Studio floor',(.18,.21,.24))
def box(name,loc,size,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=6; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def mesh(name,v,f,m):
    me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o
# The enclosure lies face-up, exposing the depth of the perforations.
box('Rounded rectangular enclosure',(0,0,1.15),(5.8,7.8,2.3),case,.48)
box('Inset front baffle',(0,0,2.31),(5.36,7.36,.12),rubber,.28)
def cylinder(name,loc,r,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o
for y,r in [(-1.45,1.7),(1.7,1.04)]:
    cylinder('Driver mounting flange',(0,y,2.4),r,.07,case)
    bpy.ops.mesh.primitive_torus_add(major_radius=r*.84,minor_radius=.09,major_segments=64,minor_segments=10,location=(0,y,2.45)); bpy.context.object.data.materials.append(rubber)
    v=[]; f=[]
    for rad,zz in [(r*.78,2.44),(r*.28,2.31)]:
        for k in range(64):
            a=2*math.pi*k/64; v.append((rad*math.cos(a),y+rad*math.sin(a),zz))
    for k in range(64): f.append((k,(k+1)%64,(k+1)%64+64,k+64))
    mesh('Recessed driver cone',v,f,cone)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=r*.29,location=(0,y,2.32)); o=bpy.context.object; o.name='Driver dust cap'; o.scale.z=.32; o.data.materials.append(cone)
# Each grid cell is an annulus between a square boundary and a real circular hole.
# Welding cell boundaries produces one continuous perforated sheet.
v=[]; f=[]; n=16; pitch=.3; radius=.103; nx=16; ny=22; front=2.67
for j in range(ny):
    for i in range(nx):
        cx=(i-(nx-1)/2)*pitch; cy=(j-(ny-1)/2)*pitch; start=len(v)
        for ring in [0,1]:
            for k in range(n):
                a=2*math.pi*k/n; c,s=math.cos(a),math.sin(a); rr=(pitch/2)/max(abs(c),abs(s)) if ring==0 else radius
                v.append((cx+rr*c,cy+rr*s,front))
        for k in range(n):
            q=(k+1)%n; f.append((start+k,start+q,start+n+q,start+n+k))
grille=mesh('True circular perforated metal grille',v,f,metal)
import bmesh
bm=bmesh.new(); bm.from_mesh(grille.data); bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(grille.data); bm.free()
s=grille.modifiers.new('Sheet thickness and hole walls','SOLIDIFY'); s.thickness=.055; s.offset=-1
b=grille.modifiers.new('Soft punched hole edges','BEVEL'); b.width=.006; b.segments=2
# Rounded rectangular continuous trim bridges the sheet to the enclosure.
def rounded_loop(w,h,r,z):
    pts=[]
    for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for k in range(13):
            a=math.radians(start+90*k/12); pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return pts
outer=rounded_loop(5.52,7.52,.38,front+.018); inner=rounded_loop(4.76,6.56,.18,front+.018); n=len(outer)
trim=mesh('Rounded grille perimeter frame',outer+inner,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],metal); s=trim.modifiers.new('Frame thickness','SOLIDIFY'); s.thickness=.085; b=trim.modifiers.new('Trim edge radius','BEVEL'); b.width=.025; b.segments=3
for x in [-2.57,2.57]:
    for y in [-3.36,0,3.36]:
        cylinder('Recessed fastening screw',(x,y,front+.04),.078,.045,screwmat)
        box('Screw slot',(x,y,front+.064),(.098,.017,.005),rubber)
box('Maker badge',(0,-3.52,front+.06),(.78,.2,.05),case,.035)
for x in [-1.9,1.9]:
    for y in [-2.8,2.8]: box('Rubber foot',(x,y,-.06),(.55,.65,.18),rubber,.08)
box('Studio surface',(0,0,-.23),(200,200,.15),floor)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.3
for loc,power,size in [((1,-5,12),1500,7),((-7,2,7),1100,6),((5,7,8),1700,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(9,-12,15)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=12.5; bpy.context.scene.camera=cam
bpy.context.scene.render.engine='CYCLES'; bpy.context.scene.render.resolution_x=1300; bpy.context.scene.render.resolution_y=1500; bpy.context.scene.render.resolution_percentage=100
