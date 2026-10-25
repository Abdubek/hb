"""Legacy OBJ/MTL export: transforms, reflected winding, UVs and scalar material."""
HB_BLENDER_REFERENCE=('3.6',)
import bpy,os,math
bpy.ops.mesh.primitive_cube_add(location=(1,2,3))
cube=bpy.context.object;cube.name='Export cube';cube.scale=(-2,1,1)
material=bpy.data.materials.new('Export paint');material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.2,.4,.6,1)
shader.inputs['Metallic'].default_value=.3
shader.inputs['Roughness'].default_value=.25
shader.inputs['Alpha'].default_value=.8
try:shader.inputs['Emission Color'].default_value=(0,0,0,1)
except KeyError:shader.inputs['Emission'].default_value=(0,0,0,1)
shader.inputs['Emission Strength'].default_value=0
cube.data.materials.append(material)
directory=os.path.join(os.environ.get('TMPDIR','/tmp'),'hb-obj-export-'+str(os.getpid()))
os.makedirs(directory,exist_ok=True)
try:
    path=os.path.join(directory,'scene.obj')
    assert bpy.ops.export_scene.obj(filepath=path,use_selection=True)=={'FINISHED'}
    lines=[line.split() for line in open(path) if line.strip() and not line.startswith('#')]
    vertices=[tuple(map(float,line[1:])) for line in lines if line[0]=='v']
    faces=[line[1:] for line in lines if line[0]=='f']
    normals=[tuple(map(float,line[1:])) for line in lines if line[0]=='vn']
    assert len(vertices)==8 and len(faces)==6 and all(len(face)==4 for face in faces)
    assert [min(v[i] for v in vertices) for i in range(3)]==[-1,2,-3]
    assert [max(v[i] for v in vertices) for i in range(3)]==[3,4,-1]
    for face in faces:
        refs=[tuple(map(int,corner.split('/'))) for corner in face]
        assert all(len(ref)==3 and all(i>0 for i in ref) for ref in refs)
        a,b,c=[vertices[ref[0]-1] for ref in refs[:3]]
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        assert sum(x*y for x,y in zip(cross,normals[refs[0][2]-1]))>0
    mtl=next(line[1] for line in lines if line[0]=='mtllib')
    factors={line[0]:line[1:] for line in (line.split() for line in open(os.path.join(directory,mtl))) if line and not line[0].startswith('#')}
    assert all(abs(a-b)<1e-5 for a,b in zip(map(float,factors['Kd']),(.2,.4,.6)))
    assert abs(float(factors['Ns'][0])-562.5)<1e-5
    assert abs(float(factors['d'][0])-.8)<1e-5
    assert factors['illum']==['6']
    path=os.path.join(directory,'triangles.obj')
    assert bpy.ops.export_scene.obj(filepath=path,use_triangles=True,use_uvs=False,use_materials=False,axis_forward='Y',axis_up='Z')=={'FINISHED'}
    lines=[line.split() for line in open(path) if line.strip() and not line.startswith('#')]
    faces=[line[1:] for line in lines if line[0]=='f']
    assert len(faces)==12 and all(len(face)==3 for face in faces)
    assert not any(line[0] in ('vt','mtllib','usemtl') for line in lines)
    modifier=cube.modifiers.new('Copies','ARRAY');modifier.count=2
    path=os.path.join(directory,'applied.obj')
    assert bpy.ops.export_scene.obj(filepath=path,use_normals=False,use_uvs=False,use_materials=False,global_scale=2)=={'FINISHED'}
    lines=[line.split() for line in open(path) if line.strip() and not line.startswith('#')]
    vertices=[tuple(map(float,line[1:])) for line in lines if line[0]=='v']
    faces=[line[1:] for line in lines if line[0]=='f']
    assert len(vertices)==16 and len(faces)==12
    assert min(v[0] for v in vertices)==-10 and max(v[0] for v in vertices)==6
    assert all('/' not in corner for face in faces for corner in face)
    path=os.path.join(directory,'unapplied.obj')
    assert bpy.ops.export_scene.obj(filepath=path,use_mesh_modifiers=False)=={'FINISHED'}
    assert sum(line.startswith('f ') for line in open(path))==6
finally:
    for name in os.listdir(directory):os.unlink(os.path.join(directory,name))
    os.rmdir(directory)
