"""Explicit glTF operator outputs: binary/separate, selection, applied modifiers."""
import bpy,json,struct,os
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
cube=bpy.context.object;cube.name='Export cube'
modifier=cube.modifiers.new('Copies','ARRAY');modifier.count=2
bpy.ops.object.camera_add(location=(0,-6,3));bpy.context.object.name='Export camera'
bpy.ops.object.light_add(type='POINT',location=(2,-2,4));bpy.context.object.name='Export light'
bpy.ops.object.select_all(action='DESELECT');cube.select_set(True)
directory=os.path.join(os.environ.get('TMPDIR','/tmp'),'hb-export-'+str(os.getpid()))
os.makedirs(directory,exist_ok=True)
try:
    def document(path):
        raw=open(path,'rb').read()
        if path.endswith('.glb'):
            magic,version,size=struct.unpack_from('<III',raw)
            assert magic==0x46546c67 and version==2 and size==len(raw)
            count,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
            return json.loads(raw[20:20+count])
        return json.loads(raw)
    path=os.path.join(directory,'selected.glb')
    assert bpy.ops.export_scene.gltf(filepath=path,use_selection=True,export_apply=True)=={'FINISHED'}
    doc=document(path)
    assert [node['name'] for node in doc['nodes']]==['Export cube']
    primitive=doc['meshes'][0]['primitives'][0]
    assert doc['accessors'][primitive['indices']]['count']==72
    path=os.path.join(directory,'scene.gltf')
    assert bpy.ops.export_scene.gltf(filepath=path,export_format='GLTF_SEPARATE',export_cameras=True,export_lights=True)=={'FINISHED'}
    doc=document(path)
    assert {node['name'] for node in doc['nodes']}=={'Export cube','Export camera','Export light'}
    assert len(doc['cameras'])==1
    assert len(doc['extensions']['KHR_lights_punctual']['lights'])==1
    primitive=doc['meshes'][0]['primitives'][0]
    assert doc['accessors'][primitive['indices']]['count']==36
    assert len(open(os.path.join(directory,doc['buffers'][0]['uri']),'rb').read())==doc['buffers'][0]['byteLength']
    path=os.path.join(directory,'default.glb')
    assert bpy.ops.export_scene.gltf(filepath=path)=={'FINISHED'}
    doc=document(path)
    assert [node['name'] for node in doc['nodes']]==['Export cube']
finally:
    for name in os.listdir(directory):os.unlink(os.path.join(directory,name))
    os.rmdir(directory)
