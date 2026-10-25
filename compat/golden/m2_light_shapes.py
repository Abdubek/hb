import bpy
HB_SYMBOLS={
'bpy.types.Light.shape':'AREA emitter shape: SQUARE, RECTANGLE, DISK or ELLIPSE',
'bpy.types.Light.size_y':'Secondary AREA emitter extent',
'bpy.types.Light.use_shadow':'Enable or disable shadow casting',
}
for shape in ('SQUARE','RECTANGLE','DISK','ELLIPSE'):
    bpy.ops.object.light_add(type='AREA',radius=2,location=(1,2,3))
    d=bpy.context.object.data;d.name=shape
    assert d.shape=='SQUARE' and d.size_y==2 and d.use_shadow
    d.shape=shape;d.size_y=3;d.use_shadow=False
    assert d.shape==shape and d.size_y==3 and not d.use_shadow
for kind in ('POINT','SUN','SPOT'):
    d=bpy.data.lights.new(kind,kind);assert d.use_shadow;d.use_shadow=False
