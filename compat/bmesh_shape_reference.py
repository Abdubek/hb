import bpy,bmesh,json
from pathlib import Path
out={}
for mode in ('co','basis','raised','translate_false','translate_true','new_layer'):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;m=o.data;o.shape_key_add(name='Basis');k=o.shape_key_add(name='Raised');k.data[0].co.z+=1
 bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table()
 if mode=='co':bm.verts[0].co.z+=2
 if mode=='basis':bm.verts[0][bm.verts.layers.shape['Basis']].z+=2
 if mode=='raised':bm.verts[0][bm.verts.layers.shape['Raised']].z+=2
 if mode.startswith('translate'):bmesh.ops.translate(bm,verts=[bm.verts[0]],vec=(0,0,2),use_shapekey=mode.endswith('true'))
 if mode=='new_layer':
  layer=bm.verts.layers.shape.new('New');bm.verts.ensure_lookup_table();bm.verts[0][layer]=(2,3,4)
 bm.to_mesh(m)
 out[mode]=dict(vertices=[list(v.co) for v in m.vertices],keys={k.name:[list(v.co) for v in k.data] for k in m.shape_keys.key_blocks})
Path('/results/shape-reference.json').write_text(json.dumps(out,indent=2)+'\n')
print({n:dict(co=r['vertices'][0],keys={k:v[0] for k,v in r['keys'].items()}) for n,r in out.items()})
