import bpy,bmesh,json,itertools
from mathutils import Matrix
from pathlib import Path
out={}
for op,shape,space_on in itertools.product(('translate','scale','rotate','transform'),(False,True),(False,True)):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;m=o.data;o.shape_key_add(name='Basis');key=o.shape_key_add(name='Raised');key.data[0].co.z+=.7
 bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table();verts=[bm.verts[0],bm.verts[4]]
 space=Matrix.Translation((.3,-.2,.4)) @ Matrix.Rotation(.4,4,'Z') if space_on else Matrix.Identity(4)
 if op=='translate':bmesh.ops.translate(bm,verts=verts,vec=(.3,-.4,1.2),space=space,use_shapekey=shape)
 if op=='scale':bmesh.ops.scale(bm,verts=verts,vec=(1.3,.6,-.8),space=space,use_shapekey=shape)
 if op=='rotate':bmesh.ops.rotate(bm,verts=verts,cent=(.2,-.4,.7),matrix=Matrix.Rotation(.7,3,'Y'),space=space,use_shapekey=shape)
 if op=='transform':bmesh.ops.transform(bm,verts=verts,matrix=Matrix.Translation((.2,.1,.3)) @ Matrix.Rotation(.7,4,'X'),space=space,use_shapekey=shape)
 bm.to_mesh(m)
 out[f'{op}_{shape}_{space_on}']=dict(vertices=[list(v.co) for v in m.vertices],keys={k.name:[list(v.co) for v in k.data] for k in m.shape_keys.key_blocks})
Path('/results/transform-reference.json').write_text(json.dumps(out,indent=2)+'\n')
