from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


root = Path.cwd()
hidden = (
    collect_submodules("moe_autopilot_studio")
    + collect_submodules("fastapi")
    + collect_submodules("uvicorn")
)

a = Analysis(
    [str(root / "src" / "moe_autopilot_studio" / "launcher.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[
        (str(root / "frontend" / "dist"), "moe_autopilot_studio/static"),
        (str(root / "fixtures"), "fixtures"),
        (str(root / "README.md"), "."),
        (str(root / "LICENSE"), "."),
        (str(root / "NOTICE"), "."),
    ],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MoEAutopilotStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="MoEAutopilotStudio",
)
