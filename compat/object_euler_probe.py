import bpy
o=bpy.data.objects.new('0',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[-0.1121046245098114, -1.9289686679840088, 0.002364572836086154];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.1121046245098114, -1.9289686679840088, 0.002364572836086154]))<=1e-5,('0',tuple(o.rotation_euler),[-0.1121046245098114, -1.9289686679840088, 0.002364572836086154])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('0',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('1',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[-0.4451114237308502, -0.29282742738723755, 0.5445345044136047];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.4451114237308502, -0.29282742738723755, 0.5445345044136047]))<=1e-5,('1',tuple(o.rotation_euler),[-0.4451114237308502, -0.29282742738723755, 0.5445345044136047])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('1',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('2',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[1.376304030418396, 1.2226828336715698, -1.4747759103775024];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.376304030418396, 1.2226828336715698, -1.4747759103775024]))<=1e-5,('2',tuple(o.rotation_euler),[1.376304030418396, 1.2226828336715698, -1.4747759103775024])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('2',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('3',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[1.5194419622421265, -1.3979377746582031, -0.0463959164917469];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.5194419622421265, -1.3979377746582031, -0.0463959164917469]))<=1e-5,('3',tuple(o.rotation_euler),[1.5194419622421265, -1.3979377746582031, -0.0463959164917469])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('3',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('4',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[0.6910094022750854, 1.0693879127502441, 0.02594660595059395];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.6910094022750854, 1.0693879127502441, 0.02594660595059395]))<=1e-5,('4',tuple(o.rotation_euler),[0.6910094022750854, 1.0693879127502441, 0.02594660595059395])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('4',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('5',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[-2.278104305267334, 1.3048869371414185, -1.6466654539108276];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-2.278104305267334, 1.3048869371414185, -1.6466654539108276]))<=1e-5,('5',tuple(o.rotation_euler),[-2.278104305267334, 1.3048869371414185, -1.6466654539108276])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('5',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('6',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XYZ';o.rotation_euler=[-0.3512776494026184, -1.168831467628479, -0.8326771259307861];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.3512776494026184, -1.168831467628479, -0.8326771259307861]))<=1e-5,('6',tuple(o.rotation_euler),[-0.3512776494026184, -1.168831467628479, -0.8326771259307861])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7120649814605713, -0.35297513008117676, -0.43788155913352966, -0.4202757775783539]))<=1e-5,('6',tuple(o.rotation_quaternion),[0.7120649814605713, -0.35297513008117676, -0.43788155913352966, -0.4202757775783539])
o=bpy.data.objects.new('7',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[1.6005245447158813, 0.9642487168312073, 2.4512946605682373];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.6005245447158813, 0.9642487168312073, 2.4512946605682373]))<=1e-5,('7',tuple(o.rotation_euler),[1.6005245447158813, 0.9642487168312073, 2.4512946605682373])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('7',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('8',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[-1.7848265171051025, 0.40723714232444763, 1.1512677669525146];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.7848265171051025, 0.40723714232444763, 1.1512677669525146]))<=1e-5,('8',tuple(o.rotation_euler),[-1.7848265171051025, 0.40723714232444763, 1.1512677669525146])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('8',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('9',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[1.6609456539154053, 1.3826301097869873, -1.569734811782837];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.6609456539154053, 1.3826301097869873, -1.569734811782837]))<=1e-5,('9',tuple(o.rotation_euler),[1.6609456539154053, 1.3826301097869873, -1.569734811782837])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('9',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('10',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[0.9409395456314087, -0.7564769983291626, 0.5804282426834106];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.9409395456314087, -0.7564769983291626, 0.5804282426834106]))<=1e-5,('10',tuple(o.rotation_euler),[0.9409395456314087, -0.7564769983291626, 0.5804282426834106])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('10',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('11',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[-0.2542142868041992, -1.1337722539901733, -1.3205698728561401];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.2542142868041992, -1.1337722539901733, -1.3205698728561401]))<=1e-5,('11',tuple(o.rotation_euler),[-0.2542142868041992, -1.1337722539901733, -1.3205698728561401])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('11',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('12',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[-0.1589077115058899, -2.1377241611480713, 2.4255688190460205];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.1589077115058899, -2.1377241611480713, 2.4255688190460205]))<=1e-5,('12',tuple(o.rotation_euler),[-0.1589077115058899, -2.1377241611480713, 2.4255688190460205])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('12',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('13',None);bpy.context.collection.objects.link(o)
o.rotation_mode='XZY';o.rotation_euler=[-2.404726505279541, -1.1220234632492065, 2.4827611446380615];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-2.404726505279541, -1.1220234632492065, 2.4827611446380615]))<=1e-5,('13',tuple(o.rotation_euler),[-2.404726505279541, -1.1220234632492065, 2.4827611446380615])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[-0.3710038661956787, -0.4368383288383484, -0.8094112873077393, 0.12799116969108582]))<=1e-5,('13',tuple(o.rotation_quaternion),[-0.3710038661956787, -0.4368383288383484, -0.8094112873077393, 0.12799116969108582])
o=bpy.data.objects.new('14',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[0.7339703440666199, 0.30150023102760315, -2.1507458686828613];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.7339703440666199, 0.30150023102760315, -2.1507458686828613]))<=1e-5,('14',tuple(o.rotation_euler),[0.7339703440666199, 0.30150023102760315, -2.1507458686828613])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('14',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('15',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[-1.242967128753662, 1.0754426717758179, -0.6057057976722717];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.242967128753662, 1.0754426717758179, -0.6057057976722717]))<=1e-5,('15',tuple(o.rotation_euler),[-1.242967128753662, 1.0754426717758179, -0.6057057976722717])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('15',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('16',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[1.2198331356048584, -1.4809279441833496, -0.7312309741973877];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.2198331356048584, -1.4809279441833496, -0.7312309741973877]))<=1e-5,('16',tuple(o.rotation_euler),[1.2198331356048584, -1.4809279441833496, -0.7312309741973877])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('16',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('17',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[-1.9815300703048706, 0.3345862030982971, -1.263787865638733];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.9815300703048706, 0.3345862030982971, -1.263787865638733]))<=1e-5,('17',tuple(o.rotation_euler),[-1.9815300703048706, 0.3345862030982971, -1.263787865638733])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('17',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('18',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[0.6368353366851807, 1.0813065767288208, 1.7277084589004517];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.6368353366851807, 1.0813065767288208, 1.7277084589004517]))<=1e-5,('18',tuple(o.rotation_euler),[0.6368353366851807, 1.0813065767288208, 1.7277084589004517])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('18',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('19',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[2.302393913269043, -0.30290907621383667, -1.3837419748306274];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[2.302393913269043, -0.30290907621383667, -1.3837419748306274]))<=1e-5,('19',tuple(o.rotation_euler),[2.302393913269043, -0.30290907621383667, -1.3837419748306274])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('19',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('20',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YXZ';o.rotation_euler=[-1.1785801649093628, 1.6096833944320679, -1.528143048286438];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.1785801649093628, 1.6096833944320679, -1.528143048286438]))<=1e-5,('20',tuple(o.rotation_euler),[-1.1785801649093628, 1.6096833944320679, -1.528143048286438])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.13897377252578735, 0.13636170327663422, 0.6991678476333618, -0.6879361271858215]))<=1e-5,('20',tuple(o.rotation_quaternion),[0.13897377252578735, 0.13636170327663422, 0.6991678476333618, -0.6879361271858215])
o=bpy.data.objects.new('21',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[-0.9387974739074707, -0.1498853713274002, -2.2270143032073975];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.9387974739074707, -0.1498853713274002, -2.2270143032073975]))<=1e-5,('21',tuple(o.rotation_euler),[-0.9387974739074707, -0.1498853713274002, -2.2270143032073975])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('21',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('22',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[-0.176334410905838, 0.6974750757217407, 0.7957105040550232];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.176334410905838, 0.6974750757217407, 0.7957105040550232]))<=1e-5,('22',tuple(o.rotation_euler),[-0.176334410905838, 0.6974750757217407, 0.7957105040550232])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('22',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('23',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[2.2707979679107666, 0.2959074079990387, 1.862023115158081];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[2.2707979679107666, 0.2959074079990387, 1.862023115158081]))<=1e-5,('23',tuple(o.rotation_euler),[2.2707979679107666, 0.2959074079990387, 1.862023115158081])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('23',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('24',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[-1.2193206548690796, -1.117973804473877, -1.1132334470748901];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.2193206548690796, -1.117973804473877, -1.1132334470748901]))<=1e-5,('24',tuple(o.rotation_euler),[-1.2193206548690796, -1.117973804473877, -1.1132334470748901])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('24',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('25',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[1.497052550315857, -1.7767103910446167, -1.4758397340774536];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.497052550315857, -1.7767103910446167, -1.4758397340774536]))<=1e-5,('25',tuple(o.rotation_euler),[1.497052550315857, -1.7767103910446167, -1.4758397340774536])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('25',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('26',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[-1.7922437191009521, -1.7914611101150513, 1.4632996320724487];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.7922437191009521, -1.7914611101150513, 1.4632996320724487]))<=1e-5,('26',tuple(o.rotation_euler),[-1.7922437191009521, -1.7914611101150513, 1.4632996320724487])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('26',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('27',None);bpy.context.collection.objects.link(o)
o.rotation_mode='YZX';o.rotation_euler=[0.4254032075405121, -1.3002113103866577, -1.5143382549285889];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.4254032075405121, -1.3002113103866577, -1.5143382549285889]))<=1e-5,('27',tuple(o.rotation_euler),[0.4254032075405121, -1.3002113103866577, -1.5143382549285889])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.6532595753669739, -0.28424182534217834, -0.3145653009414673, -0.6273015141487122]))<=1e-5,('27',tuple(o.rotation_quaternion),[0.6532595753669739, -0.28424182534217834, -0.3145653009414673, -0.6273015141487122])
o=bpy.data.objects.new('28',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[-1.055712103843689, 1.9040273427963257, -1.4835970401763916];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.055712103843689, 1.9040273427963257, -1.4835970401763916]))<=1e-5,('28',tuple(o.rotation_euler),[-1.055712103843689, 1.9040273427963257, -1.4835970401763916])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('28',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('29',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[0.7495492100715637, -1.8532134294509888, -2.1676692962646484];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.7495492100715637, -1.8532134294509888, -2.1676692962646484]))<=1e-5,('29',tuple(o.rotation_euler),[0.7495492100715637, -1.8532134294509888, -2.1676692962646484])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('29',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('30',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[-0.27952906489372253, 0.784967303276062, 1.0104098320007324];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.27952906489372253, 0.784967303276062, 1.0104098320007324]))<=1e-5,('30',tuple(o.rotation_euler),[-0.27952906489372253, 0.784967303276062, 1.0104098320007324])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('30',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('31',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[-0.5724552273750305, 0.05639628693461418, -2.1226353645324707];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.5724552273750305, 0.05639628693461418, -2.1226353645324707]))<=1e-5,('31',tuple(o.rotation_euler),[-0.5724552273750305, 0.05639628693461418, -2.1226353645324707])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('31',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('32',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[2.2884745597839355, -1.5876106023788452, -0.4914451241493225];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[2.2884745597839355, -1.5876106023788452, -0.4914451241493225]))<=1e-5,('32',tuple(o.rotation_euler),[2.2884745597839355, -1.5876106023788452, -0.4914451241493225])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('32',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('33',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[2.3907690048217773, 2.468531370162964, 1.331595540046692];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[2.3907690048217773, 2.468531370162964, 1.331595540046692]))<=1e-5,('33',tuple(o.rotation_euler),[2.3907690048217773, 2.468531370162964, 1.331595540046692])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('33',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('34',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZXY';o.rotation_euler=[-2.3238775730133057, -0.9952343702316284, 1.4451885223388672];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-2.3238775730133057, -0.9952343702316284, 1.4451885223388672]))<=1e-5,('34',tuple(o.rotation_euler),[-2.3238775730133057, -0.9952343702316284, 1.4451885223388672])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.5516985058784485, -0.7302959561347961, 0.3908844590187073, -0.09749843180179596]))<=1e-5,('34',tuple(o.rotation_quaternion),[0.5516985058784485, -0.7302959561347961, 0.3908844590187073, -0.09749843180179596])
o=bpy.data.objects.new('35',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[-1.199118733406067, -0.6943336725234985, 0.8027295470237732];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.199118733406067, -0.6943336725234985, 0.8027295470237732]))<=1e-5,('35',tuple(o.rotation_euler),[-1.199118733406067, -0.6943336725234985, 0.8027295470237732])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('35',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('36',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[-2.1384594440460205, 0.6849598288536072, 0.7929483652114868];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-2.1384594440460205, 0.6849598288536072, 0.7929483652114868]))<=1e-5,('36',tuple(o.rotation_euler),[-2.1384594440460205, 0.6849598288536072, 0.7929483652114868])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('36',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('37',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[-1.9083127975463867, 2.407369613647461, -1.5595332384109497];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.9083127975463867, 2.407369613647461, -1.5595332384109497]))<=1e-5,('37',tuple(o.rotation_euler),[-1.9083127975463867, 2.407369613647461, -1.5595332384109497])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('37',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('38',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[-1.1681076288223267, -1.9138470888137817, 0.8815876841545105];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-1.1681076288223267, -1.9138470888137817, 0.8815876841545105]))<=1e-5,('38',tuple(o.rotation_euler),[-1.1681076288223267, -1.9138470888137817, 0.8815876841545105])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('38',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('39',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[0.6811003684997559, -0.033512745052576065, -2.335209608078003];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.6811003684997559, -0.033512745052576065, -2.335209608078003]))<=1e-5,('39',tuple(o.rotation_euler),[0.6811003684997559, -0.033512745052576065, -2.335209608078003])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('39',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('40',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[0.4200643002986908, -1.898126482963562, 1.9277938604354858];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.4200643002986908, -1.898126482963562, 1.9277938604354858]))<=1e-5,('40',tuple(o.rotation_euler),[0.4200643002986908, -1.898126482963562, 1.9277938604354858])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('40',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
o=bpy.data.objects.new('41',None);bpy.context.collection.objects.link(o)
o.rotation_mode='ZYX';o.rotation_euler=[2.4708123207092285, -2.214583158493042, 1.4576066732406616];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[2.4708123207092285, -2.214583158493042, 1.4576066732406616]))<=1e-5,('41',tuple(o.rotation_euler),[2.4708123207092285, -2.214583158493042, 1.4576066732406616])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.6722908616065979, 0.11885987222194672, -0.5007811188697815, -0.5320860743522644]))<=1e-5,('41',tuple(o.rotation_quaternion),[0.6722908616065979, 0.11885987222194672, -0.5007811188697815, -0.5320860743522644])
o=bpy.data.objects.new('42',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[1.4070212841033936, -2.1197190284729004, -1.7455204725265503];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XYZ'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.21866901218891144, -0.9416168928146362, 1.3521275520324707]))<=1e-5,('42',tuple(o.rotation_euler),[-0.21866901218891144, -0.9416168928146362, 1.3521275520324707])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('42',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('43',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[-1.1860271692276, 1.9916516542434692, 0.40407082438468933];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='XZY'
assert o.rotation_euler.order=='XZY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[1.0838972330093384, -1.4141945838928223, 0.6119540929794312]))<=1e-5,('43',tuple(o.rotation_euler),[1.0838972330093384, -1.4141945838928223, 0.6119540929794312])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('43',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('44',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[-1.869583249092102, 0.3933621942996979, -1.772881031036377];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YXZ'
assert o.rotation_euler.order=='YXZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.1280089169740677, -0.9530407190322876, 1.174355149269104]))<=1e-5,('44',tuple(o.rotation_euler),[-0.1280089169740677, -0.9530407190322876, 1.174355149269104])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('44',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('45',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[1.5136502981185913, 2.275618553161621, 0.8717962503433228];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='YZX'
assert o.rotation_euler.order=='YZX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.321750670671463, -1.2490460872650146, 1.1552443504333496]))<=1e-5,('45',tuple(o.rotation_euler),[-0.321750670671463, -1.2490460872650146, 1.1552443504333496])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('45',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('46',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[-1.7563378810882568, 1.2529147863388062, 1.4566271305084229];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZXY'
assert o.rotation_euler.order=='ZXY'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.8087204098701477, -0.5880026817321777, 0.9827938079833984]))<=1e-5,('46',tuple(o.rotation_euler),[0.8087204098701477, -0.5880026817321777, 0.9827938079833984])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('46',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('47',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[-2.174042224884033, -2.3645834922790527, -0.04623996093869209];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='ZYX'
assert o.rotation_euler.order=='ZYX'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[0.8996526002883911, -0.3930187523365021, 1.4321566820144653]))<=1e-5,('47',tuple(o.rotation_euler),[0.8996526002883911, -0.3930187523365021, 1.4321566820144653])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422]))<=1e-5,('47',tuple(o.rotation_quaternion),[0.7219948768615723, 0.2062842696905136, -0.4125685393810272, 0.5157106518745422])
o=bpy.data.objects.new('48',None);bpy.context.collection.objects.link(o)
o.rotation_mode='QUATERNION';o.rotation_euler=[-0.9860703945159912, -1.2788276672363281, -0.9998450875282288];o.rotation_quaternion=[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5];o.location=(2,-3,4);o.scale=(-.5,1.2,2)
o.rotation_mode='QUATERNION'
assert o.rotation_euler.order=='XYZ'
assert max(abs(a-b) for a,b in zip(o.rotation_euler,[-0.9860703945159912, -1.2788276672363281, -0.9998450875282288]))<=1e-5,('48',tuple(o.rotation_euler),[-0.9860703945159912, -1.2788276672363281, -0.9998450875282288])
assert max(abs(a-b) for a,b in zip(o.rotation_quaternion,[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5]))<=1e-5,('48',tuple(o.rotation_quaternion),[0.699999988079071, 0.20000000298023224, -0.4000000059604645, 0.5])
