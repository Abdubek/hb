import bpy
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_1.0_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_1.0_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-9.999999747378752e-05, -9.999999747378752e-05, -9.999999747378752e-05], [-9.999999747378752e-05, -9.999999747378752e-05, 9.999999747378752e-05], [-9.999999747378752e-05, 9.999999747378752e-05, -9.999999747378752e-05], [-9.999999747378752e-05, 9.999999747378752e-05, 9.999999747378752e-05], [9.999999747378752e-05, -9.999999747378752e-05, -9.999999747378752e-05], [9.999999747378752e-05, -9.999999747378752e-05, 9.999999747378752e-05], [9.999999747378752e-05, 9.999999747378752e-05, -9.999999747378752e-05], [9.999999747378752e-05, 9.999999747378752e-05, 9.999999747378752e-05]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_0.0001_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-9.999999747378752e-05, -9.999999747378752e-05, -9.999999747378752e-05], [-9.999999747378752e-05, -9.999999747378752e-05, 9.999999747378752e-05], [-9.999999747378752e-05, 9.999999747378752e-05, -9.999999747378752e-05], [-9.999999747378752e-05, 9.999999747378752e-05, 9.999999747378752e-05], [9.999999747378752e-05, -9.999999747378752e-05, -9.999999747378752e-05], [9.999999747378752e-05, -9.999999747378752e-05, 9.999999747378752e-05], [9.999999747378752e-05, 9.999999747378752e-05, -9.999999747378752e-05], [9.999999747378752e-05, 9.999999747378752e-05, 9.999999747378752e-05]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_0.0001_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-9.999999974752427e-07, -9.999999974752427e-07, -9.999999974752427e-07], [-9.999999974752427e-07, -9.999999974752427e-07, 9.999999974752427e-07], [-9.999999974752427e-07, 9.999999974752427e-07, -9.999999974752427e-07], [-9.999999974752427e-07, 9.999999974752427e-07, 9.999999974752427e-07], [9.999999974752427e-07, -9.999999974752427e-07, -9.999999974752427e-07], [9.999999974752427e-07, -9.999999974752427e-07, 9.999999974752427e-07], [9.999999974752427e-07, 9.999999974752427e-07, -9.999999974752427e-07], [9.999999974752427e-07, 9.999999974752427e-07, 9.999999974752427e-07]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_1e-06_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[-9.999999974752427e-07, -9.999999974752427e-07, -9.999999974752427e-07], [-9.999999974752427e-07, -9.999999974752427e-07, 9.999999974752427e-07], [-9.999999974752427e-07, 9.999999974752427e-07, -9.999999974752427e-07], [-9.999999974752427e-07, 9.999999974752427e-07, 9.999999974752427e-07], [9.999999974752427e-07, -9.999999974752427e-07, -9.999999974752427e-07], [9.999999974752427e-07, -9.999999974752427e-07, 9.999999974752427e-07], [9.999999974752427e-07, 9.999999974752427e-07, -9.999999974752427e-07], [9.999999974752427e-07, 9.999999974752427e-07, 9.999999974752427e-07]],[],[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]])
o=bpy.data.objects.new('cube_1e-06_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_1.0_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_1.0_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999747378752e-05, 0.0, 0.0], [0.0, 9.999999747378752e-05, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_0.0001_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999747378752e-05, 0.0, 0.0], [0.0, 9.999999747378752e-05, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_0.0001_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999974752427e-07, 0.0, 0.0], [0.0, 9.999999974752427e-07, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_1e-06_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999974752427e-07, 0.0, 0.0], [0.0, 9.999999974752427e-07, 0.0]],[],[[0, 1, 2], [2, 1, 0]])
o=bpy.data.objects.new('opposed_1e-06_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_1.0_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_1.0_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999747378752e-05, 0.0, 0.0], [0.00019999999494757503, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_0.0001_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999747378752e-05, 0.0, 0.0], [0.00019999999494757503, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_0.0001_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999974752427e-07, 0.0, 0.0], [1.9999999949504854e-06, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_1e-06_False',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=False;bpy.ops.object.modifier_apply(modifier=w.name)
m=bpy.data.meshes.new('Mesh');m.from_pydata([[0.0, 0.0, 0.0], [9.999999974752427e-07, 0.0, 0.0], [1.9999999949504854e-06, 0.0, 0.0]],[],[[0, 1, 2]])
o=bpy.data.objects.new('collinear_1e-06_True',m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
w=o.modifiers.new('Weight','WEIGHTED_NORMAL');w.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=w.name)
