import bpy
import os
import subprocess
from pathlib import Path
from typing import Optional


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
    scene: bpy.types.Scene,
    scene_file: str,
    scene_states_file: Path,
) -> None:
    """
    Submit the given Blender scene and EasyStates file to Deadline.
    """
    script_file = _get_repository_file_path("scripts/Submission/BlenderEasyStatesSubmission.py")
    render_settings = scene.render
    threads = 0 if render_settings.threads_mode == 'AUTO' else render_settings.threads

    args = [
        _get_deadline_command(),
        "-ExecuteScript",
        script_file,
        scene_file,
        str(threads),
        str(scene_states_file),
    ]

    subprocess.Popen(args)
