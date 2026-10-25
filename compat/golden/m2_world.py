import bpy
HB_SYMBOLS={
'bpy.context.scene.world':'Scene world datablock reference',
'bpy.data.worlds.new':'Create a named World with constant-color settings',
'bpy.data.worlds.remove':'Remove a World and unlink scene users',
'bpy.data.worlds.get':'Look up a World by name',
'bpy.types.World.color':'Persistent RGB world color',
'bpy.types.World.use_nodes':'Read node usage; disabling nodes selects constant-color lighting',
'bpy.types.World.name':'World datablock name',
'bpy.types.World.users':'World scene user count',
}
w=bpy.context.scene.world
assert w.name=='World' and w.use_nodes
assert abs(w.color[0]-.05087608844041824)<1e-8
w.use_nodes=False;assert not w.use_nodes
w.color=(.1,.2,.3)
n=bpy.data.worlds.new('Studio');assert not n.use_nodes and n.users==0
assert all(abs(c-.05)<1e-6 for c in n.color)
n.color=(-1,2,3);assert tuple(n.color)==(0,2,3)
n.color=(.12,.18,.24);bpy.context.scene.world=n;assert n.users==1
assert bpy.data.worlds.get('Studio') is n
bpy.data.worlds.remove(w);assert bpy.data.worlds.get('World') is None
