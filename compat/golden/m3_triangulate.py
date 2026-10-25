import bpy
HB_FACE_ORDER_MESH_PREFIXES=('NgonBeauty','NgonClip')
def make(name,points,ngon='BEAUTY',custom=False,keep=False,smooth=False):
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],[list(range(len(points)))])
    layer=data.uv_layers.new(name='UVMap')
    for i in range(len(layer.data)):layer.data[i].uv=(i*.13,i*.07)
    data.polygons[0].use_smooth=smooth
    if custom:
        data.normals_split_custom_set([(0,.2+i*.1,1) for i in range(len(points))]);assert data.has_custom_normals
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    modifier=obj.modifiers.new('Triangles','TRIANGULATE');modifier.quad_method='BEAUTY';modifier.ngon_method=ngon;modifier.keep_custom_normals=keep
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=modifier.name)
quad=[(0,0,0),(3,0,0),(2,1,0),(0,2,0)]
ngon=[(0,0,0),(3,0,0),(3,2,0),(1.5,.7,0),(0,2,0)]
make('BeautyQuad',quad)
make('NgonBeauty',ngon)
make('NgonClip',ngon,ngon='CLIP')
make('CustomKeep',quad,custom=True,keep=True)
make('CustomReinterpret',quad,custom=True)
make('SmoothCustomKeep',quad,custom=True,keep=True,smooth=True)
