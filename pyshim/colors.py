"""Float32 RGB/HSV arithmetic and factory linear color-space conversions."""
class Color(_RotationValues):
    _path='mathutils.Color'
    def __init__(self,seq=(0.,0.,0.)):
        self._frozen=False;values=list(seq)
        if len(values)!=3:raise ValueError('Color requires three RGB values')
        self._write_values(values)
    def _write_values(self,values):
        if self._frozen:raise TypeError('Color is frozen')
        self._values=[f32(v) for v in values]
    r=_component(0);g=_component(1);b=_component(2)
    def copy(self):return Color(self)
    @property
    def is_frozen(self):return self._frozen
    @property
    def is_valid(self):return True
    @property
    def is_wrapped(self):return False
    @property
    def owner(self):return None
    def freeze(self):self._frozen=True;return self
    def __hash__(self):
        if not self._frozen:raise TypeError('Freeze a Color before hashing it')
        return hash(tuple(self))
    def __add__(self,other):
        if not isinstance(other,Color):raise TypeError('Color addition requires Color')
        return Color([a+b for a,b in zip(self,other)])
    def __sub__(self,other):
        if not isinstance(other,Color):raise TypeError('Color subtraction requires Color')
        return Color([a-b for a,b in zip(self,other)])
    def __mul__(self,other):
        if not isinstance(other,(int,float)):raise TypeError('Color multiplication requires a scalar')
        value=f32(other);return Color([a*value for a in self])
    __rmul__=__mul__
    def __truediv__(self,other):
        if not isinstance(other,(int,float)):raise TypeError('Color division requires a scalar')
        value=f32(other)
        if value==0:raise ZeroDivisionError('Color division by zero')
        return self*f32(1/value)
    def __neg__(self):return Color([-v for v in self])
    def __iadd__(self,other):self._write_values(self+other);return self
    def __isub__(self,other):self._write_values(self-other);return self
    def __imul__(self,other):self._write_values(self*other);return self
    def __itruediv__(self,other):self._write_values(self/other);return self
    @property
    def hsv(self):
        r,g,b=self;k=0.
        if g<b:g,b=b,g;k=-1.
        if r<g:r,g=g,r;k=f32(f32(-2/6)-k)
        chroma=f32(r-min(g,b))
        h=abs(f32(k+f32(f32(g-b)/f32(f32(6*chroma)+1e-20))))
        s=f32(chroma/f32(r+1e-20))
        return (h,s,r)
    def _set_hsv(self,values,clamp=True):
        values=list(values)
        if len(values)!=3:raise ValueError('HSV requires three values')
        h,s,v=[f32(max(0,min(1,x)) if clamp else x) for x in values]
        sector=f32(h*6);index=int(sector);fraction=f32(sector-index)
        p=f32(v*f32(1-s));q=f32(v*f32(1-f32(s*fraction)));t=f32(v*f32(1-f32(s*f32(1-fraction))))
        self._write_values(((v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q))[index%6])
    @hsv.setter
    def hsv(self,values):self._set_hsv(values)
    def _set_hsv_component(self,index,value):
        values=list(self.hsv);values[index]=f32(max(0,min(1,value)));self._set_hsv(values,False)
    h=property(lambda self:self.hsv[0],lambda self,v:self._set_hsv_component(0,v))
    s=property(lambda self:self.hsv[1],lambda self,v:self._set_hsv_component(1,v))
    v=property(lambda self:self.hsv[2],lambda self,v:self._set_hsv_component(2,v))
    def _convert(self,name):
        rows=_COLOR_MATRICES[name]
        return Color([f32(f32(f32(row[0]*self.r)+f32(row[1]*self.g))+f32(row[2]*self.b)) for row in rows])
    def from_srgb_to_scene_linear(self):
        decoded=Color([max(0,v)/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in self])
        return decoded._convert('from_rec709_linear_to_scene_linear')
    def from_scene_linear_to_srgb(self):
        linear=self._convert('from_scene_linear_to_rec709_linear')
        return Color([f32(f32(12.92)*max(0,v)) if v<f32(.0031308) else f32(f32(f32(1.055)*_color_gamma_power(v))-f32(.055)) for v in linear])

# Matrices are externally measured numerical coefficients. Regeneration is in
# compat/color_space_reference.py; no Blender or OpenColorIO implementation is embedded.
_COLOR_MATRICES={'from_aces_to_scene_linear': [[2.5212719440460205, -1.1339447498321533, -0.3874915540218353], [-0.27648672461509705, 1.3727529048919678, -0.09624151885509491], [-0.015381762757897377, -0.15301211178302765, 1.168634295463562]], 'from_rec709_linear_to_scene_linear': [[0.9999945759773254, -1.098955976885918e-06, -6.556470566465578e-07], [-6.257297258116523e-08, 1.0000011920928955, -3.7997997992533783e-07], [1.862633425275817e-08, 2.235176452813903e-07, 0.9999998807907104]], 'from_scene_linear_to_aces': [[0.4397051930427551, 0.38297927379608154, 0.1773356795310974], [0.0897911861538887, 0.8134193420410156, 0.09676084667444229], [0.017544051632285118, 0.11154379695653915, 0.8707029223442078]], 'from_scene_linear_to_rec709_linear': [[1.0000054836273193, 1.0989606380462646e-06, 6.556510925292969e-07], [6.257323548197746e-08, 0.9999988675117493, 3.7997961044311523e-07], [-1.862645149230957e-08, -2.2351741790771484e-07, 1.0000001192092896]], 'from_scene_linear_to_xyz_d65': [[0.4124586880207062, 0.35757604241371155, 0.18043790757656097], [0.21267405152320862, 0.7151515483856201, 0.07217541337013245], [0.01933400146663189, 0.11919168382883072, 0.9503042101860046]], 'from_xyz_d65_to_scene_linear': [[3.2404377460479736, -1.5371320247650146, -0.49852949380874634], [-0.9692674875259399, 1.8760133981704712, 0.041555702686309814], [0.055643230676651, -0.2040254920721054, 1.057225227355957]]}
def _color_linear_method(name):
    def convert(self):return self._convert(name)
    return convert
for _color_method in _COLOR_MATRICES:setattr(Color,_color_method,_color_linear_method(_color_method))
sys.modules['mathutils'].__dict__.update(Color=Color)

def _color_gamma_power(value):
    # A quantized 2/3-power seed and a balanced power mean approximate x^(5/12).
    # This mathematical approximation reproduces the reference's fast transfer
    # curve; exact pow(x, 5/12) differs by up to 0.00027 on ordinary HDR inputs.
    # Coefficients are numerical data; no Blender implementation is bundled.
    if not 0 < value <= 1e10:raise UnsupportedError('mathutils.Color.from_scene_linear_to_srgb','Use finite linear components no greater than 1e10.')
    scale=f32(math.ldexp(math.sqrt(.5),63))
    bits=struct.unpack('I',struct.pack('f',f32(value*scale)))[0]
    seed_bits=round(f32(f32(bits)*f32(2/3)))
    seed=struct.unpack('f',struct.pack('I',seed_bits))[0]
    over=f32(value*seed)
    under=f32(f32(value*value)*f32(1/math.sqrt(seed)))
    coefficient=f32(f32(1/f32(3*f32(2**(-2/3))))*f32(.999852))
    mean=f32(coefficient*f32(over+under))
    return f32(math.sqrt(f32(math.sqrt(mean))))
