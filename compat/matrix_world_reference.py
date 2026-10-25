import bpy,json,itertools
from mathutils import Matrix,Euler,Vector
from pathlib import Path
out={}
def snap(o):
 bpy.context.view_layer.update()
 return dict(location=list(o.location),rotation_euler=list(o.rotation_euler),rotation_quaternion=list(o.rotation_quaternion),scale=list(o.scale),world=[list(r) for r in o.matrix_world])
for index,(parent_kind,mode,shape) in enumerate(itertools.product(('none','uniform','nonuniform','reflected'),('XYZ','XZY','YXZ','YZX','ZXY','ZYX','QUATERNION'),('regular','reflected','shear','zero'))):
 bpy.ops.object.select_all(action='DESELECT')
 p=None
 if parent_kind!='none':
  p=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(p);p.location=(2,-1,3);p.rotation_euler=(.2,-.4,.7);p.scale={'uniform':(2,2,2),'nonuniform':(1.2,.7,2),'reflected':(-1,2,1)}[parent_kind]
 o=bpy.data.objects.new('Object',None);bpy.context.collection.objects.link(o);o.rotation_mode=mode;o.location=(1,2,3);o.rotation_euler=(.2,.3,.4);o.rotation_quaternion=(.9,.1,.2,.3);o.scale=(1.1,.8,1.3)
 if p:
  o.select_set(True);p.select_set(True);bpy.context.view_layer.objects.active=p;bpy.ops.object.parent_set(type='OBJECT',keep_transform=False)
  p.location.x+=1.7;p.rotation_euler.y+=.25
 target=Matrix.Translation((3,-2,5)) @ Euler((.4,-.6,.9),'YZX').to_matrix().to_4x4() @ Matrix.Diagonal((-.6 if shape=='reflected' else 0 if shape=='zero' else .6,1.4,2,1))
 if shape=='shear':target[0][1]+=.3;target[1][2]-=.2
 before=snap(o);basis=(p.matrix_world @ o.matrix_parent_inverse).inverted() @ target if p else target.copy();parts=basis.decompose();o.matrix_world=target;after=snap(o)
 out[str(index)]=dict(parent_kind=parent_kind,mode=mode,shape=shape,before=before,target=[list(r) for r in target],basis=[list(r) for r in basis],decomposed=[list(v) for v in parts],after=after)
 bpy.data.objects.remove(o,do_unlink=True)
 if p:bpy.data.objects.remove(p,do_unlink=True)
Path('/results/reference.json').write_text(json.dumps(out,indent=2)+'\n')
