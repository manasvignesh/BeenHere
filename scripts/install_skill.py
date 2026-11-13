#!/usr/bin/env python3
"""
scripts/install_skill.py - Installation Utility for BeenHere Agent Skill

Installs BeenHere into Claude Code (.claude/skills/beenhere) and/or
OpenAI Codex (.agents/skills/beenhere) for project-local or user-global use.

Usage:
    python scripts/install_skill.py [--target-dir PATH] [--agent {claude,codex,all}] [--global] [--mode {copy,symlink}]
    python scripts/install_skill.py --uninstall [--target-dir PATH] [--agent {claude,codex,all}] [--global]
"""

import os
import sys
import shutil
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


PAYLOAD_FILES = ["SKILL.md", "LICENSE"]
PAYLOAD_DIRS = ["scripts", "references", "templates"]


def resolve_install_paths(
    target_dir: str,
    agent: str,
    is_global: bool
) -> List[Tuple[str, Path]]:
    """Determine destination paths for selected agents."""
    if is_global:
        base_dir = Path.home()
    else:
        base_dir = Path(target_dir).resolve()
        
    paths = []
    if agent in ("claude", "all"):
        paths.append(("Claude Code", base_dir / ".claude" / "skills" / "beenhere"))
    if agent in ("codex", "all"):
        paths.append(("OpenAI Codex", base_dir / ".agents" / "skills" / "beenhere"))
        
    return paths


def copy_payload(source_root: Path, dest_dir: Path) -> List[str]:
    """Copy skill payload files and directories to destination."""
    installed_items = []
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy root payload files
    for fname in PAYLOAD_FILES:
        src_file = source_root / fname
        if src_file.exists():
            shutil.copy2(src_file, dest_dir / fname)
            installed_items.append(fname)
            
    # Copy payload directories
    for dname in PAYLOAD_DIRS:
        src_sub = source_root / dname
        dest_sub = dest_dir / dname
        if src_sub.exists():
            if dest_sub.exists():
                shutil.rmtree(dest_sub)
            shutil.copytree(src_sub, dest_sub)
            installed_items.append(f"{dname}/")
            
    return installed_items


def symlink_payload(source_root: Path, dest_dir: Path) -> str:
    """Create a symlink or junction pointing to source_root."""
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists() or dest_dir.is_symlink():
        if dest_dir.is_dir() and not dest_dir.is_symlink():
            shutil.rmtree(dest_dir)
        else:
            dest_dir.unlink()
            
    # Use junction on Windows if symlink privileges are restricted
    try:
        dest_dir.symlink_to(source_root, target_is_directory=True)
        return "symlink"
    except OSError:
        # Fall back to copy if symlinks are not permitted by OS policy
        copy_payload(source_root, dest_dir)
        return "copied (symlink fallback)"


def uninstall_skill(target_paths: List[Tuple[str, Path]], dry_run: bool = False) -> List[Dict[str, Any]]:
    """Remove installed skill from paths."""
    actions = []
    for agent_name, path in target_paths:
        status = "not_found"
        if path.exists() or path.is_symlink():
            if not dry_run:
                if path.is_symlink() or path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                status = "removed"
            else:
                status = "would_remove"
        actions.append({"agent": agent_name, "path": str(path), "status": status})
    return actions


def install_skill(
    source_root: Path,
    target_paths: List[Tuple[str, Path]],
    mode: str = "copy",
    dry_run: bool = False
) -> List[Dict[str, Any]]:
    """Install skill payload into target paths."""
    actions = []
    for agent_name, dest_path in target_paths:
        if dry_run:
            actions.append({
                "agent": agent_name,
                "path": str(dest_path),
                "mode": mode,
                "status": "would_install"
            })
            continue
            
        try:
            if mode == "symlink":
                res_mode = symlink_payload(source_root, dest_path)
                actions.append({
                    "agent": agent_name,
                    "path": str(dest_path),
                    "mode": res_mode,
                    "status": "installed"
                })
            else:
                items = copy_payload(source_root, dest_path)
                actions.append({
                    "agent": agent_name,
                    "path": str(dest_path),
                    "mode": "copy",
                    "items": items,
                    "status": "installed"
                })
        except Exception as exc:
            actions.append({
                "agent": agent_name,
                "path": str(dest_path),
                "mode": mode,
                "status": "error",
                "error": str(exc)
            })
            
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BeenHere Agent Skill Installer (Claude Code & OpenAI Codex)"
    )
    parser.add_argument(
        "--target-dir", "-t",
        default=".",
        help="Target project directory (defaults to current directory)"
    )
    parser.add_argument(
        "--agent", "-a",
        choices=["claude", "codex", "all"],
        default="all",
        help="Target AI coding agent environment (default: all)"
    )
    parser.add_argument(
        "--global", "-g",
        dest="is_global",
        action="store_true",
        help="Install to user home directory (~/.claude or ~/.agents) instead of target directory"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["copy", "symlink"],
        default="copy",
        help="Installation mode: copy (default, robust) or symlink"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall BeenHere from target location"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what actions would be performed without modifying disk"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON results"
    )
    args = parser.parse_args()

    # Determine source root where BeenHere repository lives
    source_root = Path(__file__).resolve().parent.parent
    if not (source_root / "SKILL.md").exists():
        print(f"Error: Unable to locate canonical SKILL.md in {source_root}", file=sys.stderr)
        return 1

    target_paths = resolve_install_paths(args.target_dir, args.agent, args.is_global)

    if args.uninstall:
        actions = uninstall_skill(target_paths, dry_run=args.dry_run)
    else:
        actions = install_skill(source_root, target_paths, mode=args.mode, dry_run=args.dry_run)

    if args.json:
        print(json.dumps({"success": True, "actions": actions}, indent=2))
    else:
        action_verb = "Uninstalling" if args.uninstall else "Installing"
        mode_str = f" [mode: {args.mode}]" if not args.uninstall else ""
        dry_str = " (DRY RUN)" if args.dry_run else ""
        scope_str = "Globally" if args.is_global else f"in {Path(args.target_dir).resolve()}"
        print(f"=== {action_verb} BeenHere Skill {scope_str}{mode_str}{dry_str} ===")
        for act in actions:
            status_icon = "✓" if act["status"] in ("installed", "removed") else ("•" if "would" in act["status"] else "✗")
            print(f" {status_icon} {act['agent']}: {act['path']} -> {act['status']}")
            if "error" in act:
                print(f"   [ERROR] {act['error']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
