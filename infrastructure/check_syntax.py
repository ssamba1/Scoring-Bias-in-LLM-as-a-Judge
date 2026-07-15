"""Quick syntax check of all .py files in the project."""
import os
import sys
import compileall

root = os.path.dirname(os.path.abspath(__file__))
exclude = ['.git', '__pycache__']

success, failures = compileall.compile_dir(
    root,
    force=True,
    quiet=0,
    rx=re.compile(r'[/\\](\.git|__pycache__)[/\\]') if __import__('re') else None,
    workers=0,
)

print(f"\n{'='*50}")
print(f"Syntax check complete: {'ALL PASSED' if success else 'SOME FAILURES'}")
print(f"{'='*50}")
