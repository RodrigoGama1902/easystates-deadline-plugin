from System import *
from System.Collections.Specialized import *
from System.IO import *
from System.Text import *

from Deadline.Scripting import *

from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

# For Integration UI
import imp
import os
from datetime import datetime
imp.load_source( 'IntegrationUI', RepositoryUtils.GetRepositoryFilePath( "submission/Integration/Main/IntegrationUI.py", True ) )
import IntegrationUI

########################################################################
## Globals
########################################################################
scriptDialog = None
settings = None
integration_dialog = None
StatesFile = None

ProjectManagementOptions = ["Shotgun","FTrack"]
DraftRequested = True

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__( *args ):
    global scriptDialog
    global settings
    global ProjectManagementOptions
    global DraftRequested
    global integration_dialog
    global StatesFile

    scriptDialog = DeadlineScriptDialog()
    scriptDialog.SetTitle( "Submit EasyStates Blender Batch To Deadline" )
    scriptDialog.SetIcon( scriptDialog.GetIcon( 'Blender' ) )
    
    scriptDialog.AddTabControl("Tabs", 0, 0)
    
    scriptDialog.AddTabPage("Batch Options")
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator1", "SeparatorControl", "Batch Description", 0, 0, colSpan=2 )

    scriptDialog.AddControlToGrid( "NameLabel", "LabelControl", "Batch Name", 1, 0, "The name of your job. This is optional, and if left blank, it will default to 'Untitled'.", False )
    scriptDialog.AddControlToGrid( "BatchNameBox", "TextControl", "Untitled", 1, 1 )
    scriptDialog.AddSelectionControlToGrid( "IncludeTimestamp", "CheckBoxControl", True, "Include Timestamp", 1, 2, "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job. " )

    scriptDialog.AddControlToGrid( "CommentLabel", "LabelControl", "Comment", 2, 0, "A simple description of your job. This is optional and can be left blank. (Will be applied to all jobs in the batch)", False )
    scriptDialog.AddControlToGrid( "CommentBox", "TextControl", "", 2, 1 )

    scriptDialog.AddControlToGrid( "DepartmentLabel", "LabelControl", "Department", 3, 0, "The department you belong to. This is optional and can be left blank. (Will be applied to all jobs in the batch)", False )
    scriptDialog.AddControlToGrid( "DepartmentBox", "TextControl", "", 3, 1 )
    scriptDialog.EndGrid()

    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator2", "SeparatorControl", "Job Options", 0, 0, colSpan=3 )

    scriptDialog.AddControlToGrid( "PoolLabel", "LabelControl", "Pool", 1, 0, "The pool that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "PoolBox", "PoolComboControl", "none", 1, 1 )

    scriptDialog.AddControlToGrid( "SecondaryPoolLabel", "LabelControl", "Secondary Pool", 2, 0, "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Workers.", False )
    scriptDialog.AddControlToGrid( "SecondaryPoolBox", "SecondaryPoolComboControl", "", 2, 1 )

    scriptDialog.AddControlToGrid( "GroupLabel", "LabelControl", "Group", 3, 0, "The group that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "GroupBox", "GroupComboControl", "none", 3, 1 )

    scriptDialog.AddControlToGrid( "PriorityLabel", "LabelControl", "Priority", 4, 0, "A job can have a numeric priority ranging from 0 to 100, where 0 is the lowest priority and 100 is the highest priority.", False )
    scriptDialog.AddRangeControlToGrid( "PriorityBox", "RangeControl", RepositoryUtils.GetMaximumPriority() / 2, 0, RepositoryUtils.GetMaximumPriority(), 0, 1, 4, 1 )

    scriptDialog.AddControlToGrid( "TaskTimeoutLabel", "LabelControl", "Task Timeout", 5, 0, "The number of minutes a Worker has to render a task for this job before it requeues it. Specify 0 for no limit.", False )
    scriptDialog.AddRangeControlToGrid( "TaskTimeoutBox", "RangeControl", 0, 0, 1000000, 0, 1, 5, 1 )
    scriptDialog.AddSelectionControlToGrid( "AutoTimeoutBox", "CheckBoxControl", False, "Enable Auto Task Timeout", 5, 2, "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job. " )

    scriptDialog.AddControlToGrid( "ConcurrentTasksLabel", "LabelControl", "Concurrent Tasks", 6, 0, "The number of tasks that can render concurrently on a single Worker. This is useful if the rendering application only uses one thread to render and your Workers have multiple CPUs.", False )
    scriptDialog.AddRangeControlToGrid( "ConcurrentTasksBox", "RangeControl", 1, 1, 16, 0, 1, 6, 1 )
    scriptDialog.AddSelectionControlToGrid( "LimitConcurrentTasksBox", "CheckBoxControl", True, "Limit Tasks To Worker's Task Limit", 6, 2, "If you limit the tasks to a Worker's task limit, then by default, the Worker won't dequeue more tasks then it has CPUs. This task limit can be overridden for individual Workers by an administrator." )

    scriptDialog.AddControlToGrid( "MachineLimitLabel", "LabelControl", "Machine Limit", 7, 0, "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit.", False )
    scriptDialog.AddRangeControlToGrid( "MachineLimitBox", "RangeControl", 0, 0, 1000000, 0, 1, 7, 1 )
    scriptDialog.AddSelectionControlToGrid( "IsBlacklistBox", "CheckBoxControl", False, "Machine List Is A Deny List", 7, 2, "You can force the job to render on specific machines by using an allow list, or you can avoid specific machines by using a deny list." )

    scriptDialog.AddControlToGrid( "MachineListLabel", "LabelControl", "Machine List", 8, 0, "The list of machines on the deny list or allow list.", False )
    scriptDialog.AddControlToGrid( "MachineListBox", "MachineListControl", "", 8, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "LimitGroupLabel", "LabelControl", "Limits", 9, 0, "The Limits that your job requires.", False )
    scriptDialog.AddControlToGrid( "LimitGroupBox", "LimitGroupControl", "", 9, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "DependencyLabel", "LabelControl", "Dependencies", 10, 0, "Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering.", False )
    scriptDialog.AddControlToGrid( "DependencyBox", "DependencyControl", "", 10, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "OnJobCompleteLabel", "LabelControl", "On Job Complete", 11, 0, "If desired, you can automatically archive or delete the job when it completes.", False )
    scriptDialog.AddControlToGrid( "OnJobCompleteBox", "OnJobCompleteControl", "Nothing", 11, 1 )
    scriptDialog.AddSelectionControlToGrid( "SubmitSuspendedBox", "CheckBoxControl", False, "Submit Job As Suspended", 11, 2, "If enabled, the job will submit in the suspended state. This is useful if you don't want the job to start rendering right away. Just resume it from the Monitor when you want it to render." )
    scriptDialog.EndGrid()
    
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator3", "SeparatorControl", "Blender Options", 0, 0, colSpan=3 )

    scriptDialog.AddControlToGrid( "SceneLabel", "LabelControl", "Blender File", 1, 0, "The scene file to be rendered.", False )
    scriptDialog.AddSelectionControlToGrid( "SceneBox", "FileBrowserControl", "", "Blender Files (*.blend);;All Files (*)", 1, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "ChunkSizeLabel", "LabelControl", "Frames Per Task", 4, 0, "This is the number of frames that will be rendered at a time for each job task. ", False )
    scriptDialog.AddRangeControlToGrid( "ChunkSizeBox", "RangeControl", 1, 1, 1000000, 0, 1, 4, 1 , expand=False)
    scriptDialog.AddSelectionControlToGrid("SubmitSceneBox","CheckBoxControl",False,"Submit Blender Scene File With The Job", 4, 2, "If this option is enabled, the scene file will be submitted with the job, and then copied locally to the Worker machine during rendering.")

    scriptDialog.AddControlToGrid( "ThreadsLabel", "LabelControl", "Threads", 5, 0, "The number of threads to use for rendering.", False )
    scriptDialog.AddRangeControlToGrid( "ThreadsBox", "RangeControl", 0, 0, 256, 0, 1, 5, 1, expand=False )

    scriptDialog.EndGrid()
    scriptDialog.EndTabPage()
    
    integration_dialog = IntegrationUI.IntegrationDialog()
    integration_dialog.AddIntegrationTabs( scriptDialog, "BlenderMonitor", DraftRequested, ProjectManagementOptions, failOnNoTabs=False )
    # Add Project Management and Draft Tabs
    
    scriptDialog.EndTabControl()
    
    scriptDialog.AddGrid()
    scriptDialog.AddHorizontalSpacerToGrid( "HSpacer1", 0, 0 )

    submitButton = scriptDialog.AddControlToGrid( "SubmitButton", "ButtonControl", "Submit", 0, 1, expand=False )
    submitButton.ValueModified.connect(SubmitButtonPressed)

    closeButton = scriptDialog.AddControlToGrid( "CloseButton", "ButtonControl", "Close", 0, 2, expand=False )
    # Make sure all the project management connections are closed properly
    closeButton.ValueModified.connect(integration_dialog.CloseProjectManagementConnections)
    closeButton.ValueModified.connect(scriptDialog.closeEvent)

    scriptDialog.EndGrid()
    
    settings = ("DepartmentBox","CategoryBox","PoolBox","SecondaryPoolBox","GroupBox","PriorityBox","MachineLimitBox","IsBlacklistBox","MachineListBox","LimitGroupBox","SceneBox","ChunkSizeBox","ThreadsBox", "SubmitSceneBox")
    scriptDialog.LoadSettings( _get_settings_filename(), settings )
    scriptDialog.EnabledStickySaving( settings, _get_settings_filename() )
    
    appSubmission = False
    if len( args ) > 0:
        appSubmission = True
        
        if args[0] == "":
            scriptDialog.ShowMessageBox( "The Blender scene must be saved before it can be submitted to Deadline.", "Error" )
            return
        
        scriptDialog.SetValue( "SceneBox", args[0] )
        scriptDialog.SetValue( "BatchNameBox", Path.GetFileNameWithoutExtension( args[0] ) )
        
        StatesFile = args[2]
        if StatesFile == "" or not File.Exists( StatesFile ):
            scriptDialog.ShowMessageBox( "The EasyStates scene states file must be specified and exist before it can be submitted to Deadline.", "Error" )
            return
        
        scriptDialog.SetValue( "ThreadsBox", int(args[1]) )            
        scriptDialog.MakeTopMost() # Keep the submission window above all other windows when submitting from another app.

    scriptDialog.ShowDialog( appSubmission )
    
def _get_settings_filename():
    return Path.Combine(ClientUtils.GetUsersSettingsDirectory(),"EasyStatesBlenderSettings.ini")

def SubmitButtonPressed(*args):
    global scriptDialog
    global integration_dialog
            
    # Check if blender files exist.
    sceneFile = scriptDialog.GetValue( "SceneBox" )
    if( not File.Exists( sceneFile ) ):
        scriptDialog.ShowMessageBox( "The Blender file %s does not exist" % sceneFile, "Error" )
        return
    elif (not scriptDialog.GetValue("SubmitSceneBox") and PathUtils.IsPathLocal(sceneFile)):
        result = scriptDialog.ShowMessageBox( "The Blender file %s is local. Are you sure you want to continue?" % sceneFile, "Warning", ("Yes","No") )
        if(result=="No"):
            return
                
    scene_states = []
    with open(StatesFile, 'r') as f:
        scene_states = f.readlines()
    if len(scene_states) == 0:
        scriptDialog.ShowMessageBox( "No scene states were found to render in the EasyStates scene states file %s" % scene_states_file, "Error" )
        return
    
    success = 0
    total = 0
    batch_timestamp = ""
    if scriptDialog.GetValue("IncludeTimestamp"):
        batch_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    for state in scene_states:
        # ['Scene State 2\n', 'Scene State 3\n', 'Scene State 5\n', 'Scene State 6\n']
        # convert to 'Scene State 2', 'Scene State 3', etc
        state_name, frame_list, state_id = state.strip().split("|")

        if state == "":
            continue
        if ";" in state or "," in state or "\t" in state:
            scriptDialog.ShowMessageBox( "The scene state '%s' is not valid. Scene states cannot contain spaces, commas or semicolons." % state, "Error" )
            return
        
        # Create job info file.
        jobInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "blender_job_info.job" )
        writer = StreamWriter( jobInfoFilename, False, Encoding.Unicode )
        writer.WriteLine( "Plugin=BlenderEasyStates" )
        writer.WriteLine( "Name=%s" % state_name )
        writer.WriteLine( "Comment=%s" % scriptDialog.GetValue( "CommentBox" ) )
        writer.WriteLine( "Department=%s" % scriptDialog.GetValue( "DepartmentBox" ) )
        writer.WriteLine( "Pool=%s" % scriptDialog.GetValue( "PoolBox" ) )
        writer.WriteLine( "SecondaryPool=%s" % scriptDialog.GetValue( "SecondaryPoolBox" ) )
        writer.WriteLine( "Group=%s" % scriptDialog.GetValue( "GroupBox" ) )
        writer.WriteLine( "Priority=%s" % scriptDialog.GetValue( "PriorityBox" ) )
        writer.WriteLine( "TaskTimeoutMinutes=%s" % scriptDialog.GetValue( "TaskTimeoutBox" ) )
        writer.WriteLine( "EnableAutoTimeout=%s" % scriptDialog.GetValue( "AutoTimeoutBox" ) )
        writer.WriteLine( "ConcurrentTasks=%s" % scriptDialog.GetValue( "ConcurrentTasksBox" ) )
        writer.WriteLine( "LimitConcurrentTasksToNumberOfCpus=%s" % scriptDialog.GetValue( "LimitConcurrentTasksBox" ) )
        
        writer.WriteLine( "MachineLimit=%s" % scriptDialog.GetValue( "MachineLimitBox" ) )
        if( bool(scriptDialog.GetValue( "IsBlacklistBox" )) ):
            writer.WriteLine( "Blacklist=%s" % scriptDialog.GetValue( "MachineListBox" ) )
        else:
            writer.WriteLine( "Whitelist=%s" % scriptDialog.GetValue( "MachineListBox" ) )
        
        writer.WriteLine( "LimitGroups=%s" % scriptDialog.GetValue( "LimitGroupBox" ) )
        writer.WriteLine( "JobDependencies=%s" % scriptDialog.GetValue( "DependencyBox" ) )
        writer.WriteLine( "OnJobComplete=%s" % scriptDialog.GetValue( "OnJobCompleteBox" ) )
        
        if( bool(scriptDialog.GetValue( "SubmitSuspendedBox" )) ):
            writer.WriteLine( "InitialStatus=Suspended" )
        
        writer.WriteLine( "Frames=%s" % frame_list )
        writer.WriteLine( "ChunkSize=%s" % scriptDialog.GetValue( "ChunkSizeBox" ) )
                
        # Integration
        extraKVPIndex = 0
        if integration_dialog.IntegrationProcessingRequested():
            extraKVPIndex = integration_dialog.WriteIntegrationInfo( writer, extraKVPIndex )

        _batch_name = scriptDialog.GetValue( "BatchNameBox" )
        if batch_timestamp:
            _batch_name += " [" + batch_timestamp + "]"
        
        writer.WriteLine( "BatchName=%s\n" % ( _batch_name ) ) 
        writer.Close()

        # Create plugin info file.
        pluginInfoFilename = Path.Combine( ClientUtils.GetDeadlineTempPath(), "blender_plugin_info.job" )
        writer = StreamWriter( pluginInfoFilename, False, Encoding.Unicode )
        
        if(not scriptDialog.GetValue("SubmitSceneBox")):
            writer.WriteLine("SceneFile=" + sceneFile)
        
        writer.WriteLine( "Threads=%s" % scriptDialog.GetValue( "ThreadsBox" ) )
        writer.WriteLine( "SceneStateID=%s" % state_id )

        writer.Close()
        
        # Setup the command line arguments.
        arguments = StringCollection()
        
        arguments.Add( jobInfoFilename )
        arguments.Add( pluginInfoFilename )
        if scriptDialog.GetValue( "SubmitSceneBox" ):
            arguments.Add( sceneFile )
        
        # Now submit the job.
        results = ClientUtils.ExecuteCommandAndGetOutput( arguments )
        if "The job was submitted successfully" in results:
            success += 1
        total += 1
    
    scriptDialog.ShowMessageBox( "Successfully submitted %d of %d jobs." % (success, total), "Submission Results" )
