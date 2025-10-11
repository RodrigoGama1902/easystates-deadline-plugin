import os
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

def _get_deadline_command() -> str:
    """
    Returns the full path to the DeadlineCommand executable.
    """
    deadline_bin = os.environ.get("DEADLINE_PATH", "")

    # On macOS, fallback to the shared DEADLINE_PATH file if env var is not set
    if not deadline_bin and os.path.exists("/Users/Shared/Thinkbox/DEADLINE_PATH"):
        with open("/Users/Shared/Thinkbox/DEADLINE_PATH", "r") as f:
            deadline_bin = f.read().strip()

    if not deadline_bin:
        raise FileNotFoundError("Deadline path not found. Set DEADLINE_PATH environment variable.")

    return os.path.join(deadline_bin, "deadlinecommand")


def _get_repository_file_path(subdir: Optional[str] = None) -> str:
    """
    Returns the repository path for a given subdir using DeadlineCommand.
    """
    deadline_command = _get_deadline_command()

    args = [deadline_command, "-GetRepositoryFilePath"]
    if subdir:
        args.append(subdir)

    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Close unused pipes
    proc.stdin.close() # type: ignore
    proc.stderr.close() # type: ignore

    output = proc.stdout.read() # type: ignore
    path = output.decode("utf-8").strip().replace("\\", "/")
    return path


def submit_easystate_render(
    blend_file: str,
    scene_states_file: Path,
    datetime_override : datetime,
) -> None:
    """
    Submit the given Blender scene and EasyStates file to Deadline.
    
    Args:
        blend_file (str): Path to the .blend file.
        scene_states_file (Path): Path to the temporary text file containing scene states.
        datetime_override (datetime): Datetime to override <datetime> and <session_datetime> tags in output paths.
    """
    _script_file = _get_repository_file_path("scripts/Submission/BlenderEasyStatesSubmission.py")
    args = [
        _get_deadline_command(),
        "-ExecuteScript",
        _script_file,
        blend_file,
        str(scene_states_file),
        str(datetime_override.isoformat())
    ]
    subprocess.Popen(args)
