import bpy,sys,json
from pathlib import Path
source,output=sys.argv[sys.argv.index('--')+1:]
for kind in ('objects','meshes','materials','cameras','lights','images','worlds','collections'):
    for block in list(getattr(bpy.data,kind)):getattr(bpy.data,kind).remove(block)
assert bpy.ops.wm.usd_import(filepath=source)=={'FINISHED'}
objects={}
def material(m):
    if not m or not m.use_nodes:return None
    shader=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not shader:return None
    return {name:list(shader.inputs[name].default_value) if name in ('Base Color','Emission Color') else shader.inputs[name].default_value for name in ('Base Color','Metallic','Roughness','Alpha','Emission Color','Emission Strength')}
for obj in bpy.data.objects:
    if obj.type=='EMPTY':continue
    record={'world':[list(row) for row in obj.matrix_world]}
    if obj.type=='MESH':
        mesh=obj.data;key='mesh_'+str(len(mesh.vertices))+'_'+str(len(mesh.polygons));mesh.update();normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
        record['vertices']=len(mesh.vertices);record['faces']=[]
        for poly in mesh.polygons:
            corners=[]
            for loop in poly.loop_indices:
                vertex=mesh.vertices[mesh.loops[loop].vertex_index]
                normal=(normal_matrix@mesh.corner_normals[loop].vector).normalized()
                corners.append([list(obj.matrix_world@vertex.co),list(mesh.uv_layers.active.data[loop].uv) if mesh.uv_layers.active else None,list(normal)])
            mat=mesh.materials[poly.material_index] if poly.material_index<len(mesh.materials) else None
            record['faces'].append({'corners':corners,'material':material(mat),'smooth':poly.use_smooth})
    elif obj.type=='CAMERA':
        key='camera_'+obj.data.type
        if obj.data.type=='ORTHO':record.update(ortho_scale=obj.data.ortho_scale,shift_x=obj.data.shift_x,shift_y=obj.data.shift_y)
        record.update(lens=obj.data.lens,sensor_width=obj.data.sensor_width,sensor_height=obj.data.sensor_height,near=obj.data.clip_start,far=obj.data.clip_end)
    else:
        d=obj.data;key='light_'+d.type;record.update(energy=d.energy,color=list(d.color))
        if d.type=='AREA':record.update(shape=d.shape,size=d.size,size_y=d.size_y)
        if d.type=='SPOT':record.update(angle=d.spot_size,blend=d.spot_blend)
    assert key not in objects;objects[key]=record
Path(output).write_text(json.dumps(objects,indent=2)+'\n')
