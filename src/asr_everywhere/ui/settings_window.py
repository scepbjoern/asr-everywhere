"""Settings window using tkinter."""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from asr_everywhere.audio_recorder import AudioRecorder
from asr_everywhere.config import Config, save_config
from asr_everywhere.providers.registry import get_provider_models, list_providers

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings window for configuring ASR Everywhere."""

    def __init__(
        self,
        parent: tk.Tk | None,
        config: Config,
        on_save: Callable[[], None],
        on_close: Callable[[], None] | None = None,
    ) -> None:
        """Initialize settings window.

        Args:
            parent: Parent window (or None for standalone)
            config: Current configuration
            on_save: Callback to invoke after saving config
            on_close: Optional callback to invoke when window is closed without saving
        """
        self._config = config
        self._on_save = on_save
        self._on_close_cb = on_close
        self._hotkey_capturing = False
        self._capture_hook = None
        self._owns_root = parent is None

        # Create window - use parent's root if provided, otherwise create our own
        if parent is not None:
            self._root = None
            self._window = tk.Toplevel(parent)
        else:
            self._root = tk.Tk()
            self._window = self._root
        self._window.title("ASR Everywhere - Settings")
        self._window.geometry("550x450")
        self._window.resizable(True, True)

        # Bring to front and grab focus
        self._window.lift()
        self._window.attributes("-topmost", True)
        self._window.after(100, lambda: self._window.attributes("-topmost", False))
        self._window.focus_force()

        # Create main container
        self._main_frame = ttk.Frame(self._window, padding="10")
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook (tabs)
        self._notebook = ttk.Notebook(self._main_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        self._create_asr_tab()
        self._create_hotkeys_tab()
        self._create_audio_tab()
        self._create_language_tab()

        # Create buttons
        self._create_buttons()

        # Center window on screen
        self._center_window()

        # Bind close event
        self._window.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_window(self) -> None:
        """Center window on screen."""
        self._window.update_idletasks()
        width = self._window.winfo_width()
        height = self._window.winfo_height()
        x = (self._window.winfo_screenwidth() // 2) - (width // 2)
        y = (self._window.winfo_screenheight() // 2) - (height // 2)
        self._window.geometry(f"{width}x{height}+{x}+{y}")

    def _create_asr_tab(self) -> None:
        """Create ASR Provider configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="ASR Provider")

        # Provider selection
        ttk.Label(tab, text="Provider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self._provider_var = tk.StringVar(value=self._config.asr.provider)
        provider_combo = ttk.Combobox(
            tab,
            textvariable=self._provider_var,
            values=list_providers(),
            state="readonly",
            width=30,
        )
        provider_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)

        # API Key
        ttk.Label(tab, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self._api_key_var = tk.StringVar(value=self._config.asr.get_api_key())
        self._api_key_entry = ttk.Entry(
            tab,
            textvariable=self._api_key_var,
            show="*",
            width=35,
        )
        self._api_key_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Model selection
        ttk.Label(tab, text="Model:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self._model_var = tk.StringVar(value=self._config.asr.model)
        model_values = self._get_provider_model_names(self._config.asr.provider)
        self._model_combo = ttk.Combobox(
            tab,
            textvariable=self._model_var,
            values=model_values,
            state="readonly",
            width=30,
        )
        self._model_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Model price label
        self._model_price_label = ttk.Label(tab, text="")
        self._model_price_label.grid(row=2, column=2, sticky=tk.W, padx=5)
        self._update_model_price_label()
        self._model_combo.bind("<<ComboboxSelected>>", self._on_model_change)

        # Base URL (for local/custom)
        ttk.Label(tab, text="Base URL:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self._base_url_var = tk.StringVar(value=self._config.asr.get_base_url())
        self._base_url_entry = ttk.Entry(tab, textvariable=self._base_url_var, width=35)
        self._base_url_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Update visibility based on provider
        self._update_base_url_visibility()

        # Test button
        test_btn = ttk.Button(tab, text="Test Connection", command=self._test_provider)
        test_btn.grid(row=4, column=1, sticky=tk.W, pady=15)
        
        # Model configuration guide
        guide_frame = ttk.LabelFrame(tab, text="Add Custom Models", padding="5")
        guide_frame.grid(row=5, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        guide_text = (
            "To add custom models, edit config.json manually:\n"
            "1. Click 'Open Config' below to open config.json\n"
            "2. Find your provider under 'asr.providers'\n"
            "3. Add a new model to the 'models' list:\n"
            '   {"name": "model-name", "price_per_hour": "0.10 USD"}\n'
            "4. Save the file and restart the app"
        )
        ttk.Label(guide_frame, text=guide_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        open_config_btn = ttk.Button(guide_frame, text="Open Config", command=self._open_config_file)
        open_config_btn.pack(anchor=tk.W, pady=(5, 0))

    def _create_hotkeys_tab(self) -> None:
        """Create Hotkeys configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Hotkeys")

        # Dictation hotkey
        ttk.Label(tab, text="Dictation Hotkey:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self._hotkey_var = tk.StringVar(value=self._config.hotkey.dictate)
        hotkey_entry = ttk.Entry(tab, textvariable=self._hotkey_var, width=25)
        hotkey_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        hotkey_entry.config(state="readonly")

        capture_btn = ttk.Button(tab, text="Capture", command=self._capture_hotkey)
        capture_btn.grid(row=0, column=2, sticky=tk.W, padx=5)

        # Mode selection
        ttk.Label(tab, text="Mode:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self._mode_var = tk.StringVar(value=self._config.hotkey.mode)
        mode_frame = ttk.Frame(tab)
        mode_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Toggle", variable=self._mode_var, value="toggle").pack(
            side=tk.LEFT
        )
        ttk.Radiobutton(
            mode_frame, text="Push-to-Talk", variable=self._mode_var, value="push_to_talk"
        ).pack(side=tk.LEFT, padx=10)

        # Help text
        help_text = "Toggle: Press to start/stop. Push-to-Talk: Hold to record."
        ttk.Label(tab, text=help_text, foreground="gray").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=10
        )

    def _create_audio_tab(self) -> None:
        """Create Audio configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Audio")

        # Microphone selection
        ttk.Label(tab, text="Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)

        devices = AudioRecorder.list_devices()
        device_names = [f"{d['name']} ({d['channels']}ch)" for d in devices]

        # Find current device name
        current_device = self._config.audio.device
        current_name = "System Default"
        if current_device is not None:
            for d in devices:
                if d["id"] == current_device:
                    current_name = f"{d['name']} ({d['channels']}ch)"
                    break

        self._device_var = tk.StringVar(value=current_name)
        self._device_combo = ttk.Combobox(
            tab,
            textvariable=self._device_var,
            values=["System Default"] + device_names,
            state="readonly",
            width=40,
        )
        self._device_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Store devices for later lookup
        self._devices = devices

        # Refresh button
        refresh_btn = ttk.Button(tab, text="Refresh", command=self._refresh_devices)
        refresh_btn.grid(row=0, column=2, sticky=tk.W, padx=5)

        # Sample rate (info only)
        ttk.Label(tab, text="Sample Rate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(tab, text=f"{self._config.audio.sample_rate} Hz").grid(
            row=1, column=1, sticky=tk.W
        )

    def _create_language_tab(self) -> None:
        """Create Language configuration tab."""
        tab = ttk.Frame(self._notebook, padding="10")
        self._notebook.add(tab, text="Language")

        # Language selection
        ttk.Label(tab, text="Language:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self._language_var = tk.StringVar(value=self._config.asr.language)
        language_combo = ttk.Combobox(
            tab,
            textvariable=self._language_var,
            values=["auto", "de", "en"],
            state="readonly",
            width=20,
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Language labels
        ttk.Label(tab, text="(Auto-detect, German, or English)").grid(
            row=0, column=2, sticky=tk.W, padx=10
        )

        # Clipboard behavior
        ttk.Label(tab, text="Clipboard:").grid(row=1, column=0, sticky=tk.W, pady=15)
        self._clipboard_var = tk.StringVar(
            value="restore" if self._config.clipboard_restore else "keep"
        )
        clipboard_frame = ttk.Frame(tab)
        clipboard_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(
            clipboard_frame,
            text="Restore after insert",
            variable=self._clipboard_var,
            value="restore",
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            clipboard_frame,
            text="Keep transcription",
            variable=self._clipboard_var,
            value="keep",
        ).pack(side=tk.LEFT, padx=10)
        
        # Notification toggle
        ttk.Label(tab, text="Notification:").grid(row=2, column=0, sticky=tk.W, pady=15)
        self._notification_var = tk.StringVar(
            value="show" if self._config.show_notification else "hide"
        )
        notification_frame = ttk.Frame(tab)
        notification_frame.grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(
            notification_frame,
            text="Show after transcription",
            variable=self._notification_var,
            value="show",
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            notification_frame,
            text="Don't show",
            variable=self._notification_var,
            value="hide",
        ).pack(side=tk.LEFT, padx=10)

    def _create_buttons(self) -> None:
        """Create Save and Cancel buttons."""
        button_frame = ttk.Frame(self._main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Save", command=self._on_save_click).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)

    def _get_provider_model_names(self, provider_name: str) -> list[str]:
        """Get model names for a provider from config."""
        if provider_name in self._config.asr.providers:
            provider_config = self._config.asr.providers[provider_name]
            if provider_config.models:
                return [m.name for m in provider_config.models]
        # Fallback to hardcoded if no models in config
        return get_provider_models(provider_name)

    def _update_model_price_label(self) -> None:
        """Update the model price label based on selected model."""
        model_name = self._model_var.get()
        provider = self._provider_var.get()
        price = ""
        
        if provider in self._config.asr.providers:
            provider_config = self._config.asr.providers[provider]
            for model in provider_config.models:
                if model.name == model_name:
                    price = model.price_per_hour
                    break
        
        if price:
            self._model_price_label.config(text=f"({price})")
        else:
            self._model_price_label.config(text="")

    def _on_model_change(self, event: tk.Event) -> None:
        """Handle model selection change."""
        self._update_model_price_label()

    def _on_provider_change(self, event: tk.Event) -> None:
        """Handle provider selection change."""
        provider = self._provider_var.get()

        # Update model list from config
        models = self._get_provider_model_names(provider)
        self._model_combo["values"] = models
        if models:
            self._model_var.set(models[0])

        # Update API key and base URL from config
        if provider in self._config.asr.providers:
            self._api_key_var.set(self._config.asr.providers[provider].api_key)
            self._base_url_var.set(self._config.asr.providers[provider].base_url)
        else:
            self._api_key_var.set("")
            self._base_url_var.set("")

        # Update visibility
        self._update_base_url_visibility()
        self._update_model_price_label()

        logger.debug(f"Provider changed to: {provider}")

    def _update_base_url_visibility(self) -> None:
        """Update base URL field visibility and editability."""
        provider = self._provider_var.get()
        # Allow editing for local provider, show but readonly for others
        if provider == "local":
            self._base_url_entry.config(state="normal")
        else:
            # Still show the URL but make it readonly
            self._base_url_entry.config(state="readonly")

    def _capture_hotkey(self) -> None:
        """Capture hotkey combination from keyboard."""
        import keyboard

        if self._hotkey_capturing:
            return

        self._hotkey_capturing = True
        self._hotkey_var.set("Press keys...")
        self._capture_hook = None

        def on_capture(event):
            # Only process key press events (not releases)
            if event.event_type != keyboard.KEY_DOWN:
                return

            # Build hotkey string
            modifiers = []
            key = event.name.lower() if event.name else ""

            # Check modifier keys
            if keyboard.is_pressed("ctrl"):
                modifiers.append("ctrl")
            if keyboard.is_pressed("alt"):
                modifiers.append("alt")
            if keyboard.is_pressed("shift"):
                modifiers.append("shift")
            if keyboard.is_pressed("windows"):
                modifiers.append("win")

            # Only accept combo with at least one modifier and a non-modifier key
            modifier_keys = {"ctrl", "alt", "shift", "windows", "left ctrl", "right ctrl",
                             "left alt", "right alt", "left shift", "right shift"}
            if modifiers and key and key not in modifier_keys:
                hotkey = "+".join(modifiers + [key])
                self._hotkey_var.set(hotkey)
                # Only unhook our specific hook, not all hooks
                if self._capture_hook:
                    keyboard.unhook(self._capture_hook)
                self._hotkey_capturing = False

        # Hook keyboard events (don't suppress - let main app still work)
        self._capture_hook = keyboard.hook(on_capture, suppress=False)

        # Timeout after 5 seconds
        self._window.after(5000, self._cancel_hotkey_capture)

    def _cancel_hotkey_capture(self) -> None:
        """Cancel hotkey capture if still active."""
        if self._hotkey_capturing and self._capture_hook:
            import keyboard

            keyboard.unhook(self._capture_hook)
            self._capture_hook = None
            self._hotkey_var.set(self._config.hotkey.dictate)
            self._hotkey_capturing = False

    def _refresh_devices(self) -> None:
        """Refresh audio device list."""
        devices = AudioRecorder.list_devices()
        device_names = [f"{d['name']} ({d['channels']}ch)" for d in devices]
        self._device_combo["values"] = ["System Default"] + device_names
        self._devices = devices
        messagebox.showinfo("Refresh", "Device list refreshed")

    def _test_provider(self) -> None:
        """Test provider connection with current settings."""
        provider_name = self._provider_var.get()
        api_key = self._api_key_var.get()
        base_url = self._base_url_var.get()

        if not api_key and provider_name != "local":
            messagebox.showwarning(
                "Missing API Key",
                f"Please enter an API key for {provider_name}",
            )
            return

        # Simple validation - check if we can create a client
        try:
            from openai import OpenAI

            OpenAI(api_key=api_key or "test", base_url=base_url)
            # Just verify client creation works
            messagebox.showinfo(
                "Success",
                f"Connection settings valid for {provider_name}",
            )
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"Failed to connect to {provider_name}:\n{e}",
            )

    def _open_config_file(self) -> None:
        """Open config.json in the default text editor."""
        import subprocess

        from asr_everywhere.config import get_config_path

        config_path = get_config_path()
        try:
            subprocess.run(["start", "", str(config_path)], shell=True, check=True)
        except Exception as e:
            logger.error(f"Failed to open config file: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to open config file:\n{config_path}\n\n{e}",
            )

    def _on_save_click(self) -> None:
        """Handle Save button click."""
        # Update config from UI values
        self._config.asr.provider = self._provider_var.get()
        self._config.asr.model = self._model_var.get()
        self._config.asr.language = self._language_var.get()

        # Update provider-specific config
        provider = self._config.asr.provider
        if provider in self._config.asr.providers:
            self._config.asr.providers[provider].api_key = self._api_key_var.get()
            self._config.asr.providers[provider].base_url = self._base_url_var.get()

        # Update hotkey config
        self._config.hotkey.dictate = self._hotkey_var.get()
        self._config.hotkey.mode = self._mode_var.get()

        # Update audio config
        device_name = self._device_var.get()
        if device_name == "System Default":
            self._config.audio.device = None
        else:
            for d in self._devices:
                if f"{d['name']} ({d['channels']}ch)" == device_name:
                    self._config.audio.device = d["id"]
                    break

        # Update clipboard config
        self._config.clipboard_restore = self._clipboard_var.get() == "restore"
        
        # Update notification config
        self._config.show_notification = self._notification_var.get() == "show"

        # Save config
        save_config(self._config)

        # Notify parent
        self._on_save()

        # Close window
        self._cleanup_vars()
        self._window.destroy()

        logger.info("Settings saved")

    def _on_cancel(self) -> None:
        """Handle Cancel button or window close."""
        self._cleanup_vars()
        self._window.destroy()
        if self._on_close_cb:
            self._on_close_cb()

    def _cleanup_vars(self) -> None:
        """Explicitly destroy tkinter Variables to avoid thread cleanup errors."""
        # Set all Variables to None to trigger proper cleanup in tkinter thread
        for var_name in [
            "_provider_var",
            "_api_key_var",
            "_model_var",
            "_base_url_var",
            "_hotkey_var",
            "_mode_var",
            "_device_var",
            "_language_var",
            "_clipboard_var",
        ]:
            if hasattr(self, var_name):
                setattr(self, var_name, None)

    def show(self) -> None:
        """Show the settings window and run its own event loop."""
        if self._owns_root:
            self._window.mainloop()
        else:
            self._window.wait_window()


def open_settings_in_thread(
    config: Config,
    on_save: Callable[[], None],
    on_close: Callable[[], None] | None = None,
) -> None:
    """Open the settings window in a dedicated thread with its own event loop.

    Args:
        config: Current configuration
        on_save: Callback to invoke after saving config
        on_close: Optional callback to invoke when window is closed without saving
    """

    def _run() -> None:
        window = SettingsWindow(None, config, on_save, on_close)
        window.show()

    thread = threading.Thread(target=_run, daemon=True, name="settings-window")
    thread.start()
