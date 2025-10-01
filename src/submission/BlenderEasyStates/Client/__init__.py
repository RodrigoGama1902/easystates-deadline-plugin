#
#Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from pathlib import Path

import bpy
import tempfile
import uuid

bl_info = {
    "name": "Submit Blender To Deadline",
    "description": "Submit a Blender job to Deadline",
    "author": "Thinkbox Software Inc",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "category": "Render",
    "location": "Render > Submit To Deadline",
}

from . import deadline

class SubmitToDeadline_Operator (bpy.types.Operator):
    bl_idname = "ops.submit_blender_to_deadline"
    bl_label = "Submit Blender To Deadline"
    bl_description = "Submit a Blender job to Deadline"
        
    @staticmethod
    def _generate_scene_states_file(scene: bpy.types.Scene) -> Path:
        
        ezs_manager = getattr(scene, "easystates_manager", None)
        if ezs_manager is None:
            raise Exception("EZS Manager not found on the scene, make sure you have the EasyStates addon enabled.")
                
        render_states : list[tuple[str, str]] = [] # [(state name, frame range),]  
        for state in ezs_manager.scene_states: # type:ignore
            if not state.render:
                continue
            
            _frame_range = scene.frame_current
            if state.animation_modifier.render_as_animation:
                _frame_range = state.animation_modifier.frame_start
                if state.animation_modifier.frame_start != state.animation_modifier.frame_end:
                    _frame_range = f"{_frame_range}-{state.animation_modifier.frame_end}"
            
            render_states.append((state.name, str(_frame_range)))
            
        txt_file = Path(tempfile.gettempdir()) / f"{uuid.uuid4().hex}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            for state_name, frame_range in render_states:
                f.write(f"{state_name}|{frame_range}\n")
                
        return txt_file
    
    def execute( self, context ):
        
        if not bpy.data.is_saved:
            self.report( {'ERROR'}, "You must save your .blend file before submitting to Deadline" )
            return {'CANCELLED'}
        
        scene_states_file = self._generate_scene_states_file(context.scene)
        
        bpy.ops.wm.save_mainfile() # Auto Save the current .blend file before submitting     

        deadline.submit_easystate_render(
            context.scene,
            bpy.data.filepath,
            scene_states_file
        )
        return {'FINISHED'}
    
class EZS_PT_DeadlineSubmitter(bpy.types.Panel):
    """Modifiers Panel."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "EasyStates"
    bl_label = "Deadline Submitter"
    
    def draw(self, context: bpy.types.Context):
        self.layout.operator( SubmitToDeadline_Operator.bl_idname, text="Submit To Deadline" )
    
classes = (
    EZS_PT_DeadlineSubmitter,
    SubmitToDeadline_Operator
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()