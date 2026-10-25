import bpy,sys,json
from pathlib import Path
source,output=sys.argv[sys.argv.index('--')+1:]
for kind in ('objects','meshes','materials','cameras','lights','images','worlds','collections'):
    for block in list(getattr(bpy.data,kind)):getattr(bpy.data,kind).remove(block)
assert bpy.ops.wm.usd_import(filepath=source)=={'FINISHED'}
result={}
for material in bpy.data.materials:
    shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for socket in ('Base Color','Alpha'):
        node=shader.inputs[socket].links[0].from_node
        assert node.type=='TEX_IMAGE',[(n.type,n.name) for n in material.node_tree.nodes]
        result[socket]={'size':list(node.image.size),'pixels':list(node.image.pixels),'space':node.image.colorspace_settings.name}
Path(output).write_text(json.dumps(result,indent=2)+'\n')
