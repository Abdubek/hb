import bpy
HB_EQUIVALENT_MESH_PREFIXES=('Exact','Fast','Collection','Reflected')
for label,solver,collection,reflect in [('Exact','EXACT',False,False),('Fast','FAST',False,False),('Collection','EXACT',True,False),('Reflected','EXACT',False,True)]:
    bpy.ops.mesh.primitive_cube_add();owner=bpy.context.object;owner.name=label;owner.data.name=label
    owner.data.normals_split_custom_set([(0,.2,1)]*24)
    color=owner.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    assert color.name=='Color' and color.domain=='CORNER' and color.data_type=='FLOAT_COLOR'
    for i,entry in enumerate(color.data):entry.color=(i/24,.2,.4,1)
    assert len(owner.data.color_attributes)==1 and len(owner.data.color_attributes['Color'].data)==24
    assert owner.data.color_attributes.get('Color').name=='Color'
    operands=bpy.data.collections.new(label+' cutters');bpy.context.scene.collection.children.link(operands)
    for x in (-.6,.6):
        bpy.ops.mesh.primitive_cube_add(size=.6,location=(x,0,0));cutter=bpy.context.object
        if reflect:cutter.scale.x=-1
        operands.objects.link(cutter)
    bpy.context.view_layer.objects.active=owner
    modifier=owner.modifiers.new('Boolean','BOOLEAN');modifier.solver=solver
    modifier.operation='DIFFERENCE'
    if collection:
        modifier.operand_type='COLLECTION';modifier.collection=operands
        assert modifier.collection.name==operands.name
    else:modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
