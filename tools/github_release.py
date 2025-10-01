import logging
import os

from github import Github, GithubException, Auth
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GITHUB_REPO = "rodrigogama1902/easystates-deadline-plugin"
RELEASE_VERSION = "v0.0.1"
OVERWRITE_RELEASE = True
PRE_RELEASE = False

USE_RELEASE_NOTES_FILE = True
RELEASE_NOTES_STRING = ""

USE_CHANGELOG_FILE = False
CHANGELOG_STRING = ""

RELEASE_TOKEN = os.getenv("GITHUB_TOKEN", "")
PROJECT_ROOT = Path(__file__).parent.parent

def _find_file_with_stem(stem: str, directory: Path) -> Path | None:
    """Find a file with a given stem in a directory"""

    for filename in directory.iterdir():
        if filename.stem.lower() == stem.lower():
            return filename

    return None

def _get_release_notes_string() -> str:
    if not USE_RELEASE_NOTES_FILE:
        return RELEASE_NOTES_STRING

    release_notes_path = _find_file_with_stem(
        "release_notes", PROJECT_ROOT
    )

    if release_notes_path is None:
        raise Exception("Release Notes file not found in the project root")

    with open(release_notes_path, "r") as f:
        return f.read()

def _get_changelog_string() -> str:
    if not USE_CHANGELOG_FILE:
        return CHANGELOG_STRING

    changelog_path = _find_file_with_stem(
        "changelog", PROJECT_ROOT
    )

    if changelog_path is None:
        raise Exception("Changelog file not found in the project root")

    with open(changelog_path, "r") as f:
        return f.read()

def _delete_github_release() -> None:
    """Delete the release in your GitHub repository
    Ensure you have a valid GitHub token set in the environment"""
    
    auth = Auth.Token(RELEASE_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(GITHUB_REPO)

    release = repo.get_release(RELEASE_VERSION)
    release.delete_release()

    logging.info(f"Delete GitHub Release at: {release.html_url}")
    
def _generate_release_message() -> str:
    release_notes = _get_release_notes_string()
    changelog = _get_changelog_string()

    if not release_notes and not changelog:
        return ""

    message = f""

    if release_notes:
        message += f"\n\n{release_notes}\n\n"
    if changelog:
        message += f"**Changelog**:\n\n{changelog}\n\n"

    return message

def create_github_release(release_asset: Path) -> bool:
    """Tag the release in your GitHub repository
    Ensure you have a valid GitHub token set in the environment
    """
    #g = Github(RELEASE_TOKEN)
    
    auth = Auth.Token(RELEASE_TOKEN)
    g = Github(auth=auth)

    try:
        repo = g.get_repo(GITHUB_REPO)
    except GithubException as e:
        logging.error(e)
        logging.info("Aborting GitHub release.")
        return False

    try:
        repo.get_release(RELEASE_VERSION)
        if OVERWRITE_RELEASE:
            logging.warning(
                f"Release {RELEASE_VERSION} already exists in GitHub repository. Overwriting."
            )
            _delete_github_release()
        else:
            raise Exception(
                f"Release {RELEASE_VERSION} already exists in GitHub repository."
            )
    except GithubException as e:
        if e.status == 404:
            pass
        else:
            raise e

    release = repo.create_git_release(
        tag=RELEASE_VERSION,
        name=f"Release {RELEASE_VERSION}",
        message=_generate_release_message(),
        draft=False,
        prerelease=PRE_RELEASE,
    )

    release.upload_asset(
        release_asset.as_posix(),
        label=release_asset.name,
        content_type="application/zip",
    )

    logging.info(f"Generate GitHub Release at: {release.html_url}")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dist_path = PROJECT_ROOT / "release" / "easystates_deadline_plugin.zip"
    if not dist_path.exists():
        raise Exception(f"Distribution file not found at: {dist_path}")

    create_github_release(dist_path)