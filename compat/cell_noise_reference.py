"""Regenerate the deterministic texture fixture using Blender 4.5 LTS."""
import bpy,random,json,sys
r=random.Random(20260908);t=bpy.data.textures.new('Noise',type='CLOUDS');t.noise_basis='CELL_NOISE';rows=[]
for i in range(1000):
    t.noise_depth=r.randrange(0,7);t.noise_scale=r.uniform(.001,3);t.noise_type=r.choice(['SOFT_NOISE','HARD_NOISE']);t.intensity=r.uniform(0,2);t.contrast=r.uniform(0,5)
    p=[r.uniform(-100,100) for _ in range(3)]
    rows.append({'position':p,'depth':t.noise_depth,'scale':t.noise_scale,'hard':t.noise_type=='HARD_NOISE','intensity':t.intensity,'contrast':t.contrast,'value':list(t.evaluate(p))[3]})
open(sys.argv[sys.argv.index('--')+1],'w').write(json.dumps(rows))
