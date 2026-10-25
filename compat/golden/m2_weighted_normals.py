"""Weighted-normal contracts, executed with Blender before exposing the API."""
HB_SYMBOLS={
'bpy.types.WeightedNormalModifier.name':'Modifier name',
'bpy.types.WeightedNormalModifier.type':'WEIGHTED_NORMAL',
'bpy.types.WeightedNormalModifier.mode':'FACE_AREA, CORNER_ANGLE or FACE_AREA_WITH_ANGLE',
'bpy.types.WeightedNormalModifier.keep_sharp':'Keep separate smooth fans at flat/smooth and nonmanifold boundaries',
'bpy.types.WeightedNormalModifier.show_viewport':'Viewport and glTF modifier visibility',
'bpy.types.WeightedNormalModifier.show_render':'Preview modifier visibility',
}
import bpy

def weighted(obj,mode,keep):
    mod=obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    assert mod.type=='WEIGHTED_NORMAL' and mod.mode=='FACE_AREA' and mod.weight==50
    assert abs(mod.thresh-.01)<1e-6 and not mod.keep_sharp and not mod.use_face_influence
    assert mod.vertex_group=='' and not mod.invert_vertex_group
    mod.mode=mode;mod.weight=50;mod.thresh=.01;mod.keep_sharp=keep
    mod.use_face_influence=False;mod.vertex_group='';mod.invert_vertex_group=False
    mod.show_viewport=False;mod.show_viewport=True;mod.show_render=False;mod.show_render=True
    bpy.ops.object.modifier_apply(modifier=mod.name)

for uv in (False,True):
    for smooth in (False,True):
        for keep in (False,True):
            for segments in (0,1,3,4):
                bpy.ops.mesh.primitive_cube_add(calc_uvs=uv)
                obj=bpy.context.object;obj.scale=(3,2,1)
                bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
                if smooth:bpy.ops.object.shade_smooth()
                if segments:
                    mod=obj.modifiers.new('Rounded','BEVEL');mod.width=.1;mod.segments=segments
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                weighted(obj,'FACE_AREA',keep)

for mode in ('FACE_AREA','CORNER_ANGLE','FACE_AREA_WITH_ANGLE'):
    for keep in (False,True):
        for smooth in ('flat','smooth','mixed'):
            mesh=bpy.data.meshes.new('Asymmetric tetrahedron')
            mesh.from_pydata([(0,0,0),(3,0,0),(0,2,0),(0,0,1)],[],[(0,2,1),(0,1,3),(0,3,2),(1,2,3)])
            obj=bpy.data.objects.new('Weighted tetrahedron',mesh);bpy.context.collection.objects.link(obj)
            bpy.context.view_layer.objects.active=obj
            for face in mesh.polygons:face.use_smooth=smooth=='smooth' or (smooth=='mixed' and face.index!=0)
            weighted(obj,mode,keep)

# Evaluation also works without applying the descriptor.
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object;obj.scale=(1.7,.6,.9)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
obj.modifiers.new('Evaluated','WEIGHTED_NORMAL')
