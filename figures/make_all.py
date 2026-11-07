"""Render every revision figure, one script at a time (single process, light CPU).

Usage
  python3 figures/make_all.py            # all figures, run from the repository root
  python3 figures/make_all.py fig3 figS9 # a subset
Environment overrides (optional)
  TOPCABG_WORK  analysis work folder (default <repository>/work)
  TOPCABG_FIGS  folder holding fig4_rows.csv and fig6_rows.csv (default <repository>/work)
  TOPCABG_OUT   output folder for the PNGs (default <repository>/figures/out)
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = ["fig_data_only", "figS1", "figS2", "figS3", "fig3", "fig4", "fig5", "fig6", "figS5", "figS6", "figS7", "figS8", "figS9", "figS10",
           "figS11"]


def main(argv):
    todo = [a.removesuffix(".py") for a in argv] or SCRIPTS
    failed = []
    for name in todo:
        path = os.path.join(HERE, f"{name}.py")
        t0 = time.time()
        r = subprocess.run([sys.executable, path], cwd=ROOT, capture_output=True, text=True)
        dt = time.time() - t0
        status = "ok" if r.returncode == 0 else f"FAILED ({r.returncode})"
        print(f"[{status}] {name} in {dt:.1f} s")
        for line in (r.stdout + r.stderr).strip().splitlines():
            print(f"    {line}")
        if r.returncode != 0:
            failed.append(name)
    if failed:
        print("failed: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    try:
        os.nice(10)
    except (AttributeError, OSError):
        pass
    sys.exit(main(sys.argv[1:]))
