"""Collection protocols, ID users, and default numeric values."""
HB_SYMBOLS={
'bpy.data.meshes.get':'Name lookup with optional fallback',
'bpy.data.materials.get':'Name lookup with optional fallback',
'bpy.data.cameras.get':'Name lookup with optional fallback',
'bpy.data.lights.get':'Name lookup with optional fallback',
'bpy.data.collections.get':'Name lookup with optional fallback',
'bpy.data.images.get':'Name lookup with optional fallback',
'bpy.types.Object.users':'Number of collection memberships (parent and scene-camera pointers do not increment ID users)',
'bpy.types.Material.users':'Number of mesh slots referencing the material',
'bpy.types.Camera.users':'Referencing objects',
'bpy.types.Light.users':'Referencing objects',
'bpy.types.Collection.users':'Parent collection references',
'bpy.types.Image.users':'Referencing texture nodes',
'bpy.types.MeshEdge.index':'Zero-based mesh edge index',
'bpy.types.MeshPolygon.index':'Zero-based polygon index',
'bpy.types.NodeSocket.name':'Socket name',
'bpy.types.NodeLink.from_node':'Linked output node',
'bpy.types.NodeLink.to_node':'Linked input node',
'bpy.types.NodeLink.from_socket':'Linked output socket',
'bpy.types.NodeLink.to_socket':'Linked input socket',
}
import bpy
for db,args in [(bpy.data.meshes,()),(bpy.data.materials,()),(bpy.data.cameras,()),(bpy.data.lights,('POINT',)),(bpy.data.collections,()),(bpy.data.images,(1,1))]:
    block=db.new('Database test',*args)
    assert db.get('Database test') is block
    assert db['Database test'] is block and block in list(db)
    assert db.get('missing',17)==17
    assert block.users==0
    db.remove(block)
m=bpy.data.materials.new('Defaults');assert abs(m.roughness-.4)<1e-6
m.use_nodes=True;n=m.node_tree.nodes['Principled BSDF']
assert tuple(n.inputs['Emission Color'].default_value)==(1,1,1,1)
assert n.inputs['Emission Strength'].default_value==0
for kind in ['POINT','SPOT']:
    l=bpy.data.lights.new('Radius',kind);assert l.shadow_soft_size==0
    bpy.data.lights.remove(l)
parent=bpy.data.objects.new('Parent',None);child=bpy.data.objects.new('Child',None)
assert parent.users==0
bpy.context.collection.objects.link(parent);assert parent.users==1
child.parent=parent;assert parent.users==1
bpy.data.objects.remove(child);assert parent.users==1
bpy.ops.mesh.primitive_cube_add();o=bpy.context.object
assert o.data.edges[0].index==0 and o.data.polygons[0].index==0
o.data.materials.append(m);assert m.users==1
image=bpy.data.images.new('Node image',1,1);assert tuple(image.pixels[:])==(0,0,0,1)
tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;assert image.users==1
link=m.node_tree.links.new(tex.outputs['Color'],n.inputs['Base Color'])
assert link.from_node==tex and link.to_node==n
assert link.from_socket.name=='Color' and link.to_socket.name=='Base Color'
bpy.data.objects.remove(parent)
