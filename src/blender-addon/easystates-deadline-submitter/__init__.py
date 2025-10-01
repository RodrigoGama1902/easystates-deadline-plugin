import bpy
from bpy.types import Context

bl_info = {
    "name": "EasyStates Deadline Submitter",
    "description": "Deadline Submitter for EasyStates",
    "author": "Rodrigo Gama",
    "version": (0, 0, 1),
    "blender": (4, 5, 0),
    "location": "View3D",
    "category": "3D View",
    "doc_url": "https://docs.cgoutset.com/easystates/",
    "tracker_url": "https://help.cgoutset.com/bug-report/",
}
class EZS_PT_DeadlineSubmitter(bpy.types.Panel):
    """Modifiers Panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "EasyStates"
    bl_label = "Deadline Submitter"
    
    def draw(self, context: Context):
        layout = self.layout
        
classes = (
    EZS_PT_DeadlineSubmitter,
)

def register():
    """Register addon."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister addon."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)