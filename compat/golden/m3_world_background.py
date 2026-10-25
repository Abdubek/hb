import bpy

def near(a,b):
    assert len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b)),(tuple(a),b)
w=bpy.data.worlds.new('NodeWorld')
assert w.node_tree is None and not w.use_nodes
w.color=(.1,.2,.3);w.use_nodes=True
nt=w.node_tree;bg=nt.nodes['Background'];out=nt.nodes['World Output']
assert bg.type=='BACKGROUND' and bg.bl_idname=='ShaderNodeBackground'
assert out.type=='OUTPUT_WORLD'
near(bg.inputs['Color'].default_value,(.1,.2,.3,1))
assert bg.inputs['Strength'].default_value==1
w.color=(.7,.8,.9);near(bg.inputs['Color'].default_value,(.1,.2,.3,1))
bg.inputs['Color'].default_value=(-1,2,3,4);near(bg.inputs['Color'].default_value,(0,2,3,4))
bg.inputs['Color'].default_value[1]=.25
bg.inputs['Strength'].default_value=-3;assert bg.inputs['Strength'].default_value==-3
bg.inputs['Strength'].default_value=2.5
w.use_nodes=False;assert w.node_tree.nodes['Background'].inputs['Strength'].default_value==2.5
w.use_nodes=True
bg.name='Studio Background';assert nt.nodes.get('Studio Background')==bg
im=bpy.data.images.new('Environment',width=2,height=1,float_buffer=True)
im.pixels=(.1,.2,.3,1,.4,.5,.6,1)
env=nt.nodes.new('ShaderNodeTexEnvironment');assert env.type=='TEX_ENVIRONMENT'
assert env.projection=='EQUIRECTANGULAR' and env.interpolation=='Linear'
env.projection='EQUIRECTANGULAR';env.interpolation='Linear';env.image=im
assert env.image is im and im.users==1
link=nt.links.new(env.outputs['Color'],bg.inputs['Color']);assert link.from_node==env and link.to_node==bg
bpy.context.scene.world=w
copy=w.copy();assert copy.node_tree.nodes['Studio Background'].inputs['Strength'].default_value==2.5
assert im.users==2
copy.node_tree.nodes.clear();assert len(copy.node_tree.nodes)==0 and im.users==1
bpy.data.worlds.remove(copy)
bpy.data.images.remove(im);assert env.image is None
im=bpy.data.images.new('UniformEnvironment',width=2,height=1,float_buffer=True)
im.pixels=(.25,.5,.75,1)*2;env.image=im
# A mesh allows the standard cross-engine export observer to run.
bpy.ops.mesh.primitive_cube_add()
