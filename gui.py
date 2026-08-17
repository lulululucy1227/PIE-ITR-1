"""Windows-light tkinter presentation layer for NextopSync.

All case rules and network operations remain in case_service.py.  This file
only renders the interface and returns worker-thread events to tkinter's main
thread.
"""
import queue
import threading
import time
import tkinter as tk
import ctypes
import sys
import webbrowser
from time import perf_counter
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from tkinter import messagebox, ttk

import case_service


MANUAL_SOURCES = ("whatsapp", "lark", "email")
BG = "#F5F7FA"
PANEL = "#FFFFFF"
PANEL_ALT = "#F8FAFC"
INPUT = "#FFFFFF"
BORDER = "#D9E1EA"
WEAK_BORDER = "#E7ECF2"
BLUE = "#1677FF"
BLUE_HOVER = "#0F6BEA"
SELECTED = "#EAF3FF"
TEXT = "#1F2937"
MUTED = "#667085"
DISABLED = "#98A2B3"
SUCCESS = "#16A085"
ERROR = "#C24141"
APP_USER_MODEL_ID = "Mammotion.PIE.ITRAssistant"
PROGRESS_STAGES = {
    "ready": ("READY", 0), "nextop_fetch": ("FETCHING", 10),
    "nextop_authenticating": ("AUTHENTICATING", 15),
    "nextop_auth_required": ("AUTHENTICATION REQUIRED", 15),
    "analysis": ("ANALYZING", 30), "classification": ("ANALYZING", 30),
    "matching": ("MATCHING", 50), "candidates": ("MATCHING", 50),
    "prepared": ("READY FOR REVIEW", 0), "notes": ("PREPARED", 60),
    "create": ("WRITING", 70), "writing": ("WRITING", 70),
    "refreshing_case_count": ("REFRESHING", 85),
    "verifying_case_count": ("VERIFYING", 95), "complete": ("COMPLETE", 100),
    "review_ready": ("READY FOR REVIEW", 0),
}
LOGIQ_URL = "https://logiq.cloud-cn.mammotion.com/"


def _set_windows_app_user_model_id():
    """Set Windows taskbar identity before tkinter creates a native window."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        pass


class WorkspaceState(Enum):
    EMPTY = auto()
    EDITING = auto()
    ANALYZING = auto()
    ANALYZED = auto()
    REVIEW_READY = auto()
    WRITING = auto()
    COMPLETED = auto()
    VIEWING_HISTORY = auto()


@dataclass
class CaseWorkspace:
    """All mutable case-view state, independent from the reusable widgets."""
    workspace_id: str
    source: str = "nextop"
    workspace_type: str = "NEW_CASE"
    ticket_input: str = ""
    manual_input: str = ""
    record_id: str | None = None
    current_case_dto: dict | None = None
    current_case_summary: dict | None = None
    draft: object | None = None
    candidates: list = field(default_factory=list)
    selected_record_id: str | None = None
    preview: dict | None = None
    analysis_result: dict | None = None
    analysis_language: str = "ORIGINAL"
    translation_source_hash: str | None = None
    translation_result: object | None = None
    notes: str = ""
    logiq_session_state: str = "NOT_OPENED"
    timings: dict = field(default_factory=dict)
    prepared_case: object | None = None
    translation_cache: dict = field(default_factory=dict)
    todo_original_value: bool = False
    todo_current_value: bool = False
    todo_dirty: bool = False
    progress_stage: str = "ready"
    progress_percent: int = 0
    progress_detail: str = "Waiting for input."
    status_text: str = "READY — Waiting for input."
    state: WorkspaceState = WorkspaceState.EMPTY
    last_result: dict | None = None
    running: bool = False
    generation: int = 0
    pending_nextop_ticket: str | None = None
    nextop_auth_required: bool = False


class PieItrAssistant:
    _SOURCE_LABELS = {
        "nextop": "Nextop",
        "whatsapp": "WhatsApp",
        "lark": "Lark",
        "email": "Email",
    }

    @staticmethod
    def _case_label(count):
        return f"{count} CASE" if count == 1 else f"{count} CASES"

    def _source_label(self, source=None):
        return self._SOURCE_LABELS.get(source or self.source.get(), source or self.source.get())

    def __init__(self, root):
        self.root = root
        root.title("PIE ITR Assistant")
        root.geometry("1200x700")
        root.minsize(1000, 650)
        root.configure(background=BG)
        self.source = tk.StringVar(value="nextop")
        self.ticket_no = tk.StringVar()
        self.ticket_no.trace_add("write", self._ticket_changed)
        self.status = tk.StringVar(value="READY — Waiting for input.")
        self.bottom_status = tk.StringVar(value="READY")
        self.progress_value = tk.IntVar(value=0)
        self.progress_percent = tk.StringVar(value="0%")
        self.status.trace_add("write", self._sync_task_strip)
        self.case_count = tk.StringVar(value="0 CASES")
        self._events = queue.Queue()
        self._workspaces = {}
        self._workspace_order = []
        self._active_workspace_id = None
        self._loading_workspace = False
        self._record_write_locks = set()
        self._create_workspace("nextop", activate=True)
        self._today_cases = {}
        self._today_visible = []
        self._view_mode = "workspace"
        self.preferred_analysis_language = "ZH"
        self.todo_var = tk.BooleanVar(value=False)
        self._tabs = {}
        self._set_window_icon()
        self._configure_style()
        self._build()
        root.after(100, self._drain_events)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def _active_workspace(self):
        return self._workspaces[self._active_workspace_id]

    @property
    def _state(self): return self._active_workspace.state
    @_state.setter
    def _state(self, value): self._active_workspace.state = value
    @property
    def _running(self): return self._active_workspace.running
    @_running.setter
    def _running(self, value): self._active_workspace.running = bool(value)
    @property
    def _draft(self): return self._active_workspace.draft
    @_draft.setter
    def _draft(self, value): self._active_workspace.draft = value
    @property
    def _candidates(self): return self._active_workspace.candidates
    @_candidates.setter
    def _candidates(self, value): self._active_workspace.candidates = value
    @property
    def _current_case(self): return self._active_workspace.current_case_dto
    @_current_case.setter
    def _current_case(self, value):
        self._active_workspace.current_case_dto = value
        self._active_workspace.record_id = (value or {}).get("record_id") or self._active_workspace.record_id
    @property
    def _todo_original_value(self): return self._active_workspace.todo_original_value
    @_todo_original_value.setter
    def _todo_original_value(self, value): self._active_workspace.todo_original_value = bool(value)
    @property
    def _todo_dirty(self): return self._active_workspace.todo_dirty
    @_todo_dirty.setter
    def _todo_dirty(self, value): self._active_workspace.todo_dirty = bool(value)
    @property
    def _pending_nextop_ticket(self): return self._active_workspace.pending_nextop_ticket
    @_pending_nextop_ticket.setter
    def _pending_nextop_ticket(self, value): self._active_workspace.pending_nextop_ticket = value
    @property
    def _nextop_auth_required(self): return self._active_workspace.nextop_auth_required
    @_nextop_auth_required.setter
    def _nextop_auth_required(self, value): self._active_workspace.nextop_auth_required = bool(value)

    def _create_workspace(self, source=None, activate=False):
        workspace_id = f"ws-{len(self._workspace_order) + 1}"
        workspace = CaseWorkspace(workspace_id=workspace_id, source=source or self.source.get())
        self._workspaces[workspace_id] = workspace
        self._workspace_order.append(workspace_id)
        if activate and self._active_workspace_id and hasattr(self, "input_panel"):
            self._save_active_workspace()
        if activate or self._active_workspace_id is None:
            self._active_workspace_id = workspace_id
        if hasattr(self, "case_tab_strip"):
            self._activate_workspace(workspace_id, force=True)
        return workspace

    def _workspace_tab_text(self, workspace):
        if workspace.current_case_dto:
            return str(workspace.current_case_dto.get("ticket_no") or workspace.current_case_dto.get("reference_no") or "Case")
        if workspace.ticket_input:
            return workspace.ticket_input
        if workspace.source == "nextop":
            return "New Case"
        return f"New {self._source_label(workspace.source)}"

    def _render_case_tabs(self):
        for child in self.case_tab_strip.winfo_children():
            child.destroy()
        for workspace_id in self._workspace_order:
            workspace = self._workspaces[workspace_id]
            active = workspace_id == self._active_workspace_id
            label = self._workspace_tab_text(workspace) + (" *" if workspace.state in {WorkspaceState.EDITING, WorkspaceState.ANALYZED} else "")
            style = "CaseTabActive.TButton" if active else "CaseTab.TButton"
            tab = ttk.Frame(self.case_tab_strip, style="TFrame")
            tab.pack(side="left", padx=(0, 5))
            ttk.Button(tab, text=label, command=lambda wid=workspace_id: self._activate_workspace(wid), style=style).pack(side="left")
            if len(self._workspace_order) > 1:
                ttk.Button(tab, text="×", command=lambda wid=workspace_id: self._close_workspace(wid), style="CaseTab.TButton", width=2).pack(side="left", padx=(1, 0))
        ttk.Button(self.case_tab_strip, text="+", command=self._new_case, style="CaseTab.TButton", width=3).pack(side="left")

    def _close_workspace(self, workspace_id):
        workspace = self._workspaces.get(workspace_id)
        if not workspace or workspace.running:
            return
        if workspace.state in {WorkspaceState.EDITING, WorkspaceState.ANALYZED} and not messagebox.askyesno("Unsaved input", "Close this unsaved workspace?"):
            return
        self._workspace_order.remove(workspace_id)
        self._workspaces.pop(workspace_id, None)
        if workspace_id == self._active_workspace_id:
            self._active_workspace_id = self._workspace_order[-1]
            self._activate_workspace(self._active_workspace_id, force=True)
        else:
            self._render_case_tabs()

    def _save_active_workspace(self):
        if not self._active_workspace_id or self._loading_workspace:
            return
        workspace = self._active_workspace
        workspace.source = self.source.get()
        workspace.ticket_input = self.ticket_no.get()
        workspace.todo_current_value = bool(self.todo_var.get())
        workspace.status_text = self.status.get()
        workspace.progress_percent = self.progress_value.get()
        workspace.progress_detail = self.task_detail.get()
        if getattr(self, "manual_text", None):
            workspace.manual_input = self.manual_text.get("1.0", "end-1c")
        selected = self.tree.selection() if hasattr(self, "tree") else ()
        if selected and self._view_mode != "today":
            index = int(selected[0])
            if 0 <= index < len(workspace.candidates):
                workspace.selected_record_id = workspace.candidates[index].get("record_id")

    def _activate_workspace(self, workspace_id, force=False):
        if workspace_id == self._active_workspace_id and hasattr(self, "input_panel") and not force:
            return
        self._save_active_workspace()
        self._active_workspace_id = workspace_id
        workspace = self._active_workspace
        self._loading_workspace = True
        try:
            self.source.set(workspace.source)
            self.ticket_no.set(workspace.ticket_input)
            self.todo_var.set(workspace.todo_current_value)
            self.status.set(workspace.status_text)
            self.progress_value.set(workspace.progress_percent)
            self.progress_percent.set(f"{workspace.progress_percent}%")
            self.task_detail.set(workspace.progress_detail)
            if hasattr(self, "input_panel"):
                self._view_mode = "workspace"
                self._render_workspace_view()
                if getattr(self, "manual_text", None):
                    self.manual_text.insert("1.0", workspace.manual_input)
                    self.manual_text.edit_modified(False)
                if not self._is_inspector_workspace(workspace):
                    self._render_workspace_candidates()
                self._render_workspace_progress()
                self._set_mode_buttons()
        finally:
            self._loading_workspace = False
        self._render_case_tabs()

    def _is_inspector_workspace(self, workspace=None):
        workspace = workspace or self._active_workspace
        return workspace.workspace_type in {"EXISTING_CASE", "PREPARED_CASE"} and bool(workspace.current_case_dto or workspace.prepared_case)

    def _render_workspace_candidates(self):
        if self.source.get() not in MANUAL_SOURCES:
            return
        self._clear_candidates()
        for index, candidate in enumerate(self._candidates):
            self.tree.insert("", "end", iid=str(index), values=(candidate.get("ticket_no") or "-", candidate.get("disti") or "", candidate.get("model_type") or "", case_service.format_time(candidate.get("replied_time_new"))))
        if self._candidates:
            self.empty_state.grid_remove()
            selected_index = next((index for index, candidate in enumerate(self._candidates) if candidate.get("record_id") == self._active_workspace.selected_record_id), None)
            if selected_index is not None:
                self.tree.selection_set(str(selected_index))
                self._show_preview(self._candidates[selected_index])
        self.case_count.set(self._case_label(len(self._candidates)))

    def _render_workspace_progress(self):
        workspace = self._active_workspace
        self._set_task_progress(workspace.progress_stage, None)

    def _set_window_icon(self):
        """Apply the packaged Windows icon without making startup depend on it."""
        icon_path = Path(__file__).resolve().parent / "assets" / "app.ico"
        try:
            if icon_path.is_file():
                self.root.iconbitmap(default=str(icon_path))
        except (tk.TclError, OSError):
            pass

    def _set_workspace_state(self, state):
        self._state = state
        self._set_mode_buttons()
        if hasattr(self, "case_tab_strip"):
            self._render_case_tabs()

    def _has_unsaved_work(self):
        return self._state in {WorkspaceState.EDITING, WorkspaceState.ANALYZED}

    def _load_todo_value(self, value):
        """Load a Case value without treating it as a user edit."""
        normalized = bool(value)
        self._todo_original_value = normalized
        self.todo_var.set(normalized)
        self._active_workspace.todo_current_value = normalized
        self._todo_dirty = False

    def _todo_clicked(self):
        # Only the Checkbutton command represents an explicit user action.
        self._todo_dirty = True
        self._active_workspace.todo_current_value = bool(self.todo_var.get())

    def _todo_value_for_update(self):
        return bool(self.todo_var.get()) if self._todo_dirty else None

    def _configure_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL, borderwidth=1, relief="flat", bordercolor=WEAK_BORDER)
        style.configure("Header.TFrame", background=BG, borderwidth=0, relief="flat")
        style.configure("Task.TFrame", background=PANEL_ALT, borderwidth=1, relief="flat", bordercolor=WEAK_BORDER)
        style.configure("Bottom.TFrame", background=BG, borderwidth=0, relief="flat")
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=BLUE, font=("Segoe UI Semibold", 11))
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TaskTitle.TLabel", background=PANEL_ALT, foreground=BLUE, font=("Segoe UI Semibold", 9))
        style.configure("Task.TLabel", background=PANEL_ALT, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("StatusTitle.TLabel", background=BG, foreground=DISABLED, font=("Segoe UI Semibold", 8))
        style.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TodoHelper.TLabel", background=PANEL, foreground=DISABLED, font=("Segoe UI", 8))
        style.configure("TEntry", fieldbackground=INPUT, foreground=TEXT, insertcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=(9, 7))
        style.map("TEntry", bordercolor=[("focus", BLUE)], lightcolor=[("focus", BLUE)])
        style.configure("TButton", background=PANEL, foreground=TEXT, bordercolor=BORDER, padding=(14, 7), font=("Segoe UI Semibold", 10), relief="flat")
        style.map("TButton", background=[("active", PANEL_ALT), ("disabled", PANEL_ALT)], foreground=[("disabled", DISABLED)], bordercolor=[("disabled", WEAK_BORDER), ("active", BLUE)])
        style.configure("Primary.TButton", background=BLUE, foreground="#FFFFFF", bordercolor=BLUE, padding=(15, 8))
        style.map("Primary.TButton", background=[("active", BLUE_HOVER), ("disabled", PANEL_ALT)], foreground=[("disabled", DISABLED), ("active", "#FFFFFF")], bordercolor=[("active", BLUE_HOVER), ("disabled", WEAK_BORDER)])
        style.configure("Secondary.TButton", background=PANEL, foreground=BLUE, bordercolor=BORDER, padding=(15, 7))
        style.map("Secondary.TButton", background=[("active", SELECTED), ("disabled", PANEL_ALT)], foreground=[("disabled", DISABLED), ("active", BLUE)], bordercolor=[("active", BLUE), ("disabled", WEAK_BORDER)])
        style.configure("Logiq.TButton", background="#E6FFFB", foreground="#0F766E", bordercolor="#0F766E", padding=(12, 7), font=("Segoe UI Semibold", 9))
        style.map("Logiq.TButton", background=[("active", "#CCFBF1")], foreground=[("active", "#115E59")])
        style.configure("HeaderSecondary.TButton", background=BG, foreground=MUTED, bordercolor=BG, padding=(15, 8))
        style.map("HeaderSecondary.TButton", background=[("active", PANEL_ALT)], foreground=[("active", BLUE), ("disabled", DISABLED)], bordercolor=[("active", WEAK_BORDER)])
        style.configure("HeaderPrimary.TButton", background=BLUE, foreground="#FFFFFF", bordercolor=BLUE, padding=(17, 8))
        style.map("HeaderPrimary.TButton", background=[("active", BLUE_HOVER), ("disabled", PANEL_ALT)], foreground=[("disabled", DISABLED), ("active", "#FFFFFF")], bordercolor=[("active", BLUE_HOVER), ("disabled", WEAK_BORDER)])
        style.configure("CaseTab.TButton", background=PANEL_ALT, foreground=MUTED, bordercolor=WEAK_BORDER, padding=(10, 5), font=("Segoe UI", 9))
        style.map("CaseTab.TButton", background=[("active", SELECTED)], foreground=[("active", BLUE)])
        style.configure("CaseTabActive.TButton", background=SELECTED, foreground=BLUE, bordercolor=BLUE, padding=(10, 5), font=("Segoe UI Semibold", 9))
        style.configure("Todo.TCheckbutton", background=PANEL, foreground="#344054", font=("Segoe UI", 10), indicatorcolor=INPUT, indicatormargin=(0, 0, 7, 0))
        style.map("Todo.TCheckbutton", foreground=[("disabled", DISABLED)], background=[("active", PANEL)], indicatorcolor=[("selected", BLUE), ("active", SELECTED)])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=30, bordercolor=WEAK_BORDER, relief="flat", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=TEXT, relief="flat", font=("Segoe UI Semibold", 9), padding=(8, 7))
        style.map("Treeview", background=[("selected", SELECTED)], foreground=[("selected", TEXT)])
        style.map("Treeview.Heading", background=[("active", "#F0F4F8")])
        style.configure("Horizontal.TSeparator", background=WEAK_BORDER)
        style.configure("Task.Horizontal.TProgressbar", troughcolor=WEAK_BORDER, background=BLUE, bordercolor=WEAK_BORDER, lightcolor=BLUE, darkcolor=BLUE, thickness=5)
        style.configure("Vertical.TScrollbar", background="#C7D2E0", troughcolor=PANEL_ALT, bordercolor=PANEL_ALT, arrowcolor=MUTED, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", "#AEBCCC"), ("pressed", "#AEBCCC")])

    def _build(self):
        shell = ttk.Frame(self.root, padding=(20, 16, 20, 10), style="TFrame")
        shell.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(5, weight=0, minsize=0)
        shell.rowconfigure(6, weight=1, minsize=0)
        shell.rowconfigure(8, weight=0, minsize=30)

        header = ttk.Frame(shell, padding=(0, 0, 0, 4), style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.new_case_button = ttk.Button(header, text="+ NEW CASE", command=self._new_case, style="HeaderPrimary.TButton")
        self.new_case_button.grid(row=0, column=2, sticky="e")
        self.today_button = ttk.Button(header, text="TODAY", command=self._open_today, style="HeaderSecondary.TButton")
        self.today_button.grid(row=0, column=1, sticky="e", padx=(0, 8))

        ttk.Separator(shell, orient="horizontal").grid(row=1, column=0, sticky="ew")
        self.case_tab_strip = ttk.Frame(shell, style="TFrame")
        self.case_tab_strip.grid(row=2, column=0, sticky="ew", pady=(7, 3))
        self._render_case_tabs()
        tab_strip = tk.Frame(shell, bg=BG)
        self.tab_strip = tab_strip
        tab_strip.grid(row=3, column=0, sticky="ew", pady=(3, 8))
        for column, (label, value) in enumerate((("NEXTOP", "nextop"), ("WHATSAPP", "whatsapp"), ("LARK", "lark"), ("EMAIL", "email"))):
            tab_shell = tk.Frame(tab_strip, bg=BG)
            tab_shell.grid(row=0, column=column, sticky="w")
            tab = tk.Label(tab_shell, text=label, bg=BG, fg=MUTED, font=("Segoe UI Semibold", 10), padx=17, pady=8, cursor="hand2")
            tab.grid(row=0, column=0, sticky="ew")
            indicator = tk.Frame(tab_shell, height=2, bg=BORDER)
            indicator.grid(row=1, column=0, sticky="ew")
            for widget in (tab_shell, tab, indicator):
                widget.bind("<Button-1>", lambda _event, mode=value: self._select_source(mode))
            self._tabs[value] = (tab, indicator)
        self._refresh_tabs()

        self.task_kind = tk.StringVar(value="READY")
        self.task_detail = tk.StringVar(value="Waiting for input.")
        self.task_strip = ttk.Frame(shell, padding=(12, 5), style="Task.TFrame")
        self.task_strip.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(self.task_strip, textvariable=self.task_kind, style="TaskTitle.TLabel").grid(row=0, column=0, padx=(0, 12))
        ttk.Label(self.task_strip, textvariable=self.task_detail, style="Task.TLabel").grid(row=0, column=1, sticky="w")
        self.progress_label = ttk.Label(self.task_strip, textvariable=self.progress_percent, style="TaskTitle.TLabel")
        self.progress_label.grid(row=0, column=2, sticky="e")
        self.task_strip.columnconfigure(1, weight=1)
        self.progress_bar = ttk.Progressbar(self.task_strip, variable=self.progress_value, maximum=100, mode="determinate", style="Task.Horizontal.TProgressbar")
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))

        self.input_panel = ttk.Frame(shell, padding=(18, 14), style="Panel.TFrame")
        self.input_panel.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        self.input_panel.columnconfigure(0, weight=1)

        self.candidate_panel = ttk.Frame(shell, padding=(14, 12), style="Panel.TFrame")
        self.candidate_panel.grid(row=6, column=0, sticky="nsew")
        self.candidate_panel.columnconfigure(0, weight=1)
        self.candidate_panel.rowconfigure(1, weight=1)
        self.candidate_panel.rowconfigure(2, weight=0, minsize=54)
        title = ttk.Frame(self.candidate_panel, style="Panel.TFrame")
        title.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        title.columnconfigure(0, weight=1)
        self.panel_title = ttk.Label(title, text="CANDIDATE CASES", style="PanelTitle.TLabel")
        self.panel_title.grid(row=0, column=0, sticky="w")
        self.today_search_var = tk.StringVar()
        self.today_search_var.trace_add("write", lambda *_: self._render_today(self.today_search_var.get()) if self._view_mode == "today" else None)
        self.today_search_entry = ttk.Entry(title, textvariable=self.today_search_var, width=28)
        self.panel_count = ttk.Label(title, textvariable=self.case_count, style="Muted.TLabel")
        self.panel_count.grid(row=0, column=2, sticky="e")

        browser = tk.PanedWindow(self.candidate_panel, orient="horizontal", bg=WEAK_BORDER, sashwidth=6, showhandle=False, bd=0, relief="flat")
        browser.grid(row=1, column=0, sticky="nsew")
        list_shell = tk.Frame(browser, bg=PANEL)
        preview_shell = tk.Frame(browser, bg=PANEL)
        browser.add(list_shell, minsize=380)
        browser.add(preview_shell, minsize=500)
        list_shell.columnconfigure(0, weight=1); list_shell.rowconfigure(0, weight=1)
        preview_shell.columnconfigure(0, weight=1); preview_shell.rowconfigure(1, weight=1)
        columns = ("ticket", "dealer", "model", "last_reply")
        self.tree = ttk.Treeview(list_shell, columns=columns, show="headings", selectmode="browse")
        headings = {"ticket": "Ticket No.", "dealer": "Dealer", "model": "Model", "last_reply": "Last Reply"}
        widths = {"ticket": 115, "dealer": 120, "model": 120, "last_reply": 125}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], minwidth=70, stretch=column == "issue")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_shell, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._candidate_selected)
        self.empty_state = tk.Label(list_shell, text="No candidates yet.", justify="center", bg=PANEL, fg=MUTED, font=("Segoe UI", 10))
        ttk.Label(preview_shell, text="CASE PREVIEW", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))
        self.preview = tk.Text(preview_shell, wrap="word", bg=PANEL, fg="#344054", insertbackground=TEXT, relief="flat", highlightthickness=0, font=("Segoe UI", 10), padx=12, pady=8, state="disabled")
        self.preview.grid(row=1, column=0, sticky="nsew")
        preview_scroll = ttk.Scrollbar(preview_shell, orient="vertical", command=self.preview.yview)
        preview_scroll.grid(row=1, column=1, sticky="ns")
        self.preview.configure(yscrollcommand=preview_scroll.set)
        self.tree.bind("<MouseWheel>", self._scroll_tree)
        self.preview.bind("<MouseWheel>", self._scroll_preview)

        candidate_actions = ttk.Frame(self.candidate_panel, style="Panel.TFrame")
        self.candidate_actions = candidate_actions
        candidate_actions.grid(row=2, column=0, pady=(10, 0), sticky="ew")
        candidate_actions.columnconfigure(0, weight=1)
        ttk.Separator(candidate_actions, orient="horizontal").grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        todo_group = ttk.Frame(candidate_actions, style="Panel.TFrame")
        todo_group.grid(row=1, column=0, sticky="w")
        self.todo_checkbutton = ttk.Checkbutton(todo_group, text="Add to ITR Todo", variable=self.todo_var, command=self._todo_clicked, style="Todo.TCheckbutton")
        self.todo_checkbutton.grid(row=0, column=0, sticky="w")
        self.update_button = ttk.Button(candidate_actions, text="UPDATE SELECTED CASE", command=self._update_selected, state="disabled")
        self.create_button = ttk.Button(candidate_actions, text="+ CREATE NEW CASE", command=self._create_manual, style="Primary.TButton", state="disabled")
        self.update_button.grid(row=1, column=1, padx=(0, 10))
        self.create_button.grid(row=1, column=2)

        # Reused Inspector surface.  It is rendered only for Existing/Prepared
        # workspaces; New Case continues to use the input/candidate layout.
        self.inspector_panel = ttk.Frame(shell, padding=(14, 12), style="Panel.TFrame")
        self.inspector_panel.grid(row=5, column=0, rowspan=2, sticky="nsew")
        self.inspector_panel.columnconfigure(0, weight=1)
        self.inspector_panel.rowconfigure(1, weight=1)
        inspector_title = ttk.Frame(self.inspector_panel, style="Panel.TFrame")
        inspector_title.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        inspector_title.columnconfigure(0, weight=1)
        self.inspector_commit_button = ttk.Button(inspector_title, text="UPDATE ITR", command=self._commit_prepared_nextop, style="Primary.TButton")
        self.inspector_commit_button.grid(row=0, column=1, sticky="e")
        self.inspector_todo_checkbutton = ttk.Checkbutton(inspector_title, text="Add to ITR Todo", variable=self.todo_var, command=self._todo_clicked, style="Todo.TCheckbutton")
        self.inspector_todo_checkbutton.grid(row=1, column=1, sticky="e", pady=(3, 0))
        self.inspector_browser = tk.PanedWindow(self.inspector_panel, orient="horizontal", bg=WEAK_BORDER, sashwidth=6, showhandle=False, bd=0, relief="flat")
        self.inspector_browser.grid(row=1, column=0, sticky="nsew")
        self.inspector_left = tk.Frame(self.inspector_browser, bg=PANEL)
        self.inspector_center = tk.Frame(self.inspector_browser, bg=PANEL)
        self.inspector_browser.add(self.inspector_left, minsize=230)
        self.inspector_browser.add(self.inspector_center, minsize=520)
        self.inspector_browser.bind("<Configure>", self._place_inspector_sashes)
        self.inspector_panel.grid_remove()

        ttk.Separator(shell, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=(10, 0))
        self.status_bar = ttk.Frame(shell, padding=(2, 6, 2, 2), style="Bottom.TFrame")
        self.status_bar.grid(row=8, column=0, sticky="ew")
        ttk.Label(self.status_bar, text="STATUS", style="StatusTitle.TLabel").grid(row=0, column=0, padx=(0, 12))
        ttk.Label(self.status_bar, textvariable=self.bottom_status, style="Status.TLabel").grid(row=0, column=1, sticky="w")
        self.status_bar.columnconfigure(1, weight=1)
        self._render_workspace_view()
        self._set_mode_buttons()

    def _place_inspector_sashes(self, event=None):
        """Keep the center analysis pane dominant without fixing pixel widths."""
        try:
            width = max(1, self.inspector_browser.winfo_width())
            self.inspector_browser.sash_place(0, min(320, max(230, int(width * .24))), 0)
        except tk.TclError:
            pass

    def _render_workspace_view(self):
        """Single visibility router for the shared active-content widgets."""
        if self._view_mode == "today":
            return
        self.inspector_panel.grid_remove()
        self.input_panel.grid_remove()
        self.candidate_panel.grid_remove()
        self.tab_strip.grid_remove()
        if self._is_inspector_workspace():
            self._render_inspector()
            return
        self.tab_strip.grid()
        self.input_panel.master.rowconfigure(5, weight=0, minsize=0)
        self.input_panel.master.rowconfigure(6, weight=1, minsize=0)
        self.input_panel.grid()
        self._render_input()

    def _clear_panel(self, panel):
        for child in panel.winfo_children():
            child.destroy()

    def _scrollable_panel(self, parent, title):
        parent.columnconfigure(0, weight=1); parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text=title, style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w", padx=12, pady=(11, 5))
        canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        inner = ttk.Frame(canvas, padding=(12, 4, 12, 12), style="Panel.TFrame")
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        canvas.bind("<MouseWheel>", lambda event: (canvas.yview_scroll(-3 * max(1, abs(int(event.delta / 120)) if event.delta else 1) * (1 if event.delta < 0 else -1), "units"), "break")[1])
        return inner

    def _inspector_section(self, parent, row, title, value, *, inferred=False):
        if value in (None, "", []):
            return row
        heading = ttk.Frame(parent, style="Panel.TFrame")
        heading.grid(row=row, column=0, sticky="ew", pady=((11 if row else 0), 3))
        ttk.Label(heading, text=title, style="PanelTitle.TLabel").pack(side="left")
        if inferred:
            ttk.Label(heading, text="INFERRED", style="Muted.TLabel").pack(side="left", padx=(7, 0))
        text = "\n".join(f"• {item}" for item in value) if isinstance(value, list) else str(value)
        ttk.Label(parent, text=text, style="Muted.TLabel", justify="left", wraplength=600).grid(row=row + 1, column=0, sticky="ew")
        return row + 2

    @staticmethod
    def _analysis_value(analysis, name, default=None):
        if isinstance(analysis, dict):
            return analysis.get(name, default)
        return getattr(analysis, name, default)

    def _render_inspector(self):
        self.input_panel.grid_remove()
        self.candidate_panel.grid_remove()
        self.tab_strip.grid_remove()
        self.input_panel.master.rowconfigure(5, weight=1, minsize=0)
        self.input_panel.master.rowconfigure(6, weight=0, minsize=0)
        self.inspector_panel.grid()
        for panel in (self.inspector_left, self.inspector_center):
            self._clear_panel(panel)
        case = self._current_case or {}
        left = self._scrollable_panel(self.inspector_left, "CASE CONTEXT")
        left.columnconfigure(0, weight=1)
        row = 0
        context = (("ITR TICKET NO.", case.get("ticket_no")), ("REFERENCE NO.", case.get("reference_no")),
                   ("SOURCE", case.get("reference_no")), ("DEALER", case.get("disti")),
                   ("MODEL", case.get("model_type")), ("DEVICE", case.get("device_name")),
                   ("STATUS", case.get("status")),
                   ("L1 TAG", case.get("first_level_tag")),
                   ("L2 TAG", f"{case.get('second_level_tag')}    {case.get('case_count')} CASES" if case.get("second_level_tag") and case.get("case_count") not in (None, "") else case.get("second_level_tag")),
                   ("FAULT SYMPTOM", ", ".join(case.get("fault_symptom") or [])),
                   ("ERROR CODE", ", ".join(case.get("error_codes") or [])))
        for label, value in context:
            row = self._inspector_section(left, row, label, value)
        ttk.Label(left, text="SESSION NOTES", style="PanelTitle.TLabel").grid(row=row, column=0, sticky="w", pady=(8, 0)); row += 1
        ttk.Label(left, text="Session only", style="Muted.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 3)); row += 1
        notes = tk.Text(left, height=3, wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat", highlightthickness=1, highlightbackground=BORDER, font=("Segoe UI", 9), padx=7, pady=6)
        notes.insert("1.0", self._active_workspace.notes)
        notes.grid(row=row, column=0, sticky="ew")
        notes.bind("<<Modified>>", self._inspector_notes_changed)

        center = self._scrollable_panel(self.inspector_center, "CASE REVIEW")
        center.columnconfigure(0, weight=1)
        workspace = self._active_workspace
        analysis = workspace.analysis_result
        if not analysis:
            ttk.Label(center, text="Analyze this case to generate a structured review.", style="Muted.TLabel", wraplength=600, justify="left").grid(row=0, column=0, sticky="w", pady=(8, 12))
            controls = ttk.Frame(center, style="Panel.TFrame")
            controls.grid(row=1, column=0, sticky="ew")
            controls.columnconfigure(0, weight=1)
            self.inspector_analyze_button = ttk.Button(controls, text="ANALYZE CASE", command=self._analyze_inspector_case, style="Secondary.TButton")
            self.inspector_analyze_button.grid(row=0, column=0, sticky="w")
            ttk.Button(controls, text="LOGIQ · OPEN LOGS", command=self._open_logiq, style="Logiq.TButton").grid(row=0, column=1, sticky="e")
        else:
            controls = ttk.Frame(center, style="Panel.TFrame")
            controls.grid(row=0, column=0, sticky="ew", pady=(2, 7))
            controls.columnconfigure(0, weight=1)
            self.inspector_analyze_button = ttk.Button(controls, text="RE-ANALYZE", command=self._analyze_inspector_case, style="Secondary.TButton")
            self.inspector_analyze_button.grid(row=0, column=0, sticky="w")
            original = ttk.Button(controls, text="ORIGINAL", command=lambda: self._select_analysis_language("ORIGINAL"), style="Secondary.TButton")
            original.grid(row=0, column=1, padx=(6, 0))
            chinese = ttk.Button(controls, text="中文", command=lambda: self._select_analysis_language("ZH"), style="Secondary.TButton")
            chinese.grid(row=0, column=2, padx=(5, 0))
            device = case.get("device_name") or ""
            ttk.Label(controls, text=f"Device: {device}" if device else "Device unavailable", style="Muted.TLabel").grid(row=0, column=3, padx=(14, 6))
            ttk.Button(controls, text="LOGIQ · OPEN LOGS", command=self._open_logiq, style="Logiq.TButton").grid(row=0, column=4, sticky="e")
            display = workspace.translation_result if workspace.analysis_language == "ZH" and workspace.translation_source_hash == self._analysis_value(analysis, "source_hash") else analysis
            def display_value(name):
                original = self._analysis_value(analysis, name)
                value = self._analysis_value(display, name)
                return "Translation unavailable." if workspace.analysis_language == "ZH" and original not in (None, "", []) and value in (None, "", []) else value
            row = 1
            row = self._inspector_section(center, row, "CUSTOMER ISSUE", display_value("customer_description"))
            actions = display_value("repair_actions") or "No confirmed repair action recorded."
            row = self._inspector_section(center, row, "REPAIR / TROUBLESHOOTING ACTIONS", actions)
            row = self._inspector_section(center, row, "CURRENT BLOCKER", display_value("current_blocker"), inferred=bool(self._analysis_value(analysis, "blocker_is_inferred", False)))
            recommendations = display_value("historical_pie_recommendations") or "No previous PIE guidance recorded."
            row = self._inspector_section(center, row, "PREVIOUS PIE GUIDANCE", recommendations)
            row = self._inspector_section(center, row, "CURRENT ASSESSMENT / NEXT STEP" if self._analysis_value(analysis, "historical_pie_recommendations") else "SUGGESTED NEXT STEP", display_value("ai_suggested_next_step"))
            solution_titles = {"FINAL": "FINAL SOLUTION", "CURRENT": "CURRENT SOLUTION", "WORKAROUND": "WORKAROUND", "PENDING": "PENDING ACTION", "NONE": "NO CONFIRMED SOLUTION"}
            solution_state = self._analysis_value(analysis, "solution_state", "NONE")
            row = self._inspector_section(center, row, f"SOLUTION STATE    {solution_state}", display_value("solution") or ("No confirmed solution." if solution_state == "NONE" else None))
            reply = self._analysis_value(analysis, "reply_en")
            reply_header = ttk.Frame(center, style="Panel.TFrame")
            reply_header.grid(row=row, column=0, sticky="ew", pady=(11, 3))
            ttk.Label(reply_header, text="REPLY (ENGLISH)", style="PanelTitle.TLabel").pack(side="left")
            ttk.Button(reply_header, text="COPY", command=self._copy_reply, style="Secondary.TButton", state="normal" if reply else "disabled").pack(side="right")
            if reply:
                email = tk.Text(center, height=10, wrap="word", bg="#EEF5FF", fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=BORDER, font=("Segoe UI", 10), padx=10, pady=8)
                email.insert("1.0", reply)
                email.configure(state="disabled")
                email.grid(row=row + 1, column=0, sticky="ew")
        self._set_mode_buttons()

    def _inspector_notes_changed(self, event=None):
        widget = event.widget if event else None
        if widget and widget.edit_modified():
            self._active_workspace.notes = widget.get("1.0", "end-1c")
            widget.edit_modified(False)

    def _select_analysis_language(self, language):
        workspace = self._active_workspace
        analysis = workspace.analysis_result
        if not analysis or language == workspace.analysis_language:
            return
        if language == "ORIGINAL":
            workspace.analysis_language = "ORIGINAL"
            self._render_inspector()
            return
        source_hash = self._analysis_value(analysis, "source_hash")
        if workspace.translation_source_hash == source_hash and workspace.translation_result is not None:
            workspace.analysis_language = "ZH"
            self._render_inspector()
            return
        self._set_workspace_state(WorkspaceState.ANALYZING)
        workspace.timings["translation_started"] = perf_counter()
        def operation(value, progress_callback=None):
            return case_service.translate_inspector_analysis_to_zh(value)
        self._start_task(operation, analysis, completion=self._show_inspector_translation)
        self._set_task_progress("analysis", "Translating analysis.")

    def _show_inspector_translation(self, result):
        if isinstance(result, dict) and result.get("success") is False:
            self._set_workspace_state(WorkspaceState.REVIEW_READY)
            self._show_failure("Translation failed", result)
            return
        workspace = self._active_workspace
        workspace.translation_source_hash = self._analysis_value(workspace.analysis_result, "source_hash")
        workspace.translation_result = result
        workspace.translation_cache[workspace.translation_source_hash] = result
        workspace.analysis_language = "ZH"
        if workspace.timings.get("translation_started"):
            workspace.timings["translation_seconds"] = perf_counter() - workspace.timings["translation_started"]
        self._set_workspace_state(WorkspaceState.REVIEW_READY)
        self._render_inspector()
        self._set_task_progress("review_ready", "Chinese translation ready.")

    def _copy_reply(self):
        reply = self._analysis_value(self._active_workspace.analysis_result, "reply_en")
        if not reply:
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(reply))
            self.root.update_idletasks()
            self.status.set("READY FOR REVIEW — Reply copied to clipboard.")
        except tk.TclError:
            self.status.set("WARNING — Unable to copy reply.")

    def _open_logiq(self):
        workspace = self._active_workspace
        device = str((self._current_case or {}).get("device_name") or "").strip()
        try:
            if device:
                self.root.clipboard_clear()
                self.root.clipboard_append(device)
                self.root.update_idletasks()
            opened = webbrowser.open(LOGIQ_URL)
            if opened is False:
                raise RuntimeError("browser unavailable")
            workspace.logiq_session_state = "OPENED"
            self.status.set("READY FOR REVIEW — Device name copied. LogiQ opened." if device else "READY FOR REVIEW — LogiQ opened. No device name available for automatic log lookup.")
        except Exception:
            self.status.set("WARNING — Unable to open LogiQ.")

    def _analyze_inspector_case(self):
        if self._running or not self._current_case:
            return
        self._set_workspace_state(WorkspaceState.ANALYZING)
        self._active_workspace.timings["inspector_analyze_started"] = perf_counter()
        def operation(case, progress_callback=None):
            return case_service.analyze_existing_case_for_inspector(case)
        self._start_task(operation, dict(self._current_case), completion=self._show_inspector_analysis)
        self._set_task_progress("analysis", "Analyzing case.")

    def _show_inspector_analysis(self, result):
        # The backend returns its DTO directly; a worker exception is converted
        # to the standard safe failure shape by _start_task.
        if isinstance(result, dict) and result.get("success") is False:
            self._set_workspace_state(WorkspaceState.REVIEW_READY)
            self._show_failure("Analysis failed", result)
            return
        workspace = self._active_workspace
        old_hash = self._analysis_value(workspace.analysis_result, "source_hash")
        new_hash = self._analysis_value(result, "source_hash")
        workspace.analysis_result = result
        if workspace.timings.get("inspector_analyze_started"):
            workspace.timings["inspector_analyze_seconds"] = perf_counter() - workspace.timings["inspector_analyze_started"]
        if old_hash != new_hash:
            workspace.translation_cache.clear()
            workspace.translation_source_hash = None
            workspace.translation_result = None
        workspace.analysis_language = "ORIGINAL"
        self._set_workspace_state(WorkspaceState.REVIEW_READY)
        self._render_inspector()
        self._set_task_progress("review_ready", "Ready for review.")
        if getattr(self, "preferred_analysis_language", "ZH") == "ZH":
            self._select_analysis_language("ZH")

    def _refresh_tabs(self):
        for mode, (tab, indicator) in self._tabs.items():
            active = mode == self.source.get()
            tab.configure(fg=BLUE if active else MUTED, bg=BG)
            indicator.configure(bg=BLUE if active else WEAK_BORDER)

    def _sync_task_strip(self, *_args):
        text = self.status.get() or "READY — Waiting for input."
        kind, separator, detail = text.partition("—")
        self.task_kind.set(kind.strip() or "READY")
        self.task_detail.set(detail.strip() if separator else text)
        state = (kind.strip() or "READY").upper()
        self.bottom_status.set("READY" if state in {"COMPLETE", "TODAY"} else state)
        if self._active_workspace_id:
            self._active_workspace.status_text = text

    def _set_task_progress(self, stage, detail=None):
        """Single main-thread owner of stage text, percentage, and bar value."""
        state, percent = PROGRESS_STAGES.get(stage, (None, None))
        if percent is not None:
            self.progress_value.set(percent)
            self.progress_percent.set(f"{percent}%")
        if self._active_workspace_id:
            self._active_workspace.progress_stage = stage
            if percent is not None:
                self._active_workspace.progress_percent = percent
            if detail is not None:
                self._active_workspace.progress_detail = detail
        show = stage not in {"ready", "today", "prepared", "review_ready"}
        if show and self._view_mode != "today":
            self.progress_label.grid(row=0, column=2, sticky="e")
            self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        else:
            self.progress_label.grid_remove()
            self.progress_bar.grid_remove()
        if state and detail is not None:
            self.status.set(f"{state} — {detail}")

    def _reset_task_progress(self):
        self._set_task_progress("ready")

    def _select_source(self, mode):
        if self._loading_workspace:
            return
        if self._running:
            return
        if self._view_mode == "today":
            self._leave_today(mode)
            self.status.set(f"READY — New {self._source_label(mode)} Case")
            return
        if mode == self.source.get():
            return
        if self._has_unsaved_work() and not messagebox.askyesno("Unsaved input", f"Current input has not been saved. Discard it and switch to {self._source_label(mode)}?"):
            return
        self.source.set(mode)
        self._reset_workspace()
        self._refresh_tabs()
        self._render_input()
        self._set_mode_buttons()
        self.status.set(f"READY — New {self._source_label(mode)} Case")

    def _new_case(self):
        if self._running:
            return
        if self._view_mode == "today":
            self._leave_today(self.source.get())
        workspace = self._create_workspace(self.source.get(), activate=True)
        self.status.set(f"READY — New {self._source_label(workspace.source)} {'Ticket' if workspace.source == 'nextop' else 'Case'}")

    def _open_today(self):
        if self._running:
            return
        if self._has_unsaved_work() and not messagebox.askyesno("Unsaved input", "Current input has not been saved. Discard it and open Today?"):
            return
        if self._view_mode != "today":
            self._reset_workspace()
        self._view_mode = "today"
        self._set_workspace_state(WorkspaceState.VIEWING_HISTORY)
        self.input_panel.grid_remove()
        self.tab_strip.grid_remove()
        self.case_tab_strip.grid_remove()
        self.input_panel.master.rowconfigure(5, weight=1, minsize=0)
        self.input_panel.master.rowconfigure(6, weight=0, minsize=0)
        self.candidate_panel.grid_configure(row=5)
        self.progress_bar.grid_remove()
        self.progress_label.grid_remove()
        self._show_candidate_panel(True)
        self.candidate_actions.grid_remove()
        self._configure_today_columns()
        self.panel_title.configure(text="TODAY")
        self.today_search_entry.grid(row=0, column=1, sticky="e", padx=(0, 10))
        self._render_today()
        count = len(self._today_cases)
        self.status.set(f"TODAY — {count} {'Case' if count == 1 else 'Cases'} processed this session")

    def _leave_today(self, mode):
        self._view_mode = "workspace"
        self.source.set(mode)
        self._configure_workspace_columns()
        self.panel_title.configure(text="CANDIDATE CASES")
        self.today_search_entry.grid_remove()
        self.candidate_panel.grid_configure(row=6)
        self.input_panel.master.rowconfigure(5, weight=0, minsize=0)
        self.input_panel.master.rowconfigure(6, weight=1, minsize=0)
        self.case_tab_strip.grid()
        self.tab_strip.grid()
        self.candidate_actions.grid()
        self.input_panel.grid()
        self.progress_label.grid(row=0, column=2, sticky="e")
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        self._refresh_tabs()
        self._render_input()
        self._reset_workspace()

    def _configure_workspace_columns(self):
        columns = ("ticket", "dealer", "model", "last_reply")
        headings = ("Ticket No.", "Dealer", "Model", "Last Reply")
        widths = (115, 120, 120, 125)
        self.tree.configure(columns=columns)
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, minwidth=70, stretch=True)

    def _configure_today_columns(self):
        columns = ("ticket", "source", "dealer", "model", "status", "last_action")
        headings = ("Ticket No.", "Source", "Dealer", "Model", "Status", "Last Action")
        widths = (105, 85, 110, 110, 95, 125)
        self.tree.configure(columns=columns)
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, minwidth=65, stretch=True)

    def _record_today_case(self, result, case=None):
        case = dict(case or result.get("created_case") or result.get("updated_case") or result.get("case") or {})
        record_id = result.get("record_id") or case.get("record_id")
        if not record_id:
            return
        case["record_id"] = record_id
        case.setdefault("ticket_no", result.get("ticket_no"))
        case.setdefault("reference_no", str(result.get("source") or self.source.get()).upper())
        case["channel"] = "NEXTOP" if result.get("ticket_no") else str(result.get("source") or self.source.get()).upper()
        case["last_action"] = "CREATED" if result.get("action") == "created" else "UPDATED"
        if result.get("case_count") is not None:
            case["case_count"] = result["case_count"]
        case["last_session_action_time"] = time.time()
        self._today_cases[record_id] = case

    def _render_today(self, query=""):
        query = query.strip().casefold()
        values = list(self._today_cases.values())
        if query:
            exact = [item for item in values if str(item.get("ticket_no") or "").casefold() == query]
            values = exact or [item for item in values if query in " ".join(str(item.get(key) or "") for key in ("ticket_no", "reference_no", "disti", "model_type")).casefold()]
        self._today_visible = sorted(values, key=lambda item: item.get("last_session_action_time", 0), reverse=True)
        self._clear_candidates()
        for index, item in enumerate(self._today_visible):
            self.tree.insert("", "end", iid=str(index), values=(item.get("ticket_no") or "-", item.get("reference_no") or "-", item.get("disti") or "", item.get("model_type") or "", item.get("status") or "", f"{item.get('last_action', '')} {time.strftime('%H:%M', time.localtime(item.get('last_session_action_time', 0)))}".strip()))
        if self._today_visible:
            self.empty_state.grid_remove()
        else:
            self.empty_state.configure(text="No Cases processed today.")
        self.case_count.set(self._case_label(len(self._today_visible)))

    def _reset_workspace(self):
        self._draft, self._candidates = None, []
        self._active_workspace.prepared_case = None
        self._current_case = None
        self._load_todo_value(False)
        self.ticket_no.set("")
        if getattr(self, "manual_text", None):
            self.manual_text.delete("1.0", "end")
        self._clear_candidates()
        self._reset_task_progress()
        self._set_workspace_state(WorkspaceState.EMPTY)
        focus = getattr(self, "manual_text", None)
        if focus: focus.focus_set()

    def _render_input(self):
        for child in self.input_panel.winfo_children():
            child.destroy()
        if self.source.get() == "nextop":
            self.input_panel.columnconfigure(0, weight=1)
            self.input_panel.columnconfigure(1, weight=0)
            ttk.Label(self.input_panel, text="NEXTOP TICKET", style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
            ttk.Label(self.input_panel, text="Nextop Ticket No.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(9, 4))
            entry = ttk.Entry(self.input_panel, textvariable=self.ticket_no, width=42)
            entry.grid(row=2, column=0, sticky="ew", padx=(0, 12))
            self.sync_button = ttk.Button(self.input_panel, text="SEARCH / LOAD", command=self._prepare_nextop, style="Secondary.TButton", width=15)
            self.sync_button.grid(row=2, column=1, sticky="e")
            entry.bind("<Return>", lambda _event: self._prepare_nextop())
            self.nextop_commit_button = ttk.Button(self.input_panel, text="CREATE IN ITR", command=self._commit_prepared_nextop, style="Primary.TButton", state="disabled")
            self.nextop_commit_button.grid(row=2, column=2, sticky="e", padx=(10, 0))
            todo_group = ttk.Frame(self.input_panel, style="Panel.TFrame")
            todo_group.grid(row=3, column=0, columnspan=2, sticky="w", pady=(13, 0))
            self.todo_checkbutton_nextop = ttk.Checkbutton(todo_group, text="Add to ITR Todo", variable=self.todo_var, command=self._todo_clicked, style="Todo.TCheckbutton")
            self.todo_checkbutton_nextop.grid(row=0, column=0, sticky="w")
            self.analyze_button = None
            self.manual_text = None
            if self._nextop_auth_required:
                auth = ttk.Frame(self.input_panel, style="Panel.TFrame")
                auth.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
                ttk.Label(auth, text="AUTHENTICATION REQUIRED", style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
                ttk.Label(auth, text="Paste the latest PageOrder request from Nextop.", style="Muted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 5))
                self.pageorder_entry = ttk.Entry(auth, show="•", width=58)
                self.pageorder_entry.grid(row=2, column=0, sticky="w", padx=(0, 8))
                self.refresh_session_button = ttk.Button(auth, text="REFRESH SESSION", command=self._refresh_nextop_session)
                self.refresh_session_button.grid(row=2, column=1, sticky="e")
                self.sync_button.configure(state="disabled")
            else:
                self.pageorder_entry = None
                self.refresh_session_button = None
            if self._current_case:
                summary_outer = ttk.Frame(self.input_panel, style="Panel.TFrame")
                summary_outer.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
                summary_outer.columnconfigure(0, weight=1)
                summary_outer.rowconfigure(1, weight=1)
                ttk.Label(summary_outer, text="CURRENT CASE", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
                summary_canvas = tk.Canvas(summary_outer, bg=PANEL, highlightthickness=0, height=250)
                summary_canvas.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
                summary_scroll = ttk.Scrollbar(summary_outer, orient="vertical", command=summary_canvas.yview)
                summary_scroll.grid(row=1, column=1, sticky="ns", pady=(5, 0))
                summary_canvas.configure(yscrollcommand=summary_scroll.set)
                summary = ttk.Frame(summary_canvas, style="Panel.TFrame")
                summary_window = summary_canvas.create_window((0, 0), window=summary, anchor="nw")
                summary.bind("<Configure>", lambda _event: summary_canvas.configure(scrollregion=summary_canvas.bbox("all")))
                summary_canvas.bind("<Configure>", lambda event: summary_canvas.itemconfigure(summary_window, width=event.width))
                case = self._current_case
                ttk.Label(summary, text=f"{case.get('ticket_no') or '-'}  ·  {case.get('reference_no') or '-'}", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))
                details = []
                for label, key in (("Dealer", "disti"), ("Model", "model_type"), ("Status", "status"), ("Device", "device_name"), ("Created", "ticket_created_time")):
                    value = case.get(key)
                    if key.endswith("time") or key == "ticket_created_time": value = case_service.format_time(value)
                    if value not in (None, "", [], "-"): details.append(f"{label}: {value}")
                if case.get("include_itr_todo"):
                    details.append("ADD TO ITR TODO: YES")
                ttk.Label(summary, text="   ·   ".join(details[:3]), style="Muted.TLabel", wraplength=900, justify="left").grid(row=2, column=0, sticky="w", pady=(5, 0))
                if len(details) > 3:
                    ttk.Label(summary, text="   ·   ".join(details[3:]), style="Muted.TLabel", wraplength=900, justify="left").grid(row=3, column=0, sticky="w", pady=(3, 0))
                text_row = 4
                for label, key in (("L2 TAG", "second_level_tag"), ("FAULT SYMPTOM", "fault_symptom"), ("PIE COMMENT", "pie_comment"), ("SOLUTIONS", "solutions")):
                    if case.get(key):
                        ttk.Label(summary, text=label, style="PanelTitle.TLabel").grid(row=text_row, column=0, sticky="w", pady=(10, 4))
                        value = ", ".join(case[key]) if isinstance(case[key], list) else str(case[key])
                        if label == "L2 TAG" and case.get("case_count") not in (None, ""):
                            value = f"{value}    {case['case_count']} CASES"
                        ttk.Label(summary, text=value, style="Muted.TLabel", wraplength=900, justify="left").grid(row=text_row + 1, column=0, sticky="w")
                        text_row += 2
            entry.focus_set()
        else:
            self.input_panel.columnconfigure(0, weight=1)
            self.input_panel.rowconfigure(2, weight=1)
            self.input_panel.rowconfigure(3, weight=0, minsize=42)
            ttk.Label(self.input_panel, text="NEW COMMUNICATION", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(self.input_panel, text="Paste only new communication since last import.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 8))
            editor = tk.Frame(self.input_panel, bg=INPUT, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE)
            editor.grid(row=2, column=0, sticky="nsew")
            editor.columnconfigure(0, weight=1)
            editor.rowconfigure(0, weight=1)
            self.manual_text = tk.Text(editor, height=5, wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat", highlightthickness=0, font=("Segoe UI", 10), padx=11, pady=9)
            self.manual_text.grid(row=0, column=0, sticky="nsew")
            editor_scroll = ttk.Scrollbar(editor, orient="vertical", command=self.manual_text.yview)
            editor_scroll.grid(row=0, column=1, sticky="ns")
            self.manual_text.configure(yscrollcommand=editor_scroll.set)
            button_row = ttk.Frame(self.input_panel, style="Panel.TFrame")
            button_row.grid(row=3, column=0, pady=(11, 2), sticky="e")
            self.analyze_button = ttk.Button(button_row, text="ANALYZE & FIND CASES", command=self._prepare_manual, style="Secondary.TButton")
            self.analyze_button.grid(row=0, column=0)
            self.sync_button = None
            self.nextop_commit_button = None
            self.manual_text.focus_set()
            self.manual_text.bind("<<Modified>>", self._manual_input_changed)
        self._show_candidate_panel(self.source.get() in MANUAL_SOURCES)

    def _show_candidate_panel(self, show):
        if show:
            # Keep the communication editor usable before Candidate Cases receive
            # remaining height.  Grid is deliberately used instead of a vertical
            # PanedWindow so Today can continue to remove the top workspace safely.
            self.candidate_panel.master.rowconfigure(5, weight=0, minsize=160)
            self.candidate_panel.master.rowconfigure(6, weight=1, minsize=238)
            self.candidate_panel.grid()
        else:
            self.candidate_panel.master.rowconfigure(5, weight=0, minsize=0)
            self.candidate_panel.master.rowconfigure(6, weight=0, minsize=0)
            self.candidate_panel.grid_remove()

    def _set_mode_buttons(self):
        if self._view_mode == "today":
            self.create_button.configure(state="disabled")
            self.update_button.configure(state="disabled")
            return
        if self._is_inspector_workspace():
            prepared = self._active_workspace.prepared_case
            if hasattr(self, "inspector_commit_button"):
                self.inspector_commit_button.configure(
                    state="normal" if not self._running and self._state == WorkspaceState.REVIEW_READY and prepared else "disabled",
                    text="UPDATE ITR" if prepared and getattr(prepared, "can_update", False) else "CREATE IN ITR",
                )
            if hasattr(self, "inspector_analyze_button"):
                self.inspector_analyze_button.configure(state="normal" if not self._running and self._state == WorkspaceState.REVIEW_READY else "disabled")
            return
        if self.sync_button:
            self.sync_button.configure(state="normal" if not self._running and self.ticket_no.get().strip() else "disabled")
        if getattr(self, "nextop_commit_button", None):
            prepared = self._active_workspace.prepared_case
            self.nextop_commit_button.configure(state="normal" if not self._running and self._state == WorkspaceState.REVIEW_READY and prepared else "disabled", text="UPDATE ITR" if prepared and getattr(prepared, "can_update", False) else "CREATE IN ITR")
        if self.analyze_button:
            self.analyze_button.configure(state="normal" if not self._running and self._state == WorkspaceState.EDITING else "disabled")
        can_create = not self._running and self._state == WorkspaceState.ANALYZED and self._draft is not None and self.source.get() in MANUAL_SOURCES
        can_update = can_create and bool(self.tree.selection())
        self.create_button.configure(state="normal" if can_create else "disabled")
        self.update_button.configure(state="normal" if can_update else "disabled")

    def _manual_input_changed(self, _event=None):
        if self._loading_workspace:
            return
        if not self.manual_text.edit_modified():
            return
        self.manual_text.edit_modified(False)
        if self._running:
            return
        if self._state == WorkspaceState.ANALYZED:
            self._draft, self._candidates = None, []
            self._clear_candidates()
        self._set_workspace_state(WorkspaceState.EDITING if self.manual_text.get("1.0", "end-1c").strip() else WorkspaceState.EMPTY)

    def _ticket_changed(self, *_args):
        if self._loading_workspace:
            return
        if self._running:
            return
        # Editing a completed ticket begins a separate Nextop workspace.  Keep
        # an in-progress user choice intact, but never carry a saved Case value
        # into a newly typed ticket.
        current_reference = str((self._current_case or {}).get("reference_no") or "")
        if self._state == WorkspaceState.COMPLETED and self.ticket_no.get().strip() != current_reference:
            self._load_todo_value(False)
        self._set_workspace_state(WorkspaceState.EDITING if self.ticket_no.get().strip() else WorkspaceState.EMPTY)

    def _candidate_selected(self, _event=None):
        selected = self.tree.selection()
        if selected:
            candidate = self._today_visible[int(selected[0])] if self._view_mode == "today" else self._candidates[int(selected[0])]
            self._show_preview(candidate)
            if self._view_mode != "today":
                # Candidate DTO already comes from the matching record read.
                self._load_todo_value(candidate.get("include_itr_todo", False))
        self._set_mode_buttons()

    def _show_preview(self, candidate):
        values = (
            ("Ticket No.", candidate.get("ticket_no") or "-"),
            ("Dealer", candidate.get("disti") or "-"),
            ("Model", candidate.get("model_type") or "-"),
            ("Status", candidate.get("status") or "-"),
            ("Device", candidate.get("device_name")),
            ("Error Code", ", ".join(candidate.get("error_codes") or [])),
            ("Fault Symptom", ", ".join(candidate.get("fault_symptom") or [])),
            ("Created", case_service.format_time(candidate.get("ticket_created_time"))),
            ("First Reply", case_service.format_time(candidate.get("replied_time_first"))),
            ("Last Reply", case_service.format_time(candidate.get("replied_time_new"))),
            ("L2 TAG", f"{candidate.get('second_level_tag')}    {candidate.get('case_count')} CASES" if candidate.get("second_level_tag") and candidate.get("case_count") not in (None, "") else candidate.get("second_level_tag")),
            ("ADD TO ITR TODO", "YES" if candidate.get("include_itr_todo") else None),
            ("\nPIE Comment", candidate.get("pie_comment") or "-"),
            ("\nSolutions", candidate.get("solutions")),
            ("\nDescription", candidate.get("description") or "-"),
        )
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        for label, value in values:
            if value in (None, "", [], "-"):
                continue
            self.preview.insert("end", f"{label}\n", ("label",))
            self.preview.insert("end", f"{value}\n")
        self.preview.tag_configure("label", foreground=BLUE, font=("Segoe UI Semibold", 9))
        self.preview.configure(state="disabled")

    def _scroll_tree(self, event):
        self.tree.yview_scroll(-int(event.delta / 120), "units")
        return "break"

    def _scroll_preview(self, event):
        self.preview.yview_scroll(-int(event.delta / 120), "units")
        return "break"

    def _clear_candidates(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.case_count.set("0 CASES")
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.configure(state="disabled")

    def _sync_nextop(self, duplicate_decision=None, duplicate_record_id=None, resume_progress=False):
        ticket_no = self.ticket_no.get().strip()
        if not ticket_no:
            messagebox.showwarning("Ticket No. required", "Please enter a Nextop Ticket No.")
            return
        self._set_workspace_state(WorkspaceState.WRITING)
        self._pending_nextop_ticket = ticket_no
        todo_value = bool(self.todo_var.get())
        todo_dirty = self._todo_dirty
        def operation(value, progress_callback=None):
            return case_service.sync_nextop(value, progress_callback=progress_callback, include_itr_todo=todo_value, todo_dirty=todo_dirty, duplicate_decision=duplicate_decision, duplicate_record_id=duplicate_record_id)
        self._start_task(operation, ticket_no, completion=self._show_sync_result, reset_progress=not resume_progress)

    def _prepare_nextop(self):
        ticket_no = self.ticket_no.get().strip()
        if not ticket_no:
            messagebox.showwarning("Ticket No. required", "Please enter an ITR or Nextop Ticket No.")
            return
        self._active_workspace.ticket_input = ticket_no
        self._set_workspace_state(WorkspaceState.ANALYZING)
        self._start_task(case_service.prepare_nextop_case, ticket_no, completion=self._show_prepared_nextop)

    def _show_prepared_nextop(self, result):
        if not result.get("success"):
            self._set_workspace_state(WorkspaceState.EDITING)
            self._show_failure("Search failed", result)
            return
        self._active_workspace.prepared_case = result.get("prepared")
        self._current_case = result.get("case")
        self._active_workspace.workspace_type = "EXISTING_CASE" if getattr(self._active_workspace.prepared_case, "can_update", False) else "PREPARED_CASE"
        self._set_workspace_state(WorkspaceState.REVIEW_READY)
        self._render_workspace_view()
        self._set_task_progress("prepared", "Ready for review.")
        self._render_case_tabs()

    def _commit_prepared_nextop(self):
        prepared = self._active_workspace.prepared_case
        if not prepared:
            return
        self._set_workspace_state(WorkspaceState.WRITING)
        todo_value, todo_dirty = bool(self.todo_var.get()), self._todo_dirty
        def operation(value, progress_callback=None):
            return case_service.commit_prepared_nextop_case(value, progress_callback, include_itr_todo=todo_value, todo_dirty=todo_dirty)
        self._start_task(operation, prepared, completion=self._show_sync_result)

    def _refresh_nextop_session(self):
        value = self.pageorder_entry.get().strip() if getattr(self, "pageorder_entry", None) else ""
        if not value:
            messagebox.showwarning("PageOrder required", "Paste the latest PageOrder request from Nextop.")
            return
        self.pageorder_entry.delete(0, "end")
        self._set_workspace_state(WorkspaceState.WRITING)
        self._start_task(case_service.refresh_nextop_session, value, completion=self._show_nextop_auth_result)

    def _show_nextop_auth_result(self, result):
        if not result.get("success"):
            self._set_workspace_state(WorkspaceState.EDITING)
            self._show_failure("Nextop authentication failed", result)
            return
        self._nextop_auth_required = False
        self._render_input()
        self.status.set("AUTHENTICATED — Nextop session refreshed")
        ticket = self._pending_nextop_ticket or self.ticket_no.get().strip()
        if ticket:
            self._sync_nextop(resume_progress=True)

    def _prepare_manual(self):
        raw_text = self.manual_text.get("1.0", "end-1c").strip() if self.manual_text else ""
        if not raw_text:
            messagebox.showwarning("Content required", "Please paste the newly added communication content.")
            return
        self._draft, self._candidates = None, []
        self._clear_candidates()
        self._set_workspace_state(WorkspaceState.ANALYZING)
        self._start_task(case_service.prepare_manual_submission, self.source.get(), raw_text, completion=self._show_candidates)

    def _update_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a Case", "Please select a Candidate Case before updating.")
            return
        self._set_workspace_state(WorkspaceState.WRITING)
        record_id = self._candidates[int(selected[0])]["record_id"]
        if record_id in self._record_write_locks:
            self._set_workspace_state(WorkspaceState.ANALYZED)
            messagebox.showwarning("Case busy", "This case is currently being updated in another workspace.")
            return
        self._record_write_locks.add(record_id)
        self._active_workspace.record_id = record_id
        todo_value = self._todo_value_for_update()
        def operation(value, draft, progress_callback=None):
            return case_service.update_manual_case(value, draft, progress_callback=progress_callback, include_itr_todo=todo_value)
        self._start_task(operation, record_id, self._draft, completion=self._show_manual_result)

    def _create_manual(self):
        self._set_workspace_state(WorkspaceState.WRITING)
        todo_value = bool(self.todo_var.get())
        def operation(draft, progress_callback=None):
            return case_service.create_manual_case(draft, progress_callback=progress_callback, include_itr_todo=todo_value)
        self._start_task(operation, self._draft, completion=self._show_manual_result)

    def _start_task(self, operation, *args, completion, reset_progress=True):
        workspace_id = self._active_workspace_id
        workspace = self._active_workspace
        workspace.generation += 1
        generation = workspace.generation
        self._running = True
        if reset_progress:
            self._reset_task_progress()
        self._set_mode_buttons()
        self.status.set("WORKING — Starting operation.")

        def progress(stage, message, success=None):
            self._events.put(("progress", workspace_id, generation, stage, message, success))

        def worker():
            try:
                result = operation(*args, progress_callback=progress)
            except Exception:
                result = {"success": False, "message": "Operation failed.", "error_type": "unexpected"}
            self._events.put(("result", workspace_id, generation, result, completion))

        threading.Thread(target=worker, daemon=True).start()

    def _drain_events(self):
        try:
            while True:
                event = self._events.get_nowait()
                if event[0] == "progress":
                    _, workspace_id, generation, stage, message, _success = event
                    workspace = self._workspaces.get(workspace_id)
                    if not workspace or workspace.generation != generation:
                        continue
                    if workspace_id == self._active_workspace_id:
                        self._set_task_progress(stage, message or "Processing.")
                    else:
                        state, percent = PROGRESS_STAGES.get(stage, (None, None))
                        workspace.progress_stage = stage
                        if percent is not None:
                            workspace.progress_percent = percent
                        if message:
                            workspace.progress_detail = message
                        if state and message:
                            workspace.status_text = f"{state} — {message}"
                else:
                    _, workspace_id, generation, result, completion = event
                    workspace = self._workspaces.get(workspace_id)
                    if not workspace or workspace.generation != generation:
                        continue
                    original_workspace_id = self._active_workspace_id
                    if workspace_id != original_workspace_id:
                        self._save_active_workspace()
                        self._active_workspace_id = workspace_id
                    self._running = False
                    workspace.last_result = result
                    completion(result)
                    if workspace.record_id:
                        self._record_write_locks.discard(workspace.record_id)
                    self._set_mode_buttons()
                    self._render_case_tabs()
                    if workspace_id != original_workspace_id:
                        self._active_workspace_id = original_workspace_id
                        self._activate_workspace(original_workspace_id, force=True)
        except queue.Empty:
            pass
        self.root.after(100, self._drain_events)

    def _show_sync_result(self, result):
        if result.get("error_type") == "nextop_auth_required":
            self._nextop_auth_required = True
            self._set_workspace_state(WorkspaceState.EDITING)
            self._render_input()
            self.status.set("AUTH REQUIRED — Paste latest PageOrder")
            return
        if result.get("possible_duplicate"):
            candidate = result.get("duplicate_candidate") or {}
            summary_values = (("Ticket No.", candidate.get("ticket_no")), ("Source", candidate.get("reference_no")), ("Dealer", candidate.get("disti")), ("Model", candidate.get("model_type")), ("Created", case_service.format_time(candidate.get("ticket_created_time"))), ("Latest Reply", case_service.format_time(candidate.get("replied_time_new"))), ("PIE Comment", candidate.get("pie_comment")))
            summary = "\n".join(f"{label}: {value or '-'}" for label, value in summary_values)
            self._set_workspace_state(WorkspaceState.EDITING)
            self.status.set("POSSIBLE EXISTING CASE — Confirmation required")
            update_existing = messagebox.askyesno(
                "Possible Existing Case",
                f"A high-confidence existing Case was found.\n\n{summary}\n\nYes: UPDATE EXISTING\nNo: CREATE NEW ANYWAY",
            )
            self._sync_nextop("update" if update_existing else "create", candidate.get("record_id"), resume_progress=True)
            return
        if result.get("success"):
            self._set_workspace_state(WorkspaceState.COMPLETED)
            self._record_today_case(result)
            self._current_case = result.get("case")
            if self._current_case:
                self._load_todo_value(self._current_case.get("include_itr_todo", False))
                self._active_workspace.workspace_type = "EXISTING_CASE"
                self._render_workspace_view()
            action = str(result.get("action") or "").upper()
            ticket = (result.get("case") or {}).get("ticket_no") or result.get("ticket_no") or "-"
            verb = "CREATED" if action == "CREATED" else "UPDATED"
            source = (result.get("case") or {}).get("reference_no") or result.get("ticket_no") or "-"
            count = result.get("case_count")
            suffix = f" · {count} Cases" if count is not None else ""
            if (result.get("case") or {}).get("include_itr_todo"):
                suffix += " · ADD TO ITR TODO"
            self._set_task_progress("complete", f"{ticket} {verb} · NEXTOP {source}{suffix}")
        else:
            self._show_failure("Sync failed", result)

    def _show_candidates(self, result):
        if not result.get("success"):
            self._set_workspace_state(WorkspaceState.EDITING)
            self._show_failure("Analysis failed", result)
            return
        self._draft = result["draft"]
        self._set_workspace_state(WorkspaceState.ANALYZED)
        self._candidates = result.get("candidates", [])
        self._clear_candidates()
        for index, candidate in enumerate(self._candidates):
            issue = " ".join((candidate.get("pie_comment") or candidate.get("description") or "").split())[:120]
            self.tree.insert("", "end", iid=str(index), values=(candidate.get("ticket_no") or "-", candidate.get("disti") or "", candidate.get("model_type") or "", case_service.format_time(candidate.get("replied_time_new"))))
        if self._candidates:
            self.empty_state.grid_remove()
        self.case_count.set(self._case_label(len(self._candidates)))
        self.status.set(f"PREPARED — Analysis ready. {len(self._candidates)} possible related Case(s). Select one or create a new Case.")

    def _show_manual_result(self, result):
        self._print_single_select_audit(result.get("single_select_audit"))
        if result.get("duplicate_detected"):
            self.status.set("WARNING — Content may already be recorded. No update was made.")
            messagebox.showwarning("Duplicate protected", "This content may already be recorded in the selected Case. No update was made.")
        elif result.get("success"):
            self._draft = None
            self._set_workspace_state(WorkspaceState.COMPLETED)
            created = result.get("created_case") or result.get("updated_case")
            self._record_today_case(result, created)
            if created:
                self._load_todo_value(created.get("include_itr_todo", False))
                self._candidates = [created]
                self._clear_candidates()
                self.tree.insert("", "end", iid="0", values=(created.get("ticket_no") or "-", created.get("disti") or "", created.get("model_type") or "", case_service.format_time(created.get("replied_time_new"))))
                self.empty_state.grid_remove()
                self.tree.selection_set("0")
                self._show_preview(created)
            ticket = (created or {}).get("ticket_no") or result.get("record_id") or "-"
            if result.get("case_count_refresh_warning"):
                self.status.set(f"WARNING — {ticket} created · Case count refresh pending")
            else:
                count = result.get("case_count")
                todo_suffix = " · ADD TO ITR TODO" if (created or {}).get("include_itr_todo") else ""
                self._set_task_progress("complete", f"{ticket} · Case count: {count}{todo_suffix}" if count is not None else f"{ticket} · Manual Case created{todo_suffix}")
            # Successful writes are confirmed inline through STATUS/current Case.
        else:
            self._set_workspace_state(WorkspaceState.ANALYZED)
            self._show_failure("Operation failed", result)

    @staticmethod
    def _print_single_select_audit(audit):
        """Development-terminal output only; audit contains no submitted values."""
        if not audit:
            return
        print("SingleSelect audit:")
        for field_name, item in audit.items():
            action = item.get("submit_or_omit", "omit").upper()
            query = "validated" if item.get("exact_validation_result") is True else (
                "invalid" if item.get("exact_validation_result") is False else "query failed" if item.get("live_options_query_success") is False else "no value"
            )
            print(f"  {field_name}: {action} / {query}")

    def _show_failure(self, title, result):
        error_type = result.get("error_type")
        if error_type == "network_error":
            message = "Network request failed. Check connectivity and try again."
            status = "ERROR — Network request failed"
        elif error_type == "python_error":
            message = "The application could not complete the operation."
            status = "ERROR — Application error"
        elif error_type == "feishu_api_error":
            code = result.get("feishu_code")
            category = result.get("error_category")
            if category == "authorization":
                summary = "Feishu authorization is required."
            elif category == "field_validation":
                summary = "Feishu rejected one or more field values."
            else:
                summary = "Feishu rejected the operation."
            diagnostic = result.get("safe_message") or summary
            message = f"{summary}\nCode: {code if code is not None else '-'}\nMessage: {diagnostic}"
            status = f"ERROR — Feishu code {code if code is not None else '-'}"
        else:
            message = result.get("message") or "Operation failed."
            status = "ERROR — Operation failed"
        self.status.set(status)
        messagebox.showerror(title, message)

    def _on_close(self):
        if self._running and not messagebox.askyesno("Task running", "A task is still running. Close the application?"):
            return
        self.root.destroy()


def main():
    _set_windows_app_user_model_id()
    root = tk.Tk()
    PieItrAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # pythonw has no terminal.  Keep startup feedback safe and direct
        # development diagnostics to the retained CLI launcher instead.
        try:
            fallback = tk.Tk()
            fallback.withdraw()
            messagebox.showerror(
                "PIE ITR Assistant",
                "The application could not start. Use run_cli.bat to view safe diagnostics.",
            )
            fallback.destroy()
        except tk.TclError:
            pass
