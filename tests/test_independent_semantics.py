import copy
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'compat'))
from independent_semantics import compare

class IndependentSemantics(unittest.TestCase):
    def test_corruption_cannot_pass_export_checks(self):
        reference=dict(nodes=[dict(name='Box',mesh=0)],meshes=[dict(primitives=[dict(attributes={'POSITION':0},indices=1,material=0)])],
                       accessors=[dict(count=24,min=[-1,-1,-1],max=[1,1,1]),dict(count=36)],
                       materials=[dict(name='Paint',pbrMetallicRoughness=dict(baseColorFactor=[.2,.3,.4,1]))])
        with tempfile.TemporaryDirectory() as tmp:
            def write(name,doc):
                path=Path(tmp)/name;raw=json.dumps(doc).encode();raw+=b' '*((-len(raw))%4)
                path.write_bytes(b'glTF'+struct.pack('<II',2,len(raw)+20)+struct.pack('<I',len(raw))+b'JSON'+raw)
                return path
            ref=write('reference.glb',reference)
            self.assertTrue(compare(ref,write('copy.glb',reference))['passed'])
            mutations=[]
            changed=copy.deepcopy(reference);changed['nodes'][0]['name']='Wrong';mutations.append(changed)
            changed=copy.deepcopy(reference);changed['nodes'][0]['translation']=[.01,0,0];mutations.append(changed)
            changed=copy.deepcopy(reference);changed['accessors'][1]['count']=33;mutations.append(changed)
            changed=copy.deepcopy(reference);changed['accessors'][0]['max'][2]=.9;mutations.append(changed)
            changed=copy.deepcopy(reference);changed['materials'][0]['pbrMetallicRoughness']['baseColorFactor'][0]=.9;mutations.append(changed)
            changed=copy.deepcopy(reference);del changed['meshes'][0]['primitives'][0]['material'];mutations.append(changed)
            for i,changed in enumerate(mutations):
                with self.subTest(mutation=i):self.assertFalse(compare(ref,write('bad.glb',changed))['passed'])
            defaults=copy.deepcopy(reference);defaults['materials'][0]['pbrMetallicRoughness'].update(metallicFactor=1,roughnessFactor=1)
            defaults['nodes'][0]['matrix']=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
            self.assertTrue(compare(ref,write('defaults.glb',defaults))['passed'])

    def test_camera_metadata_is_not_projection(self):
        doc=dict(nodes=[dict(name='Camera',camera=0)],cameras=[dict(name='Lens',type='perspective',perspective=dict(yfov=.8,znear=.1,zfar=100))])
        from independent_semantics import summary
        metadata=copy.deepcopy(doc);metadata['cameras'][0]['extras']={'hb_sensor_width':36}
        self.assertEqual(summary(doc),summary(metadata))
        changed=copy.deepcopy(metadata);changed['cameras'][0]['perspective']['yfov']=.9
        self.assertNotEqual(summary(doc),summary(changed))
