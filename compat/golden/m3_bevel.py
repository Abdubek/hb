"""Canonical vertex bevel and overlap clamping, from captured Blender probes."""
import bpy
for affect in ('EDGES','VERTICES'):
    for segments in range(1,9):
        bpy.ops.mesh.primitive_cube_add(calc_uvs=not (affect=='VERTICES' and segments in (3,5,7)))
        obj=bpy.context.object;obj.name=f'Bevel {affect} {segments}'
        for vertex in obj.data.vertices:vertex.co.y*=2;vertex.co.z*=3
        modifier=obj.modifiers.new('Bevel','BEVEL');modifier.affect=affect
        modifier.segments=segments;modifier.width=3 if segments==1 else .15
        bpy.ops.object.modifier_apply(modifier=modifier.name)
