"""WELD comparisons keep vertex indices, oriented faces, UV corners and weights.

Edge storage order is irrelevant here; undirected connectivity is exact.
"""
def close(a,b,tolerance=1e-5):
    if isinstance(a,list):
        assert len(a)==len(b),(len(a),len(b))
        for x,y in zip(a,b):close(x,y,tolerance)
    else:assert abs(a-b)<=tolerance,(a,b)

def compare(reference,scene):
    meshes={m['id']:m for m in scene['meshes']};objects={o['name']:o for o in scene['objects']}
    for name,expected in reference.items():
        mesh=meshes[objects[name]['data']['id']]
        actual=dict(vertices=mesh['vertices'],edges=mesh['edges'],faces=mesh['faces'],uv=mesh['uv_layers'][0]['data'] if mesh['uv_layers'] else [],weights=mesh.get('deform_weights',[[] for _ in mesh['vertices']]))
        for key in expected:
            if key in ('input','input_faces'):continue
            a,b=expected[key],actual[key]
            if key=='edges':a=sorted(sorted(e) for e in a);b=sorted(sorted(e) for e in b)
            try:close(a,b)
            except AssertionError as error:raise AssertionError((name,key,error.args)) from error

def random_script(reference):
    source='import bpy\n'
    for name,r in reference.items():
        parts=name.split('_');mode=parts[2];invert=parts[3]=='True'
        source+=f"m=bpy.data.meshes.new({name!r});m.from_pydata({r['input']!r},[(i,i+1) for i in range(19)],[])\no=bpy.data.objects.new({name!r},m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o\ng=o.vertex_groups.new(name='Mask')\nfor i in range(20):g.add([i],[0,.2,1][i%3],'REPLACE')\nw=o.modifiers.new('Weld','WELD');w.mode={mode!r};w.merge_threshold=.105;w.vertex_group='Mask';w.invert_vertex_group={invert!r}\nbpy.ops.object.modifier_apply(modifier=w.name)\n"
    return source

def face_script(reference):
    source='import bpy\n'
    for name,r in reference.items():
        mode=name.rsplit('_',1)[1]
        source+=f"m=bpy.data.meshes.new({name!r});m.from_pydata({r['input']!r},[],{r['input_faces']!r})\nu=m.uv_layers.new(name='UVMap')\nfor i,d in enumerate(u.data):d.uv=(i*.13,i*.07)\no=bpy.data.objects.new({name!r},m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o\nw=o.modifiers.new('Weld','WELD');w.mode={mode!r};w.merge_threshold=.1\nbpy.ops.object.modifier_apply(modifier=w.name)\n"
    return source
