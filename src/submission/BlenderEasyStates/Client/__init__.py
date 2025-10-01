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

import bpy

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
    def _get_scene_states_to_render(scene: bpy.types.Scene) -> list[int]:
        
        ezs_manager = getattr(scene, "easystates_manager", None)
        if ezs_manager is None:
            raise Exception("EZS Manager not found on the scene, make sure you have the EasyStates addon enabled.")
        
        idx_list = []
        for idx, state in enumerate(ezs_manager.scene_states): # type:ignore
            if not state.render:
                continue
            idx_list.append(idx)
            
        return idx_list
    
    @staticmethod
    def _get_scene_states_render_list(scene: bpy.types.Scene) -> str:
        """
        Builds a Deadline-compatible frame list string from enabled scene states.
        Example output: "0,2-4,6"
        """

        ezs_manager = getattr(scene, "easystates_manager", None)
        if ezs_manager is None:
            raise Exception("EZS Manager not found on the scene, make sure you have the EasyStates addon enabled.")

        # Collect all indexes of scene states to render
        indices: list[int] = [
            idx for idx, state in enumerate(ezs_manager.scene_states)  # type: ignore
            if getattr(state, "render", False)
        ]

        if not indices:
            return ""

        # Build ranges for consecutive numbers (e.g. 2,3,4 -> "2-4")
        ranges: list[str] = []
        start = prev = indices[0]

        for idx in indices[1:]:
            if idx == prev + 1:
                # still in a consecutive sequence
                prev = idx
                continue
            else:
                # close the previous range
                if start == prev:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{prev}")
                # start new range
                start = prev = idx

        # close last range
        if start == prev:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{prev}")

        return ",".join(ranges)
    
    def execute( self, context ):
        
        if not bpy.data.is_saved:
            self.report( {'ERROR'}, "You must save your .blend file before submitting to Deadline" )
            return {'CANCELLED'}
        
        state_list = self._get_scene_states_render_list(context.scene)
        
        bpy.ops.wm.save_mainfile() # Auto Save the current .blend file before submitting     

        deadline.submit_easystate_render(
            context.scene,
            bpy.data.filepath,
            state_list
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