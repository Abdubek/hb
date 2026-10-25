"""Deterministic Vector differential workload; run unchanged in hb and Blender."""
import json,random,sys,math
from mathutils import Vector
random.seed(20260908)
rows=[]
for index in range(10000):
    n=2+index%3
    a=Vector([random.uniform(-20,20) for _ in range(n)])
    b=Vector([random.uniform(-20,20) for _ in range(n)])
    t=random.uniform(-2,2)
    rows.append([list(a+b),list(a-b),list(a*b),list(a*t),list(a/3.7),a.dot(b),a.length,list(a.normalized()),list(a.lerp(b,t)),list(a.project(b))])
# Exactly 100,000 operations; JSON allows the same script on both runtimes.
with open('vector-fuzz.json','w') as file:json.dump(rows,file,separators=(',',':'))
