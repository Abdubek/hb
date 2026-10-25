import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
gold=mat('Gold thermal foil',(.65,.37,.075),.75,.32); metal=mat('Brushed titanium',(.4,.48,.56),.85,.3); panel=mat('Blue solar cells',(.015,.055,.18),.65,.23); lines=mat('Cell grid',(.23,.46,.66),.7); black=mat('Sensor glass',(.008,.018,.026),.35,.16)
def cube(name,loc,size,m,q=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    if q: o.rotation_mode='QUATERNION'; o.rotation_quaternion=q
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); return o
def rod(name,a,b,r,m,verts=10):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
# An icosphere supplies a uniform triangulated spherical structural network.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=7)
tmp=bpy.context.object; points=[v.co.copy() for v in tmp.data.vertices]; edges=[tuple(e.vertices) for e in tmp.data.edges]; bpy.data.objects.remove(tmp,do_unlink=True)
for i,j in edges: rod('Thin inter-satellite strut',points[i],points[j],.026,metal,8)
for idx,p in enumerate(points):
    q=p.normalized().to_track_quat('Z','Y')
    def at(x,y,z): return p+q@Vector((x,y,z))
    body=cube('Satellite %02d gold bus'%idx,p,(.46,.42,.53),gold,q); mod=body.modifiers.new('Soft machined edges','BEVEL'); mod.width=.035; mod.segments=2; body.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    cube('Top equipment deck',at(0,0,.285),(.49,.45,.05),metal,q)
    cube('Optical sensor',at(0,-.08,.325),(.17,.15,.04),black,q)
    rod('Solar array spar',at(-1,0,0),at(1,0,0),.025,metal,8)
    for side in [-1,1]:
        cube('Solar wing frame',at(side*.69,0,0),(.78,.48,.045),metal,q)
        cube('Photovoltaic wing',at(side*.69,0,.027),(.73,.43,.015),panel,q)
        for k in range(1,5): cube('Solar cell separator',at(side*.69-.365+k*.146,0,.037),(.009,.43,.004),lines,q)
        cube('Solar cell centerline',at(side*.69,0,.037),(.73,.008,.004),lines,q)
    rod('Antenna mast',at(.12,.12,.3),at(.12,.12,.66),.012,metal,8)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.035,location=at(.12,.12,.68)); bpy.context.object.name='Antenna tip'; bpy.context.object.data.materials.append(gold)
# Open space leaves the far-side satellites and struts visible through the sphere.
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.008,.014,.029,1); world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,power,size,color in [((5,-10,15),2200,10,(.78,.87,1)),((-12,-4,3),1500,9,(1,.73,.4)),((3,9,9),2600,8,(.35,.58,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color; o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(16,-22,13)); cam=bpy.context.object; cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=20; bpy.context.scene.camera=cam
bpy.context.scene.render.engine='CYCLES'; bpy.context.scene.render.resolution_x=1400; bpy.context.scene.render.resolution_y=1400; bpy.context.scene.render.resolution_percentage=100
