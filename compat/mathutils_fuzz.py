"""Independent rotation/matrix differential workload, identical on both runtimes."""
import json,random,math
from mathutils import Matrix,Vector,Quaternion,Euler
random.seed(20260908)
rows=[]
def flat(m):return [v for row in m for v in row]
for index in range(10000):
    order=('XYZ','XZY','YXZ','YZX','ZXY','ZYX')[index%6]
    e=Euler([random.uniform(-3,3) for _ in range(3)],order)
    axis=Vector([random.uniform(-1,1) for _ in range(3)])
    q=Quaternion(axis,random.uniform(-3,3));v=Vector([random.uniform(-2,2) for _ in range(3)])
    transform=Matrix.Translation(v)@q.to_matrix().to_4x4()@Matrix.Diagonal((.7,1.3,2.1,1))
    track=('X','Y','Z','-X','-Y','-Z')[index%6];up=[u for u in 'XYZ' if u!=track[-1]][index%2]
    rows.append([flat(e.to_matrix()),flat(transform.inverted()),flat(axis.to_track_quat(track,up).to_matrix()),list(q@v),list(Quaternion([random.uniform(-2,2) for _ in range(4)]).normalized()),list(q.conjugated()),flat(Matrix.Rotation(.3,3,axis)),flat(transform@Matrix.Translation((.3,.2,.1))),flat(Matrix.Scale(1.7,3,axis)),flat(e.to_matrix().to_euler(order).to_matrix())])
with open('mathutils-fuzz.json','w') as file:json.dump(rows,file,separators=(',',':'))
