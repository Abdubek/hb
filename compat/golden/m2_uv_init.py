"""First-layer UV initialization and active-layer copying, referenced before fix."""
HB_SYMBOLS={
'bpy.types.Mesh.uv_layers.new':'new(name="UVMap", do_init=True); initialize triangle/quad/ngon UVs, copy the active layer when present, or zero-fill with do_init=False',
}
import bpy,math
for n in (3,4,5,6,7,16):
    mesh=bpy.data.meshes.new('UV '+str(n))
    mesh.from_pydata([(math.cos(i*2*math.pi/n),math.sin(i*2*math.pi/n),0) for i in range(n)],[],[list(range(n))])
    obj=bpy.data.objects.new('UV '+str(n),mesh);bpy.context.collection.objects.link(obj)
    first=mesh.uv_layers.new()
    assert len(first.data)==n
    initial=[tuple(v.uv) for v in first.data]
    copied=mesh.uv_layers.new(name='Copy')
    assert initial==[tuple(v.uv) for v in copied.data]
    blank=mesh.uv_layers.new(name='Blank',do_init=False)
    assert all(tuple(x.uv)==(0,0) for x in blank.data)
    mesh.uv_layers.active=blank
    copied_blank=mesh.uv_layers.new(name='Blank copy')
    assert all(tuple(x.uv)==(0,0) for x in copied_blank.data)
    mesh.uv_layers.active=mesh.uv_layers[0]
