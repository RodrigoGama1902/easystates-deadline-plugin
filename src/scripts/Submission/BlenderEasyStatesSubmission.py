from System import *
from System.Collections.Specialized import *
from System.IO import *
from System.Text import *

from Deadline.Scripting import *

from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog
from datetime import datetime

# ========================================================================
## Globals
# ========================================================================
script_dialog = None
settings = None
states_file = None

def __main__(*args):
    """Entry point of the script. Called by Deadline."""
    global script_dialog
    global settings
    global states_file

    script_dialog = DeadlineScriptDialog()
    script_dialog.SetTitle("Submit EasyStates Blender Batch To Deadline")
    script_dialog.SetIcon(script_dialog.GetIcon('BlenderEasyStates'))
    
    script_dialog.AddTabControl("Tabs", 0, 0)
    
    script_dialog.AddTabPage("Batch Options")
    script_dialog.AddGrid()
    script_dialog.AddControlToGrid("Separator1", "SeparatorControl", "Batch Description", 0, 0, colSpan=2)

    script_dialog.AddControlToGrid("NameLabel", "LabelControl", "Batch Name", 1, 0,
        "The name of your job. This is optional, and if left blank, it will default to 'Untitled'.", False)
    script_dialog.AddControlToGrid("BatchNameBox", "TextControl", "Untitled", 1, 1)
    script_dialog.AddSelectionControlToGrid("IncludeTimestamp", "CheckBoxControl", True, "Include Timestamp", 1, 2,
        "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job.")

    script_dialog.AddControlToGrid("CommentLabel", "LabelControl", "Comment", 2, 0,
        "A simple description of your job. This is optional and can be left blank. (Will be applied to all jobs in the batch)", False)
    script_dialog.AddControlToGrid("CommentBox", "TextControl", "", 2, 1)

    script_dialog.AddControlToGrid("DepartmentLabel", "LabelControl", "Department", 3, 0,
        "The department you belong to. This is optional and can be left blank. (Will be applied to all jobs in the batch)", False)
    script_dialog.AddControlToGrid("DepartmentBox", "TextControl", "", 3, 1)
    script_dialog.EndGrid()

    script_dialog.AddGrid()
    script_dialog.AddControlToGrid("Separator2", "SeparatorControl", "Job Options", 0, 0, colSpan=3)

    script_dialog.AddControlToGrid("PoolLabel", "LabelControl", "Pool", 1, 0, "The pool that your job will be submitted to.", False)
    script_dialog.AddControlToGrid("PoolBox", "PoolComboControl", "none", 1, 1)

    script_dialog.AddControlToGrid("SecondaryPoolLabel", "LabelControl", "Secondary Pool", 2, 0,
        "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Workers.", False)
    script_dialog.AddControlToGrid("SecondaryPoolBox", "SecondaryPoolComboControl", "", 2, 1)

    script_dialog.AddControlToGrid("GroupLabel", "LabelControl", "Group", 3, 0, "The group that your job will be submitted to.", False)
    script_dialog.AddControlToGrid("GroupBox", "GroupComboControl", "none", 3, 1)

    script_dialog.AddControlToGrid("PriorityLabel", "LabelControl", "Priority", 4, 0,
        "A job can have a numeric priority ranging from 0 to 100, where 0 is the lowest priority and 100 is the highest priority.", False)
    script_dialog.AddRangeControlToGrid("PriorityBox", "RangeControl", RepositoryUtils.GetMaximumPriority() / 2, 0,
        RepositoryUtils.GetMaximumPriority(), 0, 1, 4, 1)

    script_dialog.AddControlToGrid("TaskTimeoutLabel", "LabelControl", "Task Timeout", 5, 0,
        "The number of minutes a Worker has to render a task for this job before it requeues it. Specify 0 for no limit.", False)
    script_dialog.AddRangeControlToGrid("TaskTimeoutBox", "RangeControl", 0, 0, 1000000, 0, 1, 5, 1)
    script_dialog.AddSelectionControlToGrid("AutoTimeoutBox", "CheckBoxControl", False, "Enable Auto Task Timeout", 5, 2,
        "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job.")

    script_dialog.AddControlToGrid("ConcurrentTasksLabel", "LabelControl", "Concurrent Tasks", 6, 0,
        "The number of tasks that can render concurrently on a single Worker.", False)
    script_dialog.AddRangeControlToGrid("ConcurrentTasksBox", "RangeControl", 1, 1, 16, 0, 1, 6, 1)
    script_dialog.AddSelectionControlToGrid("LimitConcurrentTasksBox", "CheckBoxControl", True, "Limit Tasks To Worker's Task Limit", 6, 2)

    script_dialog.AddControlToGrid("MachineLimitLabel", "LabelControl", "Machine Limit", 7, 0,
        "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit.", False)
    script_dialog.AddRangeControlToGrid("MachineLimitBox", "RangeControl", 0, 0, 1000000, 0, 1, 7, 1)
    script_dialog.AddSelectionControlToGrid("IsBlacklistBox", "CheckBoxControl", False, "Machine List Is A Deny List", 7, 2)

    script_dialog.AddControlToGrid("MachineListLabel", "LabelControl", "Machine List", 8, 0, "The list of machines on the deny/allow list.", False)
    script_dialog.AddControlToGrid("MachineListBox", "MachineListControl", "", 8, 1, colSpan=2)

    script_dialog.AddControlToGrid("LimitGroupLabel", "LabelControl", "Limits", 9, 0, "The Limits that your job requires.", False)
    script_dialog.AddControlToGrid("LimitGroupBox", "LimitGroupControl", "", 9, 1, colSpan=2)

    script_dialog.AddControlToGrid("DependencyLabel", "LabelControl", "Dependencies", 10, 0,
        "Specify existing jobs that this job will be dependent on.", False)
    script_dialog.AddControlToGrid("DependencyBox", "DependencyControl", "", 10, 1, colSpan=2)

    script_dialog.AddControlToGrid("OnJobCompleteLabel", "LabelControl", "On Job Complete", 11, 0, "Auto archive/delete job.", False)
    script_dialog.AddControlToGrid("OnJobCompleteBox", "OnJobCompleteControl", "Nothing", 11, 1)
    script_dialog.AddSelectionControlToGrid("SubmitSuspendedBox", "CheckBoxControl", False, "Submit Job As Suspended", 11, 2)
    script_dialog.EndGrid()
    
    script_dialog.AddGrid()
    script_dialog.AddControlToGrid("Separator3", "SeparatorControl", "Blender Options", 0, 0, colSpan=3)

    script_dialog.AddControlToGrid("BlendFileLabel", "LabelControl", "Blender File", 1, 0, "The blend file to be rendered.", False)
    script_dialog.AddSelectionControlToGrid("BlendFileBox", "FileBrowserControl", "", "Blender Files (*.blend);;All Files (*)", 1, 1, colSpan=2)

    script_dialog.AddControlToGrid("ChunkSizeLabel", "LabelControl", "Frames Per Task", 4, 0, "Frames rendered per task.", False)
    script_dialog.AddRangeControlToGrid("ChunkSizeBox", "RangeControl", 1, 1, 1000000, 0, 1, 4, 1, expand=False)
    script_dialog.AddSelectionControlToGrid("SubmitBlendFileBox", "CheckBoxControl", False, "Submit Blender File With The Job", 4, 2)

    script_dialog.EndGrid()
    script_dialog.EndTabPage()
    
    script_dialog.EndTabControl()
    
    script_dialog.AddGrid()
    script_dialog.AddHorizontalSpacerToGrid("HSpacer1", 0, 0)

    submit_button = script_dialog.AddControlToGrid("SubmitButton", "ButtonControl", "Submit", 0, 1, expand=False)
    submit_button.ValueModified.connect(_submit_button_pressed)

    close_button = script_dialog.AddControlToGrid("CloseButton", "ButtonControl", "Close", 0, 2, expand=False)
    close_button.ValueModified.connect(script_dialog.closeEvent)

    script_dialog.EndGrid()
    
    settings = ("DepartmentBox","CategoryBox","PoolBox","SecondaryPoolBox","GroupBox","PriorityBox",
                "MachineLimitBox","IsBlacklistBox","MachineListBox","LimitGroupBox","BlendFileBox",
                "ChunkSizeBox", "SubmitBlendFileBox")
    script_dialog.LoadSettings(_get_settings_filename(), settings)
    script_dialog.EnabledStickySaving(settings, _get_settings_filename())
    
    app_submission = False
    if len(args) > 0:
        app_submission = True
        
        script_dialog.SetValue("BlendFileBox", args[0])
        script_dialog.SetValue("BatchNameBox", Path.GetFileNameWithoutExtension(args[0]))
        
        states_file = args[1]
        if states_file == "" or not File.Exists(states_file):
            script_dialog.ShowMessageBox("The EasyStates scene states file must be specified and exist before it can be submitted.", "Error")
            return
        
        script_dialog.MakeTopMost()

    script_dialog.ShowDialog(app_submission)

def _get_settings_filename():
    return Path.Combine(ClientUtils.GetUsersSettingsDirectory(), "EasyStatesBlenderSettings.ini")

def _submit_button_pressed(*args):
    global script_dialog
    global states_file
            
    scene_file = script_dialog.GetValue("BlendFileBox")
    if not File.Exists(scene_file):
        script_dialog.ShowMessageBox("The Blender file %s does not exist" % scene_file, "Error")
        return
    elif (not script_dialog.GetValue("SubmitBlendFileBox") and PathUtils.IsPathLocal(scene_file)):
        result = script_dialog.ShowMessageBox("The Blender file %s is local. Continue?" % scene_file, "Warning", ("Yes","No"))
        if result == "No":
            return
                
    scene_states = []
    with open(states_file, 'r') as f:
        scene_states = f.readlines()
    if len(scene_states) == 0:
        script_dialog.ShowMessageBox("No scene states found in file %s" % states_file, "Error")
        return
    
    success = 0
    total = 0
    batch_timestamp = ""
    if script_dialog.GetValue("IncludeTimestamp"):
        batch_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    for state in scene_states:
        state_name, frame_list, state_id = state.strip().split("|")

        if state == "":
            continue
        if ";" in state or "," in state or "\t" in state:
            script_dialog.ShowMessageBox("The scene state '%s' is not valid." % state, "Error")
            return
        
        job_info_filename = Path.Combine(ClientUtils.GetDeadlineTempPath(), "blender_job_info.job")
        writer = StreamWriter(job_info_filename, False, Encoding.Unicode)
        writer.WriteLine("Plugin=BlenderEasyStates")
        writer.WriteLine("Name=%s" % state_name)
        writer.WriteLine("Comment=%s" % script_dialog.GetValue("CommentBox"))
        writer.WriteLine("Department=%s" % script_dialog.GetValue("DepartmentBox"))
        writer.WriteLine("Pool=%s" % script_dialog.GetValue("PoolBox"))
        writer.WriteLine("SecondaryPool=%s" % script_dialog.GetValue("SecondaryPoolBox"))
        writer.WriteLine("Group=%s" % script_dialog.GetValue("GroupBox"))
        writer.WriteLine("Priority=%s" % script_dialog.GetValue("PriorityBox"))
        writer.WriteLine("TaskTimeoutMinutes=%s" % script_dialog.GetValue("TaskTimeoutBox"))
        writer.WriteLine("EnableAutoTimeout=%s" % script_dialog.GetValue("AutoTimeoutBox"))
        writer.WriteLine("ConcurrentTasks=%s" % script_dialog.GetValue("ConcurrentTasksBox"))
        writer.WriteLine("LimitConcurrentTasksToNumberOfCpus=%s" % script_dialog.GetValue("LimitConcurrentTasksBox"))
        
        writer.WriteLine("MachineLimit=%s" % script_dialog.GetValue("MachineLimitBox"))
        if bool(script_dialog.GetValue("IsBlacklistBox")):
            writer.WriteLine("Blacklist=%s" % script_dialog.GetValue("MachineListBox"))
        else:
            writer.WriteLine("Whitelist=%s" % script_dialog.GetValue("MachineListBox"))
        
        writer.WriteLine("LimitGroups=%s" % script_dialog.GetValue("LimitGroupBox"))
        writer.WriteLine("JobDependencies=%s" % script_dialog.GetValue("DependencyBox"))
        writer.WriteLine("OnJobComplete=%s" % script_dialog.GetValue("OnJobCompleteBox"))
        
        if bool(script_dialog.GetValue("SubmitSuspendedBox")):
            writer.WriteLine("InitialStatus=Suspended")
        
        writer.WriteLine("Frames=%s" % frame_list)
        writer.WriteLine("ChunkSize=%s" % script_dialog.GetValue("ChunkSizeBox"))
                
        batch_name = script_dialog.GetValue("BatchNameBox")
        if batch_timestamp:
            batch_name += " [" + batch_timestamp + "]"
        
        writer.WriteLine("BatchName=%s\n" % (batch_name))
        writer.Close()

        plugin_info_filename = Path.Combine(ClientUtils.GetDeadlineTempPath(), "blender_plugin_info.job")
        writer = StreamWriter(plugin_info_filename, False, Encoding.Unicode)
        
        if not script_dialog.GetValue("SubmitBlendFileBox"):
            writer.WriteLine("SceneFile=" + scene_file)
        
        writer.WriteLine("SceneStateID=%s" % state_id)
        writer.Close()
        
        arguments = StringCollection()
        arguments.Add(job_info_filename)
        arguments.Add(plugin_info_filename)
        if script_dialog.GetValue("SubmitBlendFileBox"):
            arguments.Add(scene_file)
        
        results = ClientUtils.ExecuteCommandAndGetOutput(arguments)
        if "The job was submitted successfully" in results:
            success += 1
        total += 1
    
    script_dialog.ShowMessageBox("Successfully submitted %d of %d jobs." % (success, total), "Submission Results")
