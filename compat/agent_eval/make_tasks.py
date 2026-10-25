"""Freeze simple, objectively checkable assembly tasks before evaluation.

These tasks are a preview-workflow benchmark, not the original unrestricted
visual-modeling benchmark. Required names are published to the model; checks are
not secret. Recognition and aesthetic quality require separate human review.
"""
import json
from pathlib import Path
rows=[
('handheld','A handheld game console standing upright, with a screen and controls','Body,Screen,Dpad,Button A,Button B'),
('rover','A six-wheel exploration rover, with three wheels on each side','Chassis,Wheel L1,Wheel L2,Wheel L3,Wheel R1,Wheel R2,Wheel R3,Mast'),
('room','A furnished room with a floor exactly 4 by 5 meters in XY, two walls, a desk and a chair','Floor,Wall X,Wall Y,Desk,Chair'),
('bench','A park bench with seat, back and four legs','Seat,Back,Leg 1,Leg 2,Leg 3,Leg 4'),
('lamp','A desk lamp with a base, upright stem and shade','Base,Stem,Shade'),
('shelf','An open bookcase with two vertical sides and three shelves','Side L,Side R,Shelf 1,Shelf 2,Shelf 3'),
('camera','A compact photographic camera with body, lens and shutter button','Body,Lens,Shutter'),
('speaker','A two-driver speaker cabinet with round drivers on the front','Cabinet,Woofer,Tweeter'),
('monitor','A desktop monitor with screen, stem and base','Housing,Screen,Stem,Base'),
('stool','A round-seat stool with three legs','Seat,Leg 1,Leg 2,Leg 3'),
('bridge','A short pedestrian bridge with a deck, two piers and railings','Deck,Pier 1,Pier 2,Rail L,Rail R'),
('kiosk','A freestanding information kiosk with screen, body and base','Body,Screen,Base'),
('cabinet','A two-door cabinet with two handles and a top','Body,Door L,Door R,Handle L,Handle R,Top'),
('table','A rectangular dining table with a top and four distinct legs','Top,Leg 1,Leg 2,Leg 3,Leg 4'),
('chess','A chess-inspired geometric rook beside a pawn on a board','Board,Rook Base,Rook Tower,Rook Crown,Pawn Base,Pawn Stem,Pawn Head'),
('crate','An open-top shipping crate with a bottom and four separate sides','Bottom,Side N,Side S,Side E,Side W'),
('bottle','A reusable water bottle with cylindrical body, shoulder, neck and cap','Body,Shoulder,Neck,Cap'),
('robot','A friendly rigid toy robot with boxy torso, head, arms and feet','Torso,Head,Arm L,Arm R,Foot L,Foot R'),
('bus','A toy bus with body, roof, front window and four wheels','Body,Roof,Window,Wheel FL,Wheel FR,Wheel BL,Wheel BR'),
('stairs','An architectural staircase of five progressively taller blocks','Step 1,Step 2,Step 3,Step 4,Step 5'),
('pavilion','A small pavilion with four columns and a roof','Column 1,Column 2,Column 3,Column 4,Roof'),
('bed','A single bed with frame, mattress, pillow and headboard','Frame,Mattress,Pillow,Headboard'),
('sofa','A two-seat sofa with base, back, arms and cushions','Base,Back,Arm L,Arm R,Cushion L,Cushion R'),
('pedestal','A three-level exhibition pedestal with a displayed sphere','Lower,Middle,Upper,Exhibit'),
('fence','A three-post fence with two horizontal rails','Post 1,Post 2,Post 3,Rail Lower,Rail Upper'),
('turntable','A record player with a plinth, circular platter and tonearm','Plinth,Platter,Tonearm'),
('luggage','An upright suitcase with handle and two wheels','Body,Handle,Wheel L,Wheel R'),
('arch','A simple block archway with two uprights and a lintel','Upright L,Upright R,Lintel'),
('workbench','A workshop bench with top, lower shelf, four legs and vise','Top,Shelf,Leg 1,Leg 2,Leg 3,Leg 4,Vise'),
('booth','A trade-show booth with floor, back wall, counter and sign panel','Floor,Back Wall,Counter,Sign'),
]
tasks=[]
for i,(slug,description,names) in enumerate(rows,1):
    tasks.append({'id':f'{i:02}-{slug}','description':description,'required_meshes':names.split(','),'minimum_materials':2,'camera':'Camera','special':{'floor_xy':[4,5]} if slug=='room' else {}})
Path(__file__).with_name('tasks.json').write_text(json.dumps(tasks,indent=2)+'\n')
