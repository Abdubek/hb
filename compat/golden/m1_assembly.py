"""M1 contract, written before implementing shared data blocks."""
HB_SYMBOLS = {
'bpy.data.meshes':'Mesh data blocks: iteration, lookup and creation',
'bpy.data.meshes.new':'new(name) creates an empty mesh',
'bpy.data.meshes.remove':'remove(mesh, do_unlink=True)',
'bpy.data.materials':'Material data blocks',
'bpy.data.materials.new':'new(name)',
'bpy.data.materials.remove':'remove(material, do_unlink=True)',
'bpy.data.cameras':'Camera data blocks',
'bpy.data.cameras.new':'new(name)',
'bpy.data.cameras.remove':'remove(camera, do_unlink=True)',
'bpy.data.lights':'Light data blocks',
'bpy.data.lights.new':'new(name, type): POINT, SUN, SPOT, AREA',
'bpy.data.lights.remove':'remove(light, do_unlink=True)',
'bpy.data.collections':'Collections, excluding the scene master collection',
'bpy.data.collections.new':'new(name)',
'bpy.data.collections.remove':'remove(collection, do_unlink=True)',
'bpy.data.objects.new':'new(name, object_data): mesh, camera, light or None',
'bpy.data.objects.remove':'remove(object, do_unlink=True)',
'bpy.types.Object.type':'MESH, CAMERA, LIGHT or EMPTY according to data block',
'bpy.types.Object.data':'Shared mesh, camera or light data block; None for an empty',
'bpy.types.Object.parent':'Object parent; local transforms retained',
'bpy.types.Object.children':'Immediate child objects',
'bpy.types.Object.users_collection':'Collections containing the object',
'bpy.types.Object.rotation_mode':'XYZ supported; other rotation modes fail explicitly',
'bpy.types.Object.hide_render':'Exclude object from renders',
'bpy.types.Object.copy':'Copy object, sharing its data and retaining transforms',
'bpy.types.Object.location.x':'Component access on transform views (see type deviation)',
'bpy.types.Mesh.name':'Unique mesh name',
'bpy.types.Mesh.users':'Number of referencing objects',
'bpy.types.Mesh.from_pydata':'from_pydata(vertices, edges, faces, shade_flat=True)',
'bpy.types.Mesh.update':'update(calc_edges=False, calc_edges_loose=False)',
'bpy.types.Mesh.vertices':'Mesh vertices; indexed/iterable with .co and .index',
'bpy.types.Mesh.edges':'Mesh edges with .vertices and .index',
'bpy.types.Mesh.polygons':'Mesh polygons with .vertices, .index, .material_index, .use_smooth',
'bpy.types.Mesh.materials':'Material slots: append, clear, pop, indexed access and assignment',
'bpy.types.Mesh.materials.append':'Append a material data block',
'bpy.types.Mesh.materials.clear':'Remove all material slots',
'bpy.types.Mesh.materials.pop':'pop(index=-1)',
'bpy.types.Mesh.copy':'Copy mesh geometry and material references',
'bpy.types.MeshVertex.co':'XYZ coordinate; assignment and indexed access',
'bpy.types.MeshVertex.index':'Zero-based vertex index',
'bpy.types.MeshEdge.vertices':'Two vertex indices',
'bpy.types.MeshPolygon.vertices':'Face vertex indices',
'bpy.types.MeshPolygon.material_index':'Material slot index',
'bpy.types.MeshPolygon.use_smooth':'Smooth or flat shading',
'bpy.types.Collection.name':'Unique collection name',
'bpy.types.Collection.objects':'Direct object membership',
'bpy.types.Collection.objects.link':'Link object to collection',
'bpy.types.Collection.objects.unlink':'Unlink object from collection',
'bpy.types.Collection.children':'Child collections',
'bpy.types.Collection.children.link':'Link child collection',
'bpy.types.Collection.children.unlink':'Unlink child collection',
'bpy.context.collection.objects.unlink':'Unlink from active collection',
'bpy.context.scene.collection':'Scene master collection',
'bpy.context.scene.camera':'Active camera object or None',
'bpy.context.view_layer.update':'Synchronize evaluated scene state',
'bpy.types.Material.name':'Unique material name',
'bpy.types.Material.diffuse_color':'Viewport RGBA, independent of node inputs',
'bpy.types.Material.metallic':'Non-node metallic factor',
'bpy.types.Material.roughness':'Non-node roughness factor',
'bpy.types.Material.use_nodes':'Enable or disable material node tree',
'bpy.types.Material.node_tree':'None until nodes are enabled; retained when disabled',
'bpy.types.Camera.name':'Unique camera data name',
'bpy.types.Camera.type':'PERSP or ORTHO; panoramic cameras fail explicitly',
'bpy.types.Camera.lens':'Focal length in millimeters',
'bpy.types.Camera.sensor_width':'Sensor width in millimeters',
'bpy.types.Camera.sensor_height':'Sensor height in millimeters',
'bpy.types.Camera.sensor_fit':'AUTO, HORIZONTAL or VERTICAL',
'bpy.types.Camera.clip_start':'Near clipping plane in meters',
'bpy.types.Camera.clip_end':'Far clipping plane in meters',
'bpy.types.Camera.ortho_scale':'Orthographic view scale',
'bpy.types.Camera.shift_x':'Horizontal lens shift',
'bpy.types.Camera.shift_y':'Vertical lens shift',
'bpy.types.Light.name':'Unique light name',
'bpy.types.Light.type':'POINT, SUN, SPOT, AREA',
'bpy.types.Light.energy':'Blender energy units',
'bpy.types.Light.color':'Linear RGB',
'bpy.types.Light.shadow_soft_size':'Point/spot source radius',
'bpy.types.Light.size':'Area source size',
'bpy.types.Light.spot_size':'Spot cone angle in radians',
'bpy.types.Light.spot_blend':'Spot cone edge softness',
'bpy.ops.object.select_all':'action: SELECT, DESELECT, INVERT or TOGGLE',
'bpy.ops.object.delete':'Delete selected objects in the scene; use_global supported',
'bpy.ops.object.shade_smooth':'Set mesh polygons to smooth shading',
'bpy.ops.object.shade_flat':'Set mesh polygons to flat shading',
}
import bpy
mesh=bpy.data.meshes.new('PanelMesh')
assert len(mesh.vertices)==0
mesh.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[],[(0,1,2,3)])
mesh.update()
assert len(mesh.vertices)==4 and len(mesh.edges)==4 and len(mesh.polygons)==1
assert tuple(mesh.polygons[0].vertices)==(0,1,2,3)
assert mesh.vertices[2].index==2
mesh.vertices[2].co=(1,1,.1)
assert tuple(mesh.vertices[0].co)==(-1,-1,0)
for edge in mesh.edges: assert len(edge.vertices)==2
mat=bpy.data.materials.new('Coating')
assert not mat.use_nodes and mat.node_tree is None
mat.diffuse_color=(.1,.3,.7,1)
mat.metallic=.25; mat.roughness=.6
mesh.materials.append(mat)
assert mesh.materials[0] is mat
mesh.polygons[0].material_index=0
mesh.polygons[0].use_smooth=True
obj=bpy.data.objects.new('Panel',mesh)
assert obj.data is mesh and mesh.users==1
bpy.context.collection.objects.link(obj)
copy=obj.copy();copy.name='SharedPanel'
bpy.context.collection.objects.link(copy)
assert copy.data is mesh and mesh.users==2
copy.location=(2,0,0)
copy.location.x=3
assert tuple(copy.location)==(3,0,0)
assert copy.rotation_mode=='XYZ'
copy.hide_render=True
anchor=bpy.data.objects.new('Anchor',None)
bpy.context.collection.objects.link(anchor)
anchor.location=(0,0,1)
obj.parent=anchor
assert obj.parent is anchor and obj in anchor.children
assert tuple(obj.location)==(0,0,0)
collection=bpy.data.collections.new('Assembly')
bpy.context.scene.collection.children.link(collection)
collection.objects.link(obj)
assert len(obj.users_collection)==2
bpy.context.collection.objects.unlink(obj)
assert tuple(c.name for c in obj.users_collection)==('Assembly',)
cam=bpy.data.cameras.new('Lens')
assert cam.type=='PERSP' and cam.lens==50 and cam.sensor_width==36
cam.lens=45;cam.sensor_width=32;cam.sensor_height=18;cam.sensor_fit='HORIZONTAL'
cam.clip_start=.1;cam.clip_end=100;cam.shift_x=.1;cam.shift_y=-.1
cam.ortho_scale=6
camera=bpy.data.objects.new('Camera',cam)
bpy.context.collection.objects.link(camera)
camera.location=(4,-6,4);camera.rotation_euler=(1.1,0,.6)
bpy.context.scene.camera=camera
assert bpy.context.scene.camera is camera and camera.type=='CAMERA'
for kind in ('POINT','SUN','SPOT','AREA'):
    data=bpy.data.lights.new(kind,kind)
    light=bpy.data.objects.new(kind,data)
    assert light.type=='LIGHT'
    bpy.context.collection.objects.link(light)
    data.energy=20;data.color=(1,.8,.6)
    light.location=(1,-2,4)
    if kind=='POINT':data.shadow_soft_size=.2
    if kind=='AREA':data.size=2
    if kind=='SPOT':data.spot_size=.8;data.spot_blend=.2
bpy.context.view_layer.update()
loose=mesh.copy();loose.name='LooseMesh';assert loose.users==0
removed=loose.materials.pop(index=0);assert removed is mat
loose.materials.append(mat);loose.materials.clear();assert len(loose.materials)==0
bpy.data.meshes.remove(loose)
unused=bpy.data.materials.new('Unused');bpy.data.materials.remove(unused)
unused=bpy.data.cameras.new('Unused');bpy.data.cameras.remove(unused)
unused=bpy.data.lights.new('Unused','POINT');bpy.data.lights.remove(unused)
unused=bpy.data.collections.new('Unused');bpy.data.collections.remove(unused)
unused=bpy.data.objects.new('Unused',None);bpy.data.objects.remove(unused)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True);bpy.context.view_layer.objects.active=obj
assert bpy.ops.object.shade_flat()=={'FINISHED'}
assert not mesh.polygons[0].use_smooth
assert bpy.ops.object.shade_smooth()=={'FINISHED'}
assert mesh.polygons[0].use_smooth
bpy.ops.mesh.primitive_cube_add();bpy.context.object.name='Temporary'
assert bpy.ops.object.delete()=={'FINISHED'}
assert bpy.data.objects.get('Temporary') is None
