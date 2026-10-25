"""Measure cuboid corner interpolation using external Blender 4.5 LTS.

FACE integer labels identify inherited faces. CORNER float labels reveal the
original interpolation face and position without changing UV connectivity.
Each coordinate is independently classified as original corner (0), width
inset (1), or evaluated vertex coordinate (2). These are measured coefficients,
not Blender source code. Run after bevel_stencils.py, with -- output.json.
"""
import bpy
import json
import sys
from pathlib import Path

geometry=json.loads(Path(__file__).resolve().parents[1].joinpath('core/src/bevel_stencils.json').read_text())['stencils']
tables={}
for mode in ('default','islands'):
    for narrow,width in ((False,.25),(True,.005)):
        rows=[]
        for segments in range(1,9):
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.mesh.primitive_cube_add()
            obj=bpy.context.object;mesh=obj.data
            mesh.attributes.new('hb_face','INT','FACE')
            for polygon in mesh.polygons:
                mesh.attributes['hb_face'].data[polygon.index].value=polygon.index
                if mode=='islands':
                    for j,li in enumerate(polygon.loop_indices):
                        mesh.uv_layers.active.data[li].uv=(polygon.index*3+(j in (1,2)),j in (2,3))
            mesh.attributes.new('hb_source','FLOAT','CORNER')
            for axis in 'xyz':mesh.attributes.new('hb_'+axis,'FLOAT','CORNER')
            for polygon in mesh.polygons:
                for li in polygon.loop_indices:
                    mesh.attributes['hb_source'].data[li].value=polygon.index
                    for i,axis in enumerate('xyz'):
                        mesh.attributes['hb_'+axis].data[li].value=mesh.vertices[mesh.loops[li].vertex_index].co[i]
            mod=obj.modifiers.new('Bevel','BEVEL');mod.width=width;mod.segments=segments
            bpy.ops.object.modifier_apply(modifier=mod.name)
            stencil=geometry[segments-1]
            assert [list(p.vertices) for p in mesh.polygons]==stencil['faces']
            encoded=[]
            for loop in mesh.loops:
                v=stencil['vertices'][loop.vertex_index]
                codes=[]
                for axis,name in enumerate('xyz'):
                    pos=mesh.attributes['hb_'+name].data[loop.index].value
                    assert int(pos>0)==v[axis]
                    inset=(1-abs(pos))/width
                    choices=(0,1,v[axis+3])
                    code=min(range(3),key=lambda i:abs(choices[i]-inset))
                    assert abs(choices[code]-inset)<1e-4
                    codes.append(code)
                source=mesh.attributes['hb_source'].data[loop.index].value
                assert abs(source-round(source))<1e-5
                encoded.append(round(source)+6*(codes[0]+3*codes[1]+9*codes[2]))
            rows.append(dict(owners=[mesh.attributes['hb_face'].data[p.index].value for p in mesh.polygons],loops=encoded))
        tables[mode+('_narrow' if narrow else '')]=rows
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(dict(reference='Blender 4.5.9 LTS; measured cuboid interpolation labels; no Blender source code',tables=tables),separators=(',',':'))+'\n')
