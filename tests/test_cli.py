import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'compat'))
from normalize import revision

ROOT=Path(__file__).resolve().parents[1]
HB=Path(os.environ.get('HB_BIN',ROOT/'target/release/hb')).resolve()
class CLI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def hb(self,*args,ok=True):
        r=subprocess.run([str(HB),*map(str,args)],cwd=self.path,capture_output=True,text=True,env={**os.environ,'PYTHONHOME':'/nonexistent','PYTHONPATH':'/nonexistent'})
        self.assertEqual(r.returncode,0 if ok else 1,r.stderr+'\n'+r.stdout)
        return json.loads(r.stdout)
    def script(self,source,name='script.py'):
        p=self.path/name;p.write_text(source);return p
    def test_golden_assertions(self):
        for script in sorted((ROOT/'compat/golden').glob('*.py')):
            self.hb('run',script,'--scene',script.stem+'.hb')
    def test_self_contained_and_print_protocol(self):
        p=self.script("import bpy\nimport math\nprint('hello')\nbpy.ops.mesh.primitive_cube_add(location=(math.sin(0),0,1))")
        r=self.hb('run',p,'--out','scene.glb')
        self.assertEqual(r['objects']['created'],['Cube'])
        self.assertTrue((self.path/'scene.glb').is_file())
    def test_deterministic_and_rollback(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        a=self.hb('run',p,'--scene','a.hb','--out','a.glb')
        b=self.hb('run',p,'--scene','b.hb','--out','b.glb')
        self.assertEqual(a['revision'],b['revision'])
        self.assertEqual((self.path/'a.glb').read_bytes(),(self.path/'b.glb').read_bytes())
        before=(self.path/'a.hb').read_bytes()
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.ops.wm.save_as_mainfile(filepath="x.blend")')
        r=self.hb('run',p,'--scene','a.hb',ok=False)
        self.assertEqual(r['error']['code'],'UNSUPPORTED_API')
        self.assertEqual(r['error']['location'],str(p)+':3')
        self.assertEqual((self.path/'a.hb').read_bytes(),before)
    def test_manifest_and_checker(self):
        p=self.script('import bpy as b\no=b.context.object\no.modifiers.new("X", "SHRINKWRAP")\nb.ops.mesh.primitive_ico_sphere_add()\nb.data.materials.new("M")')
        r=self.hb('check',p,ok=False)
        messages=' '.join(e['message'] for e in r['errors'])
        self.assertIn('SHRINKWRAP',messages);self.assertNotIn('primitive_ico_sphere_add',messages)
        self.assertEqual(self.hb('api','--json'),json.loads((ROOT/'compat/manifest.json').read_text()))
    def test_runtime_unknown_writes(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.context.object.not_supported=3')
        self.assertEqual(self.hb('run',p,ok=False)['error']['code'],'UNSUPPORTED_API')
    def test_dynamic_checker(self):
        p=self.script('import bpy\npath=input()\ngetattr(bpy.ops.mesh,path)()')
        self.assertEqual(self.hb('check',p,ok=False)['errors'][0]['code'],'STATIC_UNRESOLVED')
    def test_syntax_and_system_exit(self):
        p=self.script('if:')
        self.assertEqual(self.hb('check',p,ok=False)['errors'][0]['code'],'SYNTAX_ERROR')
        p=self.script('raise SystemExit(0)')
        self.assertEqual(self.hb('run',p,ok=False)['error']['code'],'SCRIPT_ERROR')
    def test_history_and_tamper(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        a=self.hb('run',p);b=self.hb('run',p)
        self.assertNotEqual(a['revision'],b['revision'])
        self.assertEqual(len(list((self.path/'scene.hb.revisions').glob('*.hbr'))),2)
        scene=revision(self.path/'scene.hb');scene['scene']['objects'][0]['name']='tampered'
        (self.path/'scene.hb').write_text(json.dumps(scene))
        self.assertEqual(self.hb('export','x.glb',ok=False)['error']['code'],'INVALID_SCENE')
    def test_glb_layout(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()')
        self.hb('run',p,'--out','cube.glb')
        data=(self.path/'cube.glb').read_bytes()
        self.assertEqual(struct.unpack_from('<4sII',data), (b'glTF',2,len(data)))
        length,kind=struct.unpack_from('<II',data,12)
        self.assertEqual(kind,0x4e4f534a)
        doc=json.loads(data[20:20+length]);self.assertEqual(doc['asset']['version'],'2.0')
        prim=doc['meshes'][0]['primitives'][0]
        self.assertEqual(doc['accessors'][prim['indices']]['count'],36)
        self.assertEqual(doc['accessors'][prim['attributes']['POSITION']]['min'],[-1,-1,-1])
        self.assertEqual(doc['nodes'][0]['name'],'Cube')
        self.assertEqual(doc['scenes'][0]['nodes'],[0])
    def test_truthful_capabilities(self):
        c=self.hb('capabilities');self.assertIn('render',c['commands'])
        self.assertEqual(c,self.hb('capabilities','--json'))
        self.assertIn('Partial compatibility',c['compatibility'])
        self.assertLess(len(json.dumps(c)),5000)
        self.assertEqual(self.hb('capabilities','--unknown',ok=False)['error']['code'],'USAGE')
        self.assertEqual(self.hb('render',ok=False)['error']['code'],'SCENE_NOT_FOUND')
    def test_hash_order_is_deterministic(self):
        p=self.script('import bpy\nfor name in {"anchor", "wheel", "desk", "panel", "door", "window", "roof", "base"}:\n    bpy.ops.mesh.primitive_cube_add()\n    bpy.context.object.name=name')
        ids=[self.hb('run',p,'--scene',str(i)+'.hb')['revision'] for i in range(3)]
        self.assertEqual(len(set(ids)),1)
    def test_seed_and_notices(self):
        p=self.script('import bpy\nimport random\nbpy.ops.mesh.primitive_cube_add(location=(random.random(),0,0))')
        a=self.hb('run',p,'--seed','12','--scene','a.hb')
        b=self.hb('run',p,'--seed','12','--scene','b.hb')
        c=self.hb('run',p,'--seed','13','--scene','c.hb')
        self.assertEqual(a['revision'],b['revision'])
        self.assertNotEqual(a['revision'],c['revision'])
        self.assertEqual(revision(self.path/'a.hb')['seed'],12)
        self.assertIn('PYTHON',self.hb('licenses')['third_party'])
    def test_nonfinite_transform(self):
        p=self.script('import bpy\nbpy.ops.mesh.primitive_cube_add()\nbpy.context.object.location=(float("nan"),0,0)')
        self.hb('run',p,ok=False)
        self.assertFalse((self.path/'scene.hb').exists())
    def test_snapshot_extension(self):
        p=self.script('import bpy\nimport hb\nbpy.ops.mesh.primitive_cube_add()\nassert hb.snapshot()["objects"][0]["name"] == "Cube"')
        self.hb('run',p)
    def test_deviation_transform_type(self):
        p=self.script('import bpy\nimport hb\nbpy.ops.mesh.primitive_cube_add()\ntry:\n    bpy.context.object.location + (1,2,3)\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError("must reject tuple arithmetic")')
        self.hb('run',p)
if __name__=='__main__':unittest.main()
