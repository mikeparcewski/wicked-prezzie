"""Dependency detection and auto-installation for wicked-prezzie.

Checks for required external tools and installs them if missing,
using the appropriate package manager for the current platform.

Supported package managers:
  macOS:   brew
  Linux:   apt-get
  Windows: winget, choco (fallback)
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


def _is_windows():
    return platform.system() == "Windows"


def _has_brew():
    return shutil.which("brew") is not None


def _has_apt():
    return shutil.which("apt-get") is not None


def _has_winget():
    return shutil.which("winget") is not None


def _has_choco():
    return shutil.which("choco") is not None


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

    # macOS
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if os.path.exists(p):
            return p

    # Linux
    linux_paths = [
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ]
    for p in linux_paths:
        if os.path.exists(p):
            return p

    # Windows
    win_paths = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                     "LibreOffice", "program", "soffice.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                     "LibreOffice", "program", "soffice.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     "Programs", "LibreOffice", "program", "soffice.exe"),
    ]
    for p in win_paths:
        if p and os.path.exists(p):
            return p

    return None


def _find_pdftoppm():
    """Find pdftoppm binary across platforms."""
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        return pdftoppm

    # Windows: poppler for Windows installs to common locations
    if _is_windows():
        win_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                         "poppler", "Library", "bin", "pdftoppm.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                         "poppler-utils", "bin", "pdftoppm.exe"),
        ]
        for p in win_paths:
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
        if _run_install(["sudo", "apt-get", "install", "-y", "libreoffice-impress"],
                        "LibreOffice Impress"):
            soffice = _find_soffice()
            if soffice:
                return soffice

    elif _is_windows():
        if _has_winget():
            if _run_install(["winget", "install", "--id", "TheDocumentFoundation.LibreOffice",
                             "--accept-package-agreements", "--accept-source-agreements"],
                            "LibreOffice"):
                soffice = _find_soffice()
                if soffice:
                    return soffice
        elif _has_choco():
            if _run_install(["choco", "install", "libreoffice-fresh", "-y"], "LibreOffice"):
                soffice = _find_soffice()
                if soffice:
                    return soffice

    raise RuntimeError(
        "Could not install LibreOffice automatically.\n"
        "Install manually:\n"
        "  macOS:   brew install --cask libreoffice\n"
        "  Ubuntu:  sudo apt install libreoffice-impress\n"
        "  Windows: winget install TheDocumentFoundation.LibreOffice\n"
        "           or https://www.libreoffice.org/download/"
    )


def ensure_pdftoppm():
    """Ensure pdftoppm (poppler) is installed. Install if missing.

    Returns:
        Path to pdftoppm binary.

    Raises:
        RuntimeError if installation fails or platform unsupported.
    """
    pdftoppm = _find_pdftoppm()
    if pdftoppm:
        return pdftoppm

    print("\n  pdftoppm not found — required for PDF-to-PNG conversion.")

    if _is_macos() and _has_brew():
        if _run_install(["brew", "install", "poppler"], "poppler"):
            pdftoppm = _find_pdftoppm()
            if pdftoppm:
                return pdftoppm

    elif _is_linux() and _has_apt():
        if _run_install(["sudo", "apt-get", "install", "-y", "poppler-utils"], "poppler-utils"):
            pdftoppm = _find_pdftoppm()
            if pdftoppm:
                return pdftoppm

    elif _is_windows():
        if _has_choco():
            if _run_install(["choco", "install", "poppler", "-y"], "poppler"):
                pdftoppm = _find_pdftoppm()
                if pdftoppm:
                    return pdftoppm
        elif _has_winget():
            # poppler not in winget, guide to choco or manual
            pass

    raise RuntimeError(
        "Could not install poppler automatically.\n"
        "Install manually:\n"
        "  macOS:   brew install poppler\n"
        "  Ubuntu:  sudo apt install poppler-utils\n"
        "  Windows: choco install poppler\n"
        "           or https://github.com/oschwartz10612/poppler-windows/releases"
    )


def ensure_chrome():
    """Ensure Google Chrome is available. Returns path or raises."""
    chrome = os.environ.get("CHROME_PATH")
    if chrome and os.path.exists(chrome):
        return chrome

    # macOS
    mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac_path):
        return mac_path

    # Linux
    for name in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
        p = shutil.which(name)
        if p:
            return p

    # Windows
    win_paths = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                     "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                     "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     "Google", "Chrome", "Application", "chrome.exe"),
    ]
    for p in win_paths:
        if p and os.path.exists(p):
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
        "pdftoppm (poppler)": _find_pdftoppm(),
        "Google Chrome": None,
    }

    # Chrome detection
    try:
        deps["Google Chrome"] = ensure_chrome()
    except RuntimeError:
        pass

    print("Dependency check:")
    all_ok = True
    for name, path in deps.items():
        status = f"OK ({path})" if path else "MISSING"
        if not path:
            all_ok = False
        print(f"  {name}: {status}")

    return all_ok
