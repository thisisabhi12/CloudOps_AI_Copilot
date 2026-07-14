"""
CloudOps AI Copilot — Backend Syntax & Structure Checker

Validates all Python files for syntax errors and structure issues
without requiring external dependencies.
"""

import sys
import ast
from pathlib import Path
from typing import List, Tuple

def check_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """
    Check if a Python file has valid syntax.
    
    Returns: (is_valid, error_message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def check_imports_structure(file_path: Path) -> List[str]:
    """
    Extract import statements to check for obvious import issues.
    Returns list of imported modules.
    """
    imports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except:
        pass
    
    return imports


def get_all_python_files(root_dir: Path) -> List[Path]:
    """Get all Python files in the app directory."""
    return sorted(root_dir.glob("app/**/*.py"))


def main():
    """Run all checks."""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    
    print("\n" + "=" * 70)
    print("CloudOps AI Copilot — Backend Syntax & Structure Check")
    print("=" * 70 + "\n")
    
    # Check all Python files
    python_files = get_all_python_files(backend_dir)
    
    print(f"Found {len(python_files)} Python files in app/\n")
    
    syntax_errors = []
    valid_files = []
    
    print("Checking syntax...\n")
    
    for file_path in python_files:
        relative_path = file_path.relative_to(backend_dir)
        is_valid, error_msg = check_python_syntax(file_path)
        
        if is_valid:
            valid_files.append(file_path)
            print(f"✓ {relative_path}")
        else:
            syntax_errors.append((relative_path, error_msg))
            print(f"✗ {relative_path}")
            print(f"  └─ {error_msg}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {len(valid_files)} valid, {len(syntax_errors)} errors")
    print("=" * 70)
    
    if syntax_errors:
        print("\nSyntax Errors Found:")
        for file_path, error in syntax_errors:
            print(f"\n  {file_path}")
            print(f"    {error}")
        return False
    else:
        print("\n✓ All Python files have valid syntax!\n")
    
    # Check for common structure issues
    print("\n" + "=" * 70)
    print("Checking Module Structure...")
    print("=" * 70 + "\n")
    
    structure_check = {
        "app/__init__.py": "Package init",
        "app/main.py": "FastAPI application entry point",
        "app/config.py": "Configuration module",
        "app/database.py": "Database setup",
        "app/api/auth.py": "Auth endpoints",
        "app/api/chat.py": "Chat endpoints",
        "app/api/review.py": "Review endpoints",
        "app/api/health.py": "Health endpoint",
        "app/models/user.py": "User model",
        "app/models/chat.py": "Chat models",
        "app/services/auth_service.py": "Auth service",
        "app/services/ai_provider.py": "AI provider",
        "app/services/chat_service.py": "Chat service",
        "app/services/review_engine.py": "Review engine",
        "app/schemas/auth.py": "Auth schemas",
        "app/schemas/chat.py": "Chat schemas",
        "app/schemas/review.py": "Review schemas",
    }
    
    missing_files = []
    for file_rel_path, description in structure_check.items():
        file_path = backend_dir / file_rel_path
        if file_path.exists():
            print(f"✓ {file_rel_path:<35} ({description})")
        else:
            print(f"✗ {file_rel_path:<35} (MISSING)")
            missing_files.append(file_rel_path)
    
    print("\n" + "=" * 70)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} expected files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("\n✓ All expected files are present!\n")
    
    # Check requirements
    print("=" * 70)
    print("Checking requirements.txt...")
    print("=" * 70 + "\n")
    
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file) as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        print(f"Found {len(requirements)} dependencies:\n")
        for req in requirements[:10]:
            print(f"  • {req}")
        if len(requirements) > 10:
            print(f"  ... and {len(requirements) - 10} more")
        print()
    else:
        print("⚠️  requirements.txt not found\n")
    
    print("=" * 70)
    print("✓ Backend structure check complete!")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
