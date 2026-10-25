"""Read Blender reference state. Only this observer uses unrestricted Blender RNA."""
import bpy

def observe():
    objects=[]
    for o in sorted(bpy.data.objects,key=lambda o:o.name):
        mesh=None
        if o.type=='MESH':
            m=o.data
            mesh=dict(name=m.name,vertices=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],uv=[list(x.uv) for x in m.uv_layers.active.data] if m.uv_layers else [])
        objects.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,data=o.data.name if o.data else None,location=list(o.location),rotation_euler=list(o.rotation_euler),scale=list(o.scale),selected=o.select_get(),linked=o.name in bpy.context.scene.objects,mesh=mesh))
        if o.type=='MESH' and len(o.vertex_groups):objects[-1]['vertex_groups']=[g.name for g in o.vertex_groups]
        modifiers=[]
        for modifier in o.modifiers:
            record=dict(name=modifier.name,type=modifier.type)
            if modifier.type=='WEIGHTED_NORMAL':
                for key in ('mode','weight','thresh','keep_sharp','use_face_influence','vertex_group','invert_vertex_group','show_viewport','show_render'):record[key]=getattr(modifier,key)
            if modifier.type=='ARRAY':
                for key in ('count','fit_type','use_relative_offset','use_constant_offset','use_merge_vertices','use_object_offset','show_viewport','show_render'):record[key]=getattr(modifier,key)
                for key in ('relative_offset_displace','constant_offset_displace'):record[key]=list(getattr(modifier,key))
            if modifier.type=='MIRROR':
                record.update(use_axis=list(modifier.use_axis),use_mirror_merge=modifier.use_mirror_merge,merge_threshold=modifier.merge_threshold,use_clip=modifier.use_clip,show_viewport=modifier.show_viewport,show_render=modifier.show_render)
            if modifier.type=='TRIANGULATE':
                for key in ('quad_method','ngon_method','min_vertices','keep_custom_normals','show_viewport','show_render'):record[key]=getattr(modifier,key)
            if modifier.type=='BEVEL':
                for key in ('width','segments','affect','offset_type','limit_method','angle_limit','profile','use_clamp_overlap','loop_slide','harden_normals','material','show_viewport','show_render'):record[key]=getattr(modifier,key)
            if modifier.type=='DISPLACE':
                for key in ('strength','mid_level','direction','space','texture_coords','vertex_group','invert_vertex_group','show_viewport','show_render'):record[key]=getattr(modifier,key)
                record['texture']=modifier.texture.name if modifier.texture else None
            if modifier.type=='SUBSURF':
                for key in ('subdivision_type','levels','render_levels','quality','uv_smooth','boundary_smooth','use_limit_surface','use_creases','show_only_control_edges','show_viewport','show_render'):record[key]=getattr(modifier,key)
                if modifier.use_custom_normals:record['use_custom_normals']=True
            if modifier.type=='BOOLEAN':
                for key in ('operation','solver','operand_type','material_mode','use_self','use_hole_tolerant','double_threshold','show_viewport','show_render'):record[key]=getattr(modifier,key)
                record['object']=modifier.object.name if modifier.object else None
                if modifier.operand_type=='COLLECTION' or modifier.collection:record['collection']=modifier.collection.name if modifier.collection else None
            if modifier.type=='WELD':
                for key in ('mode','merge_threshold','loose_edges','vertex_group','invert_vertex_group','show_viewport','show_render'):record[key]=getattr(modifier,key)
            if modifier.type=='SOLIDIFY':
                for key in ('solidify_mode','thickness','offset','use_rim','use_rim_only','use_even_offset','use_quality_normals','thickness_clamp','material_offset','material_offset_rim','show_viewport','show_render'):record[key]=getattr(modifier,key)
            modifiers.append(record)
        objects[-1]['modifiers']=modifiers
    mats=[]
    for m in sorted(bpy.data.materials,key=lambda m:m.name):
        nodes=[]
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.bl_idname=='ShaderNodeBsdfPrincipled':
                    # Blender 3.6 names the same emission socket "Emission".
                    def socket(k):return n.inputs['Emission' if k=='Emission Color' and k not in n.inputs else k].default_value
                    inputs={k:(list(socket(k)) if k in ('Base Color','Emission Color','Normal') else socket(k)) for k in ('Base Color','Metallic','Roughness','Alpha','Emission Color','Emission Strength','Normal')}
                elif n.bl_idname=='ShaderNodeNormalMap':inputs={k:(list(n.inputs[k].default_value) if k=='Color' else n.inputs[k].default_value) for k in ('Strength','Color')}
                elif n.bl_idname=='ShaderNodeTexImage':inputs={'Vector':list(n.inputs['Vector'].default_value)}
                elif n.bl_idname=='ShaderNodeMapping':inputs={k:list(n.inputs[k].default_value) for k in ('Vector','Location','Rotation','Scale')}
                elif n.bl_idname=='ShaderNodeTexCoord':inputs={}
                else:inputs={'Surface':None}
                nodes.append(dict(name=n.name,type=n.bl_idname,inputs=inputs,image=n.image.name if n.bl_idname=='ShaderNodeTexImage' and n.image else None))
        mats.append(dict(name=m.name,diffuse_color=list(m.diffuse_color),metallic=m.metallic,roughness=m.roughness,use_nodes=m.use_nodes,nodes=nodes))
    meshes=[]
    for m in sorted(bpy.data.meshes,key=lambda m:m.name):
        meshes.append(dict(name=m.name,materials=[x.name if x else None for x in m.materials],material_indices=[p.material_index for p in m.polygons],smooth=[p.use_smooth for p in m.polygons],uv_layers=[dict(name=l.name,data=[list(x.uv) for x in l.data]) for l in m.uv_layers]))
        weights=[[[g.group,g.weight] for g in v.groups] for v in m.vertices]
        if any(weights):meshes[-1]['deform_weights']=weights
    cameras=[{k:(getattr(c,k)) for k in ('name','type','lens','sensor_width','sensor_height','sensor_fit','clip_start','clip_end','ortho_scale','shift_x','shift_y')} for c in sorted(bpy.data.cameras,key=lambda c:c.name)]
    lights=[]
    for l in sorted(bpy.data.lights,key=lambda l:l.name):
        d=dict(name=l.name,type=l.type,energy=l.energy,color=list(l.color),use_shadow=l.use_shadow)
        for field,types in [('shadow_soft_size',('POINT','SPOT')),('size',('AREA',)),('size_y',('AREA',)),('shape',('AREA',)),('spot_size',('SPOT',)),('spot_blend',('SPOT',))]:
            if l.type in types:d[field]=getattr(l,field)
        lights.append(d)
    collections=[dict(name=c.name,objects=sorted(o.name for o in c.objects),children=sorted(x.name for x in c.children)) for c in sorted(bpy.data.collections,key=lambda c:c.name)]
    images=[dict(name=i.name,size=list(i.size),pixels=list(i.pixels),colorspace=i.colorspace_settings.name) for i in sorted(bpy.data.images,key=lambda i:i.name)]
    textures=[{k:getattr(t,k) for k in ('name','type','noise_basis','noise_scale','noise_depth','noise_type','cloud_type','intensity','contrast')} for t in sorted(bpy.data.textures,key=lambda t:t.name)]
    worlds=[dict(name=w.name,color=list(w.color),use_nodes=w.use_nodes) for w in sorted(bpy.data.worlds,key=lambda w:w.name)]
    return dict(worlds=worlds,world=bpy.context.scene.world.name if bpy.context.scene.world else None,objects=objects,meshes=meshes,materials=mats,cameras=cameras,lights=lights,collections=collections,images=images,textures=textures,camera=bpy.context.scene.camera.name if bpy.context.scene.camera else None)
