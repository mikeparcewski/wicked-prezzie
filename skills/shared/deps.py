"""Dependency detection and auto-installation for wicked-prezzie.

Checks for required external tools and installs them if missing,
using the appropriate package manager for the current platform.
"""

import os
import platform
import shutil
import subprocess
import sys


def _is_macos():
    return platform.system() == "Darwin"


def _is_linux():
    return platform.system() == "Linux"


def _has_brew():
    return shutil.which("brew") is not None


def _has_apt():
    return shutil.which("apt-get") is not None


def _run_install(cmd, name):
    """Run an install command, printing progress."""
    print(f"  Installing {name}...")
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr.strip()}", file=sys.stderr)
        return False
    print(f"  {name} installed successfully.")
    return True


def _find_soffice():
    """Find soffice binary across platforms."""
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if os.path.exists(p):
            return p

    linux_paths = [
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ]
    for p in linux_paths:
        if os.path.exists(p):
            return p

    return None


def ensure_libreoffice():
    """Ensure LibreOffice is installed. Install if missing.

    Returns:
        Path to soffice binary.

    Raises:
        RuntimeError if installation fails or platform unsupported.
    """
    soffice = _find_soffice()
    if soffice:
        return soffice

    print("\n  LibreOffice not found — required for PPTX rendering.")

    if _is_macos() and _has_brew():
        if _run_install(["brew", "install", "--cask", "libreoffice"], "LibreOffice"):
            soffice = _find_soffice()
            if soffice:
                return soffice

    elif _is_linux() and _has_apt():
        if _run_install(["sudo", "apt-get", "install", "-y", "libreoffice-impress"], "LibreOffice Impress"):
            soffice = _find_soffice()
            if soffice:
                return soffice

    raise RuntimeError(
        "Could not install LibreOffice automatically.\n"
        "Install manually:\n"
        "  macOS:   brew install --cask libreoffice\n"
        "  Ubuntu:  sudo apt install libreoffice-impress\n"
        "  Windows: https://www.libreoffice.org/download/"
    )


def ensure_pdftoppm():
    """Ensure pdftoppm (poppler) is installed. Install if missing.

    Returns:
        Path to pdftoppm binary.

    Raises:
        RuntimeError if installation fails or platform unsupported.
    """
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        return pdftoppm

    print("\n  pdftoppm not found — required for PDF-to-PNG conversion.")

    if _is_macos() and _has_brew():
        if _run_install(["brew", "install", "poppler"], "poppler"):
            pdftoppm = shutil.which("pdftoppm")
            if pdftoppm:
                return pdftoppm

    elif _is_linux() and _has_apt():
        if _run_install(["sudo", "apt-get", "install", "-y", "poppler-utils"], "poppler-utils"):
            pdftoppm = shutil.which("pdftoppm")
            if pdftoppm:
                return pdftoppm

    raise RuntimeError(
        "Could not install poppler automatically.\n"
        "Install manually:\n"
        "  macOS:  brew install poppler\n"
        "  Ubuntu: sudo apt install poppler-utils"
    )


def ensure_chrome():
    """Ensure Google Chrome is available. Returns path or raises.

    Chrome can't be auto-installed easily, so just detect and guide.
    """
    chrome = os.environ.get("CHROME_PATH")
    if chrome and os.path.exists(chrome):
        return chrome

    mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac_path):
        return mac_path

    linux_paths = [
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium-browser"),
        shutil.which("chromium"),
    ]
    for p in linux_paths:
        if p:
            return p

    raise RuntimeError(
        "Google Chrome not found.\n"
        "Install from: https://www.google.com/chrome/\n"
        "Or set CHROME_PATH environment variable."
    )


def ensure_render_deps():
    """Ensure all rendering dependencies are installed.

    Returns:
        (soffice_path, pdftoppm_path)
    """
    soffice = ensure_libreoffice()
    pdftoppm = ensure_pdftoppm()
    return soffice, pdftoppm


def check_all():
    """Check all dependencies and report status. Does not install."""
    deps = {
        "LibreOffice (soffice)": _find_soffice(),
        "pdftoppm (poppler)": shutil.which("pdftoppm"),
        "Google Chrome": None,
    }

    # Chrome detection
    chrome = os.environ.get("CHROME_PATH")
    if chrome and os.path.exists(chrome):
        deps["Google Chrome"] = chrome
    elif os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        deps["Google Chrome"] = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        for name in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
            p = shutil.which(name)
            if p:
                deps["Google Chrome"] = p
                break

    print("Dependency check:")
    all_ok = True
    for name, path in deps.items():
        status = f"OK ({path})" if path else "MISSING"
        if not path:
            all_ok = False
        print(f"  {name}: {status}")

    return all_ok
