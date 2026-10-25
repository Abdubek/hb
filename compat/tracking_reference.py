from mathutils import Vector,Quaternion,Euler,Matrix
import json,sys
out=[]
for d in ((1,2,3),(0,0,1),(0,0,-1),(0,1,0),(0,-1,0),(1,0,0),(-1,0,0),(0,0,0)):
 for track in ('X','Y','Z','-X','-Y','-Z'):
  for up in ('X','Y','Z'):
   if track[-1]==up:continue
   q=Vector(d).to_track_quat(track,up)
   out.append(dict(d=d,track=track,up=up,q=list(q),matrix=[list(row) for row in q.to_matrix()],euler=list(q.to_euler())))
open(sys.argv[sys.argv.index('--')+1],'w').write(json.dumps(out))
