import bpy

def close(actual,expected,path):
    if isinstance(expected,dict):
        assert set(actual)==set(expected),(path,tuple(actual),tuple(expected))
        for key in expected:close(actual[key],expected[key],path+'.'+key)
    elif isinstance(expected,list):
        assert len(actual)==len(expected),(path,len(actual),len(expected))
        for index,(a,b) in enumerate(zip(actual,expected)):close(a,b,path+'.'+str(index))
    elif isinstance(expected,(float,int)) and not isinstance(expected,bool):assert abs(actual-expected)<=1e-5,(path,actual,expected)
    else:assert actual==expected,(path,actual,expected)

def state():
    return dict(objects={o.name:dict(data=o.data.name if o.data else None,parent=o.parent.name if o.parent else None,location=list(o.location),rotation_euler=list(o.rotation_euler),scale=list(o.scale),world=[list(r) for r in o.matrix_world]) for o in bpy.data.objects},meshes={m.name:dict(vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],users=m.users) for m in bpy.data.meshes})

def check_stage(reference,stage,key):
    expected=reference[stage]
    for obj in expected['objects'].values():obj.pop('parent_inverse',None)
    close(state(),expected,key+'.'+stage)

for key,row in references.items():
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    for mesh in list(bpy.data.meshes):bpy.data.meshes.remove(mesh)
    kind=row['kind'];negative=row['negative']
    if row['operation']=='apply':
        bpy.ops.mesh.primitive_cube_add(calc_uvs=False);obj=bpy.context.object;obj.name='Target'
        obj.location=(1,2,3);obj.rotation_euler=(.3,-.4,.7);obj.scale=(-.5 if negative else .5,1.2,2)
        if kind in ('parent','both'):
            parent=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(parent)
            parent.location=(2,-3,1);parent.rotation_euler=(-.2,.3,.5);parent.scale=(1.2,.8,2);obj.parent=parent
        if kind in ('child','both'):
            child=bpy.data.objects.new('Child',None);bpy.context.collection.objects.link(child)
            child.location=(2,-1,3);child.rotation_euler=(-.3,.4,-.1);child.parent=obj
        if kind.startswith('shared'):
            shared=bpy.data.objects.new('Shared',obj.data);bpy.context.collection.objects.link(shared);shared.location=(-3,2,1)
            if row.get('transformed_shared'):shared.rotation_euler=(.2,.4,-.7);shared.scale=(.8,1.3,1.7)
            if kind=='shared_selected':shared.select_set(True)
        check_stage(row,'before',key)
        try:result=sorted(bpy.ops.object.transform_apply(location=row['flags'][0],rotation=row['flags'][1],scale=row['flags'][2],isolate_users=row['isolate']));error=None
        except Exception as exception:result=None;error=str(exception)
    else:
        bpy.ops.mesh.primitive_cube_add(calc_uvs=False);active=bpy.context.object;active.name='Active'
        active.location=(1,2,3);active.rotation_euler=(.3,-.4,.7);active.scale=(-.5 if negative in ('active','both') else .5,1.2,2)
        bpy.ops.mesh.primitive_cube_add(calc_uvs=False);source=bpy.context.object;source.name='Source'
        source.location=(-2,1,-1);source.rotation_euler=(-.2,.5,-.3);source.scale=(-.8 if negative in ('source','both') else .8,.7,1.4)
        if kind.startswith('parent_'):
            parent=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(parent)
            parent.location=(2,-3,1);parent.rotation_euler=(-.2,.3,.5);parent.scale=(1.2,.8,2)
            if kind=='parent_active':active.parent=parent
            else:source.parent=parent
        if kind.startswith('child_'):
            child=bpy.data.objects.new('Child',None);bpy.context.collection.objects.link(child)
            child.location=(2,-1,3);child.rotation_euler=(-.3,.4,-.1);child.parent=active if kind=='child_active' else source
        if kind=='source_parent_active':active.parent=source
        if kind=='active_parent_source':source.parent=active
        if kind.startswith('shared_'):
            shared=bpy.data.objects.new('Shared',active.data if kind=='shared_active' else source.data);bpy.context.collection.objects.link(shared);shared.location=(-3,2,1)
            if kind=='shared_selected':shared.select_set(True)
        active.select_set(True);source.select_set(True);bpy.context.view_layer.objects.active=active
        check_stage(row,'before',key)
        try:result=sorted(bpy.ops.object.join());error=None
        except Exception as exception:result=None;error=str(exception)
    assert bool(error)==bool(row['error']),(key,error,row['error'])
    assert result==row['result'],(key,result,row['result'])
    check_stage(row,'after',key)
