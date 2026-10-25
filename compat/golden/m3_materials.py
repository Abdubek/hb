"""Blender-first Principled inputs and a single UV/Mapping/Image chain."""
import bpy
import math
HB_GLTF_MATERIAL_NAMES=('Glass',)
DEFAULTS={'Base Color': [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0], 'Metallic': 0.0, 'Roughness': 0.5, 'IOR': 1.5, 'Alpha': 1.0, 'Normal': [0.0, 0.0, 0.0], 'Diffuse Roughness': 0.0, 'Subsurface Weight': 0.0, 'Subsurface Radius': [1.0, 0.20000000298023224, 0.10000000149011612], 'Subsurface Scale': 0.05000000074505806, 'Subsurface Anisotropy': 0.0, 'Specular IOR Level': 0.5, 'Specular Tint': [1.0, 1.0, 1.0, 1.0], 'Anisotropic': 0.0, 'Anisotropic Rotation': 0.0, 'Tangent': [0.0, 0.0, 0.0], 'Transmission Weight': 0.0, 'Coat Weight': 0.0, 'Coat Roughness': 0.029999999329447746, 'Coat IOR': 1.5, 'Coat Tint': [1.0, 1.0, 1.0, 1.0], 'Coat Normal': [0.0, 0.0, 0.0], 'Sheen Weight': 0.0, 'Sheen Roughness': 0.5, 'Sheen Tint': [1.0, 1.0, 1.0, 1.0], 'Emission Color': [1.0, 1.0, 1.0, 1.0], 'Emission Strength': 0.0, 'Thin Film Thickness': 0.0, 'Thin Film IOR': 1.3300000429153442}
def near(a,b):
    if isinstance(b,list):assert len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b)),(tuple(a),b)
    else:assert abs(a-b)<1e-6,(a,b)
m=bpy.data.materials.new('Glass');m.use_nodes=True
n=m.node_tree.nodes['Principled BSDF']
for key,default in DEFAULTS.items():
    near(n.inputs[key].default_value,default)
    if key in ('Normal','Tangent','Coat Normal'):continue
    for value in ([-2.]*len(default) if isinstance(default,list) else -2., [2.]*len(default) if isinstance(default,list) else 2.):
        n.inputs[key].default_value=value
        near(n.inputs[key].default_value,[max(0.,x) for x in value] if isinstance(value,list) and len(value)==4 else value)
    n.inputs[key].default_value=default
n.inputs['Transmission Weight'].default_value=.75
n.inputs['IOR'].default_value=1.33
n.inputs['Roughness'].default_value=.2
n.inputs['Base Color'].default_value=(.2,.4,.6,1)
bpy.ops.mesh.primitive_cube_add();bpy.context.object.name='GlassCube';bpy.context.object.data.materials.append(m)
# A second material tests the chain independently of transmission export.
m=bpy.data.materials.new('Mapped');m.use_nodes=True
nodes=m.node_tree.nodes;tc=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping')
assert tc.type=='TEX_COORD' and mapping.type=='MAPPING' and mapping.vector_type=='POINT'
assert tc.object is None and not tc.from_instancer
mapping.vector_type='POINT'
for key,default in [('Location',[0.,0.,0.]),('Rotation',[0.,0.,0.]),('Scale',[1.,1.,1.])]:
    near(mapping.inputs[key].default_value,default)
    mapping.inputs[key].default_value=default
tex=nodes.new('ShaderNodeTexImage');assert tex.projection=='FLAT' and tex.interpolation=='Linear'
tex.projection='FLAT';tex.interpolation='Linear'
im=bpy.data.images.new('MappedColor',width=2,height=2);im.pixels=(1,0,0,1,0,1,0,1,0,0,1,1,1,1,1,1);tex.image=im
links=m.node_tree.links
links.new(tc.outputs['UV'],mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color'])
bpy.ops.mesh.primitive_cube_add(location=(3,0,0));bpy.context.object.name='MappedCube';bpy.context.object.data.materials.append(m)
