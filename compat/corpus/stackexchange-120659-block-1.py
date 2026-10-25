bl_info = {
        "name": "Areatype Trim",
        "description":"This example adds a button which toggles a split of an area with another.",
        "author":"dustractor@gmail.com, tintwotin",
        "version":(0,1),
        "blender":(2,65,0),
        "location":"Button prepended to the header of the sequencer.",
        "warning":"",
        "wiki_url":"",
        "category": "Sequencer"
        }

import bpy


class AREATYPE_OT_trim(bpy.types.Operator):
    bl_idname = "areatype.trimview"
    bl_label = "Trim"

    def execute(self,context):
        thisarea = context.area
        otherarea = None
        tgxvalue = thisarea.x + thisarea.width + 1
        thistype = context.area.type
        arealist = list(context.screen.areas)
        for area in context.screen.areas:
            if area == thisarea:
                continue
            elif area.x == tgxvalue and area.y == thisarea.y:
                otherarea = area
                break
        if otherarea: #leave trim-mode
            bpy.ops.screen.area_join(min_x=thisarea.x,min_y=thisarea.y,max_x=otherarea.x,max_y=otherarea.y)
            print("this x: "+str(thisarea.x))   #min_x = left x of left window 
            print("this y: "+str(thisarea.y))   #min_y = mouse position, starting from window bottom y
            print("other x: "+str(otherarea.x)) #max_x = x between left and right window
            print("other y: "+str(otherarea.y)) #max_y = mouse position, starting from window bottom y

            bpy.context.space_data.overlay_type = 'CURRENT' 
            bpy.ops.screen.screen_full_area()
            bpy.ops.screen.screen_full_area()
            return {"FINISHED"}
        else: # enter trim-mode
            bpy.context.space_data.overlay_type = 'REFERENCE'          
            areax = None
            bpy.ops.screen.area_split(direction="VERTICAL")
            for area in context.screen.areas:
                if area not in arealist:
                    areax = area
                    break
            if areax:
                areax.type = thistype
                return {"FINISHED"}
        return {"CANCELLED"}


def draw_func(self,context):
    layout = self.layout
    layout.operator("areatype.trimview",text="Trim",icon="ARROW_LEFTRIGHT")

def register():
    bpy.utils.register_class(AREATYPE_OT_trim)
    bpy.types.SEQUENCER_HT_header.prepend(draw_func)   

def unregister():
    bpy.utils.unregister_class(AREATYPE_OT_trim)
    bpy.types.SEQUENCER_HT_header.remove(draw_func)


if __name__ == "__main__":
    register()
