#!/usr/bin/env python3

from System import *
from System.Diagnostics import *
from System.IO import *

from Deadline.Plugins import *
from Deadline.Scripting import *


def GetDeadlinePlugin() -> 'EasyStatesBlenderPlugin':
    return EasyStatesBlenderPlugin()
    
def CleanupDeadlinePlugin(deadlinePlugin: 'EasyStatesBlenderPlugin') -> None:
    deadlinePlugin.Cleanup()
    
def _easystates_render_python_expr(scene_state_id: str, frame_start: int, frame_end: int) -> str:
    """
    Returns a Python expression to be used with Blender's -P argument
    to set up the scene for rendering with EasyStates.
    """
    return (
        "import bpy, addon_utils\n"
        "if not hasattr(bpy.context.scene, 'easystates_manager'):\n"
        "    print('EasyStates add-on is not enabled.')\n"
        "else:\n"
        "    bpy.ops.easystates.single_render(id={scene_state_id}, background_render=True, frame_start={frame_start}, frame_end={frame_end})\n"
    ).format(scene_state_id=repr(scene_state_id), frame_start=frame_start, frame_end=frame_end)

class EasyStatesBlenderPlugin(DeadlinePlugin):
    frameCount: int = 0
    finishedFrameCount: int = 0
    totalFrames: int = 0
    finishedFrames: int = 0
    totalChunks: int = 0
    currentChunk: int = 0
    chunkType: str = ""
    
    def __init__(self) -> None:
        super().__init__()  # Required in Deadline 10.3 and later.
        
        self.InitializeProcessCallback += self.InitializeProcess
        self.RenderExecutableCallback += self.RenderExecutable
        self.RenderArgumentCallback += self.RenderArgument
        self.PreRenderTasksCallback += self.PreRenderTasks
        self.PostRenderTasksCallback += self.PostRenderTasks
    
    def Cleanup(self) -> None:
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback
        
        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback
        del self.PreRenderTasksCallback
        del self.PostRenderTasksCallback
    
    def InitializeProcess(self) -> None:
        """Initialize the process settings."""
        self.SingleFramesOnly = False
        self.StdoutHandling = True
        
        self.AddStdoutHandlerCallback(".*Tile ([0-9]+)/([0-9]+).*").HandleCallback += self.HandleTileProgress
        self.AddStdoutHandlerCallback(".*Sample ([0-9]+)/([0-9]+).*").HandleCallback += self.HandleSampleProgress
        self.AddStdoutHandlerCallback(".*Scene, Part ([0-9]+)-([0-9]+).*").HandleCallback += self.HandleSceneProgress
        self.AddStdoutHandlerCallback(".*Saved:.*").HandleCallback += self.HandleStdoutSaved
        self.AddStdoutHandlerCallback("Unable to open.*").HandleCallback += self.HandleStdoutFailed
        self.AddStdoutHandlerCallback("Failed to read blend file.*").HandleCallback += self.HandleStdoutFailed
        self.AddStdoutHandlerCallback(".*Unable to create directory.*").HandleCallback += self.HandleStdoutFailed
        self.AddStdoutHandlerCallback(".*EasyStates add-on is not enabled.*").HandleCallback += self.HandleStdoutError
    
    def RenderExecutable(self) -> str:
        """Determine the path to the Blender executable."""
        executableList: str = self.GetConfigEntry("BlenderEasyStatesExecutable")
        executable: str = FileUtils.SearchFileList(executableList)
        if executable == "":
            self.FailRender(
                "Blender render executable was not found in the semicolon separated list \"" +
                executableList +
                "\". The path to the render executable can be configured from the Plugin Configuration in the Deadline Monitor."
            )
        return executable
        
    def RenderArgument(self) -> str:
        """Construct the command line arguments for Blender rendering with EasyStates."""
        
        _blend_file: str = self.GetPluginInfoEntryWithDefault("SceneFile", self.GetDataFilename())
        _scene_state_id: str = self.GetPluginInfoEntryWithDefault("SceneStateID", "")
        
        _blend_file = RepositoryUtils.CheckPathMapping(_blend_file)
        if SystemUtils.IsRunningOnWindows():
            _blend_file = _blend_file.replace("/", "\\")
            if _blend_file.startswith("\\") and not _blend_file.startswith("\\\\"):
                _blend_file = "\\" + _blend_file
        else:
            _blend_file = _blend_file.replace("\\", "/")
        
        render_agrs: str = " -b \"" + _blend_file + "\""
        render_agrs += " --python-expr \"" + _easystates_render_python_expr(
            _scene_state_id,
            self.GetStartFrame(),
            self.GetEndFrame()
        ).strip().replace('"', '\\"') + "\""
                
        return render_agrs
        
    def PreRenderTasks(self) -> None:
        """Tasks to perform before rendering starts."""
        self.LogInfo("EasyStates Blender job starting...")
        self.totalFrames = self.GetEndFrame() - self.GetStartFrame() + 1
        self.finishedFrames = 0
        self.totalChunks = 0
        self.currentChunk = 0
        self.chunkType = ""
        self.UpdateProgress()
        
    def PostRenderTasks(self) -> None:
        """Tasks to perform after rendering ends."""
        self.LogInfo("EasyStatesBlender job finished.")
        
    def UpdateProgress(self) -> None:
        """Update the progress of the render task."""
        progress: float = self.finishedFrames
        if self.chunkType != "":
            progress += (self.currentChunk / float(self.totalChunks))
            message: str = "Rendering %(ct)s %(cc)s/%(tt)s of frame %(ff)s/%(tf)s"
        else:
            message = "Rendering frame %(ff)s/%(tf)s"
            
        self.SetStatusMessage(message % {
            "ct": self.chunkType,
            "ff": str(self.finishedFrames + 1),
            "tf": str(self.totalFrames),
            "cc": str(self.currentChunk),
            "tt": str(self.totalChunks)
        })
        
        progress = progress / float(self.totalFrames)
        self.SetProgress(progress * 100)
        
    def HandleStdoutSaved(self) -> None:
        """Handle the event when a frame is saved."""
        self.finishedFrames += 1
        self.currentChunk = 0
        self.UpdateProgress()
        if self.finishedFrames + 1 > self.totalFrames:
            self.SetStatusMessage("Task complete.")
        
    def HandleTileProgress(self) -> None:
        """Handle tile progress updates."""
        self.currentChunk = int(self.GetRegexMatch(1))
        self.totalChunks = int(self.GetRegexMatch(2))
        self.chunkType = "tile"
        self.UpdateProgress()
        
    def HandleSampleProgress(self) -> None:
        """Handle sample progress updates."""
        self.currentChunk = int(self.GetRegexMatch(1))
        self.totalChunks = int(self.GetRegexMatch(2))
        self.chunkType = "sample"
        self.UpdateProgress()
        
    def HandleSceneProgress(self) -> None:
        """Handle scene part progress updates."""
        self.UpdateProgress()
            
    def HandleStdoutError(self) -> None:
        """Handle errors reported in stdout."""
        self.FailRender(self.GetRegexMatch(0))
        
    def HandleStdoutFailed(self) -> None:
        """Handle failure messages reported in stdout."""
        self.FailRender(self.GetRegexMatch(0))
