import sys
import traceback
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from dev.syntax.C_Syntax import parse_file


try:
    parse_file()
    print("ok")
except Exception:
    traceback.print_exc()
