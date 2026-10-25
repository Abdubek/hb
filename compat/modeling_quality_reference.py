"""Run only in Blender; capture independent geometry measurements, no source extraction.

blender --background --factory-startup --python this.py -- output.json font.ttf
"""
import bpy
import json
import sys

output,font_path=sys.argv[sys.argv.index('--')+1:]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
records=[]

def record(name,obj):
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    vertices=[list(v.co) for v in mesh.vertices]
    faces=[list(p.vertices) for p in mesh.polygons]
    volume=0.
    for f in faces:
        a=mesh.vertices[f[0]].co
        for i in range(1,len(f)-1):
            b=mesh.vertices[f[i]].co;c=mesh.vertices[f[i+1]].co
            volume+=a.dot(b.cross(c))/6
    records.append(dict(name=name,vertices=vertices,faces=faces,volume=volume,
                        bounds=[[min(v[i] for v in vertices) for i in range(3)],
                                [max(v[i] for v in vertices) for i in range(3)]]))
    evaluated.to_mesh_clear()

for name,primitive in [('cylinder',lambda:bpy.ops.mesh.primitive_cylinder_add(vertices=16)),
                       ('frustum',lambda:bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=1,radius2=.4)),
                       ('cone',lambda:bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=1,radius2=0)),
                       ('icosphere',lambda:bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1))]:
    primitive();o=bpy.context.object;m=o.modifiers.new('Round','BEVEL');m.width=.08;m.segments=4;m.limit_method='ANGLE'
    record('bevel-'+name,o)

c=bpy.data.curves.new('Arc','CURVE');c.dimensions='3D';c.resolution_u=8
s=c.splines.new('BEZIER');s.bezier_points.add(1)
a,b=s.bezier_points;a.co=(0,0,0);b.co=(2,0,0)
a.handle_left_type=a.handle_right_type=b.handle_left_type=b.handle_right_type='FREE'
a.handle_right=(0,0,2);b.handle_left=(2,0,2)
o=bpy.data.objects.new('Arc',c);bpy.context.collection.objects.link(o)
record('bezier-wire',o)
c.bevel_depth=.05;c.use_fill_caps=True
record('bezier-capped',o)

font=bpy.data.fonts.load(font_path)
for body in ('O','B','HB','i','AV\nBO'):
    for size in (1.,2.):
        c=bpy.data.curves.new('Text','FONT');c.font=font;c.body=body;c.resolution_u=8;c.size=size;c.extrude=.1
        o=bpy.data.objects.new('Text',c);bpy.context.collection.objects.link(o)
        record('text-'+body+'-'+str(size),o)
with open(output,'w') as file:json.dump(dict(blender=bpy.app.version_string,records=records),file)
print('Wrote',len(records),'reference cases to',output)
