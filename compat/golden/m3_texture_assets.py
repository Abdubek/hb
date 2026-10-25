"""Blender-first wrapping, UV selection and transformed emissive asset chain."""
import bpy
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for i,mode in enumerate(('REPEAT','EXTEND','MIRROR')):
 bpy.ops.mesh.primitive_cube_add(location=(i*3,0,0));o=bpy.context.object;o.name=mode
 a=o.data.uv_layers[0];b=o.data.uv_layers.new(name='Detail');assert a.active_render and not b.active_render
 b.active_render=True;assert b.active_render and not a.active_render
 b.active_render=False;assert b.active_render
 for channel in range(2,8):o.data.uv_layers.new(name="UV"+str(channel))
 o.data.uv_layers[7].active_render=True;assert o.data.uv_layers[7].active_render and not b.active_render
 b.active_render=True;assert b.active_render and not o.data.uv_layers[7].active_render
 for uv in b.data:uv.uv=(uv.uv[0]*.5+.2,uv.uv[1]*.5+.1)
 m=bpy.data.materials.new(mode);m.use_nodes=True;o.data.materials.append(m)
 ns=m.node_tree.nodes;p=ns['Principled BSDF'];p.inputs['Emission Strength'].default_value=2
 im=bpy.data.images.new(mode,width=2,height=2);im.pixels=(1,0,0,1,0,1,0,1,0,0,1,1,1,1,1,1)
 t=ns.new('ShaderNodeTexImage');assert t.extension=='REPEAT';t.extension=mode;assert t.extension==mode;t.image=im
 tc=ns.new('ShaderNodeTexCoord');mp=ns.new('ShaderNodeMapping')
 mp.inputs['Location'].default_value=(.2,.3,0);mp.inputs['Rotation'].default_value=(0,0,.4);mp.inputs['Scale'].default_value=(2,3,1)
 l=m.node_tree.links;l.new(tc.outputs['UV'],mp.inputs['Vector']);l.new(mp.outputs['Vector'],t.inputs['Vector']);l.new(t.outputs['Color'],p.inputs['Base Color']);l.new(t.outputs['Color'],p.inputs['Emission Color'])
