import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.35):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough; return m
red=mat('Cherry red lacquer',(.72,.035,.028),.18)
blue=mat('Ocean blue lacquer',(.025,.25,.52),.2)
yellow=mat('Golden yellow trim',(.98,.65,.06),.25)
black=mat('Soft charcoal',(.035,.045,.055),.1)
steel=mat('Bright metal',(.63,.7,.74),.75)
wood=mat('Beech track base',(.56,.32,.15),0,.65)
cream=mat('Cream lettering',(.96,.9,.7))

 def_placeholder = None
