"""Deterministic RGB/HSV, arithmetic and color-space differential workload."""
import json,random
from mathutils import Color
rng=random.Random(20260908)
methods=('from_aces_to_scene_linear','from_scene_linear_to_aces','from_rec709_linear_to_scene_linear','from_scene_linear_to_rec709_linear','from_xyz_d65_to_scene_linear','from_scene_linear_to_xyz_d65','from_srgb_to_scene_linear','from_scene_linear_to_srgb')
rows=[]
for index in range(2000):
    c=Color([rng.uniform(-.5,4) for _ in range(3)]);d=Color([rng.uniform(-.5,4) for _ in range(3)])
    scalar=rng.uniform(.01,3);hsv=[rng.uniform(-.5,1.5) for _ in range(3)]
    h,s,v=[c.copy() for _ in range(3)];h.h=hsv[0];s.s=hsv[1];v.v=hsv[2]
    changed=Color();changed.hsv=hsv
    rows.append([list(c.hsv),list(changed),list(h),list(s),list(v),list(c+d),list(c-d),list(c*scalar),list(c/scalar),*[list(getattr(c,name)()) for name in methods]])
with open('color-fuzz.json','w') as f:json.dump(rows,f)
