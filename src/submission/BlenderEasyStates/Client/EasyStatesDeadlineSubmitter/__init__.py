from pathlib import Path

import bpy
import tempfile

bl_info = {
    "name": "Submit EasyStates To Deadline",
    "description": "Submit a EasyStates batch job to Deadline",
    "author": "Rodrigo Gama",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "category": "Render",
    "location": "View 3D > Sidebar > EasyStates > Render",
}

from . import deadline
from datetime import datetime

class EZS_OT_SubmitToDeadline(bpy.types.Operator):
    bl_idname = "easystates.submit_to_deadline"
    bl_label = "Submit Blender To Deadline"
    bl_description = "Submit a Blender job to Deadline"
        
    @staticmethod
    def _generate_scene_states_file(context: bpy.types.Context) -> tuple[bool, Path, str]:
        """Generate a temporary text file containing the scene states to render
        We are using this instead of passing the data directly to avoid issues with very 
        long command line arguments.
        """
        ezs_manager = getattr(context.scene, "easystates_manager", None)
        if ezs_manager is None:
            raise Exception("EZS Manager not found on the scene, make sure you have the EasyStates addon enabled.")
                
        render_states : list[tuple[str, str, str, str]] = [] # [(state name, frame range, scene_state_id, state_filepath),]  
        for state in ezs_manager.scene_states: # type:ignore
            if not state.render:
                continue
            
            _frame_range = context.scene.frame_current
            if state.animation_modifier.render_as_animation:
                _frame_range = state.animation_modifier.frame_start
                if state.animation_modifier.frame_start != state.animation_modifier.frame_end:
                    _frame_range = f"{_frame_range}-{state.animation_modifier.frame_end}"
                    
            parsed_output, is_valid_path = state.get_output_filepath(
                context,
                ezs_manager,
                parse_output=True,
                session_start_datetime=datetime.now(),
                scene_state_datetime=datetime.now(),
            )
            if not is_valid_path:
                return (False, Path(""), f"Invalid output path for scene state '{state.name}': {parsed_output}")
            
            render_states.append((state.name, str(_frame_range), state.id, str(parsed_output)))
            
        txt_file = Path(tempfile.gettempdir()) / f"temp_scene_states_file.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            for state_name, frame_range, scene_state_id, state_filepath in render_states:
                f.write(f"{state_name}|{frame_range}|{scene_state_id}|{state_filepath}\n")
                
        return (True, txt_file, "")
    
    def execute( self, context ):
        if not bpy.data.is_saved:
            self.report( {'ERROR'}, "You must save your .blend file before submitting to Deadline" )
            return {'CANCELLED'}
        
        success, scene_states_file, error_message = self._generate_scene_states_file(context)
        if not success:
            self.report( {'ERROR'}, error_message )
            return {'CANCELLED'}
        
        bpy.ops.wm.save_mainfile() # Auto Save the current .blend file before submitting     
        deadline.submit_easystate_render(
            bpy.data.filepath,
            scene_states_file
        )
        return {'FINISHED'}
        
classes = (
    EZS_OT_SubmitToDeadline,
)

def _submit_render_operator(self, context):
    """Add a button to the EZS Render panel to submit to Deadline"""
    self.layout.separator()
    row = self.layout.row()
    row.operator("easystates.submit_to_deadline", text="EasyStates: Submit To Deadline", icon="RESTRICT_VIEW_OFF")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)      
    bpy.types.TOPBAR_MT_render.append(_submit_render_operator)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_render.remove(_submit_render_operator)

if __name__ == "__main__":
    register()