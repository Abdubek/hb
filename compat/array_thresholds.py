"""ARRAY exact-zero and inclusive-boundary merge references."""
import bpy,json,os
result={}
for name,offset,threshold in [('zero',0,0),('boundary',1.25,.25),('near',1.125,.25)]:
    data=bpy.data.meshes.new(name);data.from_pydata([(0,0,0),(1,0,0)],[(0,1)],[])
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    modifier=obj.modifiers.new('Array','ARRAY');modifier.count=2
    modifier.use_relative_offset=False;modifier.use_constant_offset=True
    modifier.constant_offset_displace=(offset,0,0);modifier.use_merge_vertices=True;modifier.merge_threshold=threshold
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    data=obj.data
    result[name]={'vertices':[list(v.co) for v in data.vertices],'faces':[list(f.vertices) for f in data.polygons],'edges':[list(e.vertices) for e in data.edges],'uv':[]}
with open(os.environ['HB_ARRAY_THRESHOLD_RESULTS'],'w') as output:json.dump(result,output)
