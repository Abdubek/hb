"""Standalone Color arithmetic, HSV, freezing and factory color-space transforms."""
HB_SYMBOLS={
'mathutils.Color':'Float32 RGB sequence with Color arithmetic and scalar multiply/divide; default black',
'mathutils.Color.r':'Mutable red channel',
'mathutils.Color.g':'Mutable green channel',
'mathutils.Color.b':'Mutable blue channel',
'mathutils.Color.h':'HSV hue; assignments clamp to 0..1',
'mathutils.Color.s':'HSV saturation; assignments clamp to 0..1',
'mathutils.Color.v':'HSV value; assignments clamp to 0..1',
'mathutils.Color.hsv':'HSV tuple; assignments clamp all three components to 0..1',
'mathutils.Color.copy':'Independent mutable copy',
'mathutils.Color.freeze':'Freeze an unwrapped Color and return itself',
'mathutils.Color.is_frozen':'Read-only immutability flag',
'mathutils.Color.is_valid':'Read-only validity flag',
'mathutils.Color.is_wrapped':'Read-only ownership flag',
'mathutils.Color.owner':'Owning RNA value or None for standalone colors',
'mathutils.Color.from_aces_to_scene_linear':'ACES AP0 to factory scene-linear RGB',
'mathutils.Color.from_scene_linear_to_aces':'Factory scene-linear RGB to ACES AP0',
'mathutils.Color.from_rec709_linear_to_scene_linear':'Linear Rec.709 to factory scene-linear RGB',
'mathutils.Color.from_scene_linear_to_rec709_linear':'Factory scene-linear RGB to linear Rec.709',
'mathutils.Color.from_xyz_d65_to_scene_linear':'CIE XYZ D65 to factory scene-linear RGB',
'mathutils.Color.from_scene_linear_to_xyz_d65':'Factory scene-linear RGB to CIE XYZ D65',
'mathutils.Color.from_srgb_to_scene_linear':'sRGB transfer decoding plus factory scene-linear matrix',
'mathutils.Color.from_scene_linear_to_srgb':'Factory scene-linear matrix plus measured fast sRGB transfer behavior; positive linear components up to 1e10',
}
from mathutils import Color
assert tuple(Color())==(0,0,0)
a=Color((.25,.5,.75));b=a.copy();b.r=.5;b[1:]=(.25,1)
assert tuple(a)==(.25,.5,.75) and tuple(b)==(.5,.25,1)
assert tuple(a+b)==(.75,.75,1.75) and tuple(a-b)==(-.25,.25,-.25)
assert tuple(2*a)==(.5,1,1.5) and tuple(a/2)==(.125,.25,.375)
c=a.copy();c+=b;c-=b;c*=2;c/=2;assert c==a
assert tuple(-a)==(-.25,-.5,-.75)
c.hsv=(.3,.7,.8);assert max(abs(x-y) for x,y in zip(c,(.352,.8,.24)))<1e-6
c.h=.4;c.s=.5;c.v=.9;assert max(abs(x-y) for x,y in zip(c.hsv,(.4,.5,.9)))<1e-6
assert c.is_valid and not c.is_wrapped and c.owner is None and not c.is_frozen
assert c.freeze() is c and c.is_frozen and not c.copy().is_frozen
try:c.r=0
except TypeError:pass
else:raise AssertionError('Frozen Color mutation must fail')
assert hash(c)==hash(c.copy().freeze())
for converted in (a.from_aces_to_scene_linear(), a.from_scene_linear_to_aces(), a.from_rec709_linear_to_scene_linear(), a.from_scene_linear_to_rec709_linear(), a.from_xyz_d65_to_scene_linear(), a.from_scene_linear_to_xyz_d65(), a.from_srgb_to_scene_linear(), a.from_scene_linear_to_srgb()):
    assert isinstance(converted,Color) and len(converted)==3 and tuple(a)==(.25,.5,.75)
