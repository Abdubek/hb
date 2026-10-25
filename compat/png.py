"""Small PNG reader used only by tests (8-bit RGB/RGBA, non-interlaced)."""
import struct,zlib

def rgba(data):
    width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',data[16:29])
    assert depth==8 and color in (2,6) and interlace==0
    channels=4 if color==6 else 3;at=8;compressed=b''
    while at<len(data):
        size=struct.unpack_from('>I',data,at)[0];kind=data[at+4:at+8]
        if kind==b'IDAT':compressed+=data[at+8:at+8+size]
        at+=size+12
    raw=zlib.decompress(compressed);stride=width*channels;previous=bytearray(stride);pixels=[];at=0
    for _ in range(height):
        kind=raw[at];at+=1;row=bytearray(raw[at:at+stride]);at+=stride
        for x in range(stride):
            a=row[x-channels] if x>=channels else 0;b=previous[x];c=previous[x-channels] if x>=channels else 0
            if kind==1:v=a
            elif kind==2:v=b
            elif kind==3:v=(a+b)//2
            elif kind==4:
                p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c);v=a if pa<=pb and pa<=pc else b if pb<=pc else c
            else:v=0
            row[x]=(row[x]+v)%256
        pixels.append([list(row[x:x+channels])+([] if channels==4 else [255]) for x in range(0,stride,channels)]);previous=row
    return width,height,pixels
