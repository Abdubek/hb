import bpy,json

result={}
for name,points,quad,ngon,custom,keep in [
 ('beauty_quad',[(0,0,0),(3,0,0),(2,1,0),(0,2,0)],'BEAUTY','BEAUTY',False,False),
 ('beauty_ngon',[(0,0,0),(3,0,0),(3,2,0),(1.5,.7,0),(0,2,0)],'BEAUTY','BEAUTY',False,False),
 ('clip_ngon',[(0,0,0),(3,0,0),(3,2,0),(1.5,.7,0),(0,2,0)],'BEAUTY','CLIP',False,False),
 ('custom_keep',[(0,0,0),(3,0,0),(2,1,0),(0,2,0)],'BEAUTY','BEAUTY',True,True),
 ('custom_drop',[(0,0,0),(3,0,0),(2,1,0),(0,2,0)],'BEAUTY','BEAUTY',True,False)]:
 data=bpy.data.meshes.new(name);data.from_pydata(points,[],[tuple(range(len(points)))])
 layer=data.uv_layers.new(name='UVMap')
 for i in range(len(points)):layer.data[i].uv=(i*.13,i*.07)
 if custom:data.normals_split_custom_set([(0,.2+i*.1,1) for i in range(len(points))])
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 modifier=obj.modifiers.new('Triangulate','TRIANGULATE');modifier.quad_method=quad;modifier.ngon_method=ngon;modifier.keep_custom_normals=keep
 bpy.ops.object.modifier_apply(modifier=modifier.name)
 obj.name=name

