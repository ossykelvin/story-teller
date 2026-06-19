import json
import shutil
from pathlib import Path
from typing import Any
from core.config import LOCAL_STORAGE_PATH, EXPORT_STORAGE_PATH, ensure_dirs
from core.utils import slugify, now_iso

PROJECTS_DIR = LOCAL_STORAGE_PATH / "projects"

DEFAULT_STORY_BIBLE = {
    "characters": [],
    "locations": [],
    "timeline": [],
    "plot_points": [],
    "themes": [],
    "world_rules": [],
    "objects": [],
    "relationships": [],
    "unresolved_threads": [],
    "chapter_summaries": [],
    "glossary": []
}


def read_json(path: Path, fallback: Any):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def list_projects(username: str) -> list[dict]:
    ensure_dirs()
    projects = []
    for project_file in PROJECTS_DIR.glob("*/project.json"):
        project = read_json(project_file, {})
        if project and project.get("owner") == username:
            project["_path"] = str(project_file.parent)
            projects.append(project)
    return sorted(projects, key=lambda p: p.get("updated_at", ""), reverse=True)


def create_project(username: str, payload: dict) -> dict:
    ensure_dirs()
    slug = slugify(payload.get("title", "untitled"))
    project_dir = PROJECTS_DIR / f"{slug}-{now_iso().replace(':','').replace('-','')[:15]}"
    project_dir.mkdir(parents=True, exist_ok=True)
    project = {
        "id": project_dir.name,
        "owner": username,
        "title": payload.get("title", "Untitled Project"),
        "project_type": payload.get("project_type", "novel"),
        "fiction_type": payload.get("fiction_type", "fiction"),
        "genre": payload.get("genre", "Fantasy"),
        "theme": payload.get("theme", ""),
        "style_label": payload.get("style_label", ""),
        "safe_style_profile": payload.get("safe_style_profile", ""),
        "custom_style": payload.get("custom_style", ""),
        "target_word_count": payload.get("target_word_count", 3000),
        "chapter_count": payload.get("chapter_count", 1),
        "current_chapter": 1,
        "status": "idea",
        "seed_prompt": payload.get("seed_prompt", ""),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    write_json(project_dir / "project.json", project)
    write_json(project_dir / "outline.json", {"content": "", "approved": False, "created_at": ""})
    write_json(project_dir / "story_bible.json", DEFAULT_STORY_BIBLE)
    write_json(project_dir / "chapters.json", [])
    write_json(project_dir / "continuity_log.json", [])
    write_json(project_dir / "qa_reports.json", [])
    write_json(project_dir / "custom_style.json", {"profiles": []})
    (project_dir / "exports").mkdir(exist_ok=True)
    (project_dir / "assets").mkdir(exist_ok=True)
    return project


def project_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id


def load_project_bundle(project_id: str) -> dict:
    p = project_dir(project_id)
    return {
        "project": read_json(p / "project.json", {}),
        "outline": read_json(p / "outline.json", {"content": "", "approved": False}),
        "story_bible": read_json(p / "story_bible.json", DEFAULT_STORY_BIBLE),
        "chapters": read_json(p / "chapters.json", []),
        "continuity_log": read_json(p / "continuity_log.json", []),
        "qa_reports": read_json(p / "qa_reports.json", []),
        "custom_style": read_json(p / "custom_style.json", {"profiles": []}),
    }


def save_project(project_id: str, data: dict) -> None:
    p = project_dir(project_id)
    project = data.get("project", {})
    project["updated_at"] = now_iso()
    write_json(p / "project.json", project)
    for name in ["outline", "story_bible", "chapters", "continuity_log", "qa_reports", "custom_style"]:
        if name in data:
            write_json(p / f"{name}.json", data[name])


def delete_project(project_id: str) -> None:
    p = project_dir(project_id)
    if p.exists():
        shutil.rmtree(p)
