import bpy

# pass arguments to build a handler
def text_body_handler(obname, textname):
    # the handler method
    def text_body(scene):
        text = bpy.data.texts.get(textname)
        text_ob = scene.objects.get(obname)
        if not text and text_ob:
            print("Error: check names")
            return 
        f = scene.frame_current
        lines = len(text.lines)
        if text_ob and f <= lines:
            text_ob.data.body = text.lines[f-1].body
 
    return text_body

bpy.app.handlers.frame_change_post.clear()           
bpy.app.handlers.frame_change_post.append(text_body_handler("Text", "Text"))
