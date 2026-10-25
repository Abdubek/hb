import bpy,json,itertools,random
from pathlib import Path
orders=('XYZ','XZY','YXZ','YZX','ZXY','ZYX','QUATERNION')
def state(o):
 bpy.context.view_layer.update()
 return dict(mode=o.rotation_mode,euler=list(o.rotation_euler),order=o.rotation_euler.order,quaternion=list(o.rotation_quaternion),matrix=[list(r) for r in o.matrix_world])
out={};rng=random.Random(293)
for index,(before,after) in enumerate(itertools.product(orders,orders)):
 o=bpy.data.objects.new('probe',None);bpy.context.collection.objects.link(o)
 o.rotation_mode=before;o.rotation_euler=[rng.uniform(-2.5,2.5) for _ in range(3)];o.rotation_quaternion=[.7,.2,-.4,.5]
 o.location=(2,-3,4);o.scale=(-.5,1.2,2)
 start=state(o);o.rotation_mode=after
 out[str(index)]=dict(before=start,after=state(o))
 bpy.data.objects.remove(o,do_unlink=True)
o=bpy.data.objects.new('order',None);bpy.context.collection.objects.link(o);o.rotation_euler=(.3,.7,-1.1)
view=o.rotation_euler
for order in orders[:-1]:
 view.order=order
 out['view_'+order]=state(o)
Path('/results/reference.json').write_text(json.dumps(out,indent=2)+'\n')
