"""
OHW - Oral History Workflow
A Flet UI app designed to streamline the oral history recording and ingest workflow
for Digital.Grinnell, including WAV-to-MP3 conversion and future processing steps.
"""

import flet as ft
import os
import logging
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
os.makedirs("logfiles", exist_ok=True)
log_filename = f"logfiles/ohw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

# Reduce Flet's logging verbosity
logging.getLogger("flet").setLevel(logging.WARNING)
logging.getLogger("flet_core").setLevel(logging.WARNING)
logging.getLogger("flet_desktop").setLevel(logging.WARNING)

# Persistent storage file
PERSISTENCE_FILE = "persistent.json"


class PersistentStorage:
    """Handle persistent storage of UI state and function usage."""

    def __init__(self):
        self.data = self.load()

    def load(self) -> dict:
        """Load persistent data from file."""
        try:
            if os.path.exists(PERSISTENCE_FILE):
                with open(PERSISTENCE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Loaded persistent data from {PERSISTENCE_FILE}")
                return data
        except Exception as e:
            logger.warning(f"Could not load persistent data: {str(e)}")

        return {
            "ui_state": {
                "last_wav_dir": "",
                "last_mp3_dir": "",
            },
            "function_usage": {},
        }

    def save(self):
        """Save persistent data to file."""
        try:
            with open(PERSISTENCE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved persistent data to {PERSISTENCE_FILE}")
        except Exception as e:
            logger.error(f"Could not save persistent data: {str(e)}")

    def set_ui_state(self, field: str, value: str):
        """Update UI state field."""
        self.data["ui_state"][field] = value
        self.save()

    def get_ui_state(self, field: str, default: str = "") -> str:
        """Get UI state field."""
        return self.data["ui_state"].get(field, default)

    def record_function_usage(self, function_name: str):
        """Record that a function was used."""
        if function_name not in self.data["function_usage"]:
            self.data["function_usage"][function_name] = {"count": 0}

        self.data["function_usage"][function_name]["last_used"] = datetime.now().isoformat()
        self.data["function_usage"][function_name]["count"] = (
            self.data["function_usage"][function_name].get("count", 0) + 1
        )
        self.save()

    def get_function_usage(self, function_name: str) -> dict:
        """Get usage stats for a function."""
        return self.data["function_usage"].get(
            function_name, {"last_used": None, "count": 0}
        )


def check_ffmpeg() -> bool:
    """Return True if ffmpeg is available on PATH."""
    return shutil.which("ffmpeg") is not None


def convert_wav_to_mp3(
    wav_path: Path,
    mp3_path: Path,
    quality: int = 2,
    sample_rate: int = 44100,
) -> tuple[bool, str]:
    """
    Convert a WAV file to MP3 using ffmpeg.

    Args:
        wav_path: Path to the source WAV file.
        mp3_path: Destination path for the MP3 file.
        quality:  VBR quality level (0=best, 9=worst; 2 approx. 190 kbps).
        sample_rate: Output sample rate in Hz.

    Returns:
        (success, message)
    """
    if not check_ffmpeg():
        return False, (
            "ffmpeg is not installed. Please install it:\n"
            "  • macOS:  brew install ffmpeg\n"
            "  • Linux:  sudo apt install ffmpeg\n"
            "  • Windows: https://ffmpeg.org/download.html"
        )

    if not wav_path.exists():
        return False, f"Source file not found: {wav_path}"

    if mp3_path.exists():
        return False, f"Output file already exists: {mp3_path}"

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-q:a", str(quality),
                "-ar", str(sample_rate),
                str(mp3_path),
                "-hide_banner",
                "-loglevel", "error",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0 and mp3_path.exists():
            wav_mb = wav_path.stat().st_size / (1024 * 1024)
            mp3_mb = mp3_path.stat().st_size / (1024 * 1024)
            return True, (
                f"✅ Conversion successful!\n\n"
                f"Created: {mp3_path.name}\n"
                f"Location: {mp3_path.parent}\n\n"
                f"WAV: {wav_mb:.1f} MB  →  MP3: {mp3_mb:.1f} MB"
            )

        error_msg = result.stderr.strip() if result.stderr else "Unknown ffmpeg error"
        return False, f"❌ ffmpeg error:\n\n{error_msg}"

    except subprocess.TimeoutExpired:
        return False, "❌ Conversion timed out after 10 minutes."
    except Exception as exc:
        return False, f"❌ Unexpected error: {exc}"


def main(page: ft.Page):
    page.title = "OHW - Oral History Workflow"
    page.padding = 20
    page.window.width = 900
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO

    storage = PersistentStorage()
    logger.info("OHW application started")

    # ------------------------------------------------------------------ helpers

    def add_log_message(text: str):
        """Prepend a timestamped line to the log output field."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        existing = log_output.value or ""
        log_output.value = f"[{timestamp}] {text}\n{existing}"
        page.update()

    def update_status(message: str, is_error: bool = False):
        """Update the status text widget."""
        status_text.value = message
        status_text.color = ft.Colors.RED_600 if is_error else ft.Colors.GREEN_700
        page.update()

    # ------------------------------------------------------------------ widgets

    status_text = ft.Text(
        "Ready",
        size=14,
        color=ft.Colors.GREEN_700,
        italic=True,
    )

    log_output = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=8,
        max_lines=12,
        text_size=12,
        border_color=ft.Colors.GREY_400,
        bgcolor=ft.Colors.GREY_100,
        value="",
    )

    # -------------------------------------------------------- WAV-to-MP3 state
    selected_wav_path: Path | None = None

    wav_file_label = ft.Text(
        "No WAV file selected",
        size=13,
        color=ft.Colors.GREY_600,
        italic=True,
    )

    convert_button = ft.ElevatedButton(
        "Convert WAV → MP3",
        icon=ft.Icons.AUDIO_FILE,
        disabled=True,
        visible=False,
    )

    wav_file_picker = ft.FilePicker()
    page.overlay.append(wav_file_picker)

    # -------------------------------------------------------- function handlers

    def on_wav_file_picked(e: ft.FilePickerResultEvent):
        """Called when the user selects a WAV file."""
        nonlocal selected_wav_path
        if not e.files:
            wav_file_label.value = "Selection cancelled"
            wav_file_label.color = ft.Colors.ORANGE_600
            convert_button.disabled = True
            convert_button.visible = False
            selected_wav_path = None
            page.update()
            return

        path = Path(e.files[0].path)
        selected_wav_path = path
        storage.set_ui_state("last_wav_dir", str(path.parent))

        wav_file_label.value = f"{path.name}  ({path.parent})"
        wav_file_label.color = ft.Colors.BLUE_700
        convert_button.disabled = False
        convert_button.visible = True
        add_log_message(f"WAV file selected: {path.name}")
        update_status(f"WAV file selected: {path.name}")

    wav_file_picker.on_result = on_wav_file_picked

    def on_pick_wav_click(e):
        """Open the file picker for WAV files."""
        if not check_ffmpeg():
            update_status(
                "⚠️  ffmpeg not found — install it before converting WAV files.",
                is_error=True,
            )
            add_log_message(
                "ffmpeg not installed. Install via: brew install ffmpeg (macOS) "
                "or sudo apt install ffmpeg (Linux)"
            )
            return

        initial_dir = storage.get_ui_state("last_wav_dir") or str(Path.home())
        wav_file_picker.pick_files(
            dialog_title="Select a WAV file to convert to MP3",
            allowed_extensions=["wav", "WAV"],
            initial_directory=initial_dir if os.path.isdir(initial_dir) else None,
        )

    def on_convert_click(e):
        """Execute WAV → MP3 conversion."""
        nonlocal selected_wav_path
        wav_path = selected_wav_path
        if wav_path is None:
            update_status("No WAV file selected.", is_error=True)
            return

        mp3_path = wav_path.with_suffix(".mp3")

        if mp3_path.exists():
            update_status(
                f"⚠️  MP3 already exists: {mp3_path.name} — skipping conversion.",
                is_error=True,
            )
            add_log_message(f"Skipped: {mp3_path.name} already exists.")
            return

        storage.record_function_usage("function_1_wav_to_mp3")
        convert_button.disabled = True
        update_status(f"Converting {wav_path.name} …")
        add_log_message(f"Starting conversion: {wav_path.name} → {mp3_path.name}")
        page.update()

        success, message = convert_wav_to_mp3(wav_path, mp3_path)

        if success:
            storage.set_ui_state("last_mp3_dir", str(mp3_path.parent))
            add_log_message(f"✅ Conversion complete: {mp3_path.name}")
            # Disable convert button — MP3 now exists; user should pick a new file
            convert_button.disabled = True
        else:
            add_log_message(f"❌ Conversion failed: {message}")
            convert_button.disabled = False

        update_status(message.splitlines()[0], is_error=not success)
        page.update()

    convert_button.on_click = on_convert_click

    def on_clear_log_click(e):
        """Clear the log output field."""
        log_output.value = ""
        page.update()

    def on_copy_status_click(e):
        """Copy current status text to clipboard."""
        page.set_clipboard(status_text.value or "")
        add_log_message("Status copied to clipboard.")

    # ------------------------------------------------------------------ layout

    page.add(
        ft.Column(
            controls=[
                # ---- Title
                ft.Text(
                    "🎙️ OHW — Oral History Workflow",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "A tool for managing creation and ingest of Oral Histories for Digital.Grinnell",
                    size=13,
                    color=ft.Colors.GREY_700,
                    italic=True,
                ),
                ft.Divider(height=8),

                # ---- Function 1: WAV to MP3 Conversion
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Function 1 — Convert WAV to MP3",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Select a WAV file and convert it to a compressed MP3 "
                                "using ffmpeg (libmp3lame, VBR quality 2, approx. 190 kbps).",
                                size=13,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "Select WAV File…",
                                        icon=ft.Icons.FOLDER_OPEN,
                                        on_click=on_pick_wav_click,
                                    ),
                                    wav_file_label,
                                ],
                                spacing=12,
                            ),
                            convert_button,
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50,
                ),

                ft.Divider(height=8),

                # ---- Status
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Status",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.COPY,
                                        tooltip="Copy status to clipboard",
                                        on_click=on_copy_status_click,
                                        icon_size=20,
                                    ),
                                ],
                            ),
                            status_text,
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.all(10),
                ),

                ft.Divider(height=8),

                # ---- Log output
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Log Output",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_SWEEP,
                                        tooltip="Clear log",
                                        on_click=on_clear_log_click,
                                        icon_size=20,
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=log_output,
                                border=ft.border.all(1, ft.Colors.GREY_400),
                                border_radius=5,
                                bgcolor=ft.Colors.GREY_100,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.all(10),
                ),
            ],
            spacing=4,
        )
    )

    logger.info("UI initialised successfully")
    add_log_message("OHW application ready. Select a WAV file to begin.")


if __name__ == "__main__":
    logger.info("Application starting…")
    ft.app(
        target=main,
        assets_dir="assets",
    )
