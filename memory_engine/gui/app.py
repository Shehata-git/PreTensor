import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import time
import threading
from memory_engine.llm.orchestrator import LLMOrchestrator
from memory_engine.gui.theme import CSS
from memory_engine.gui.components.telemetry import TelemetryBlock
from memory_engine.gui.components.chat import ChatPane

class SemanticMemoryApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.memory.engine")
        self.orchestrator = LLMOrchestrator()
        self.current_session_id = None
        self.comparison_mode = False

    def do_activate(self):
        # Window Setup
        self.window = Gtk.ApplicationWindow(application=self, title="TERMINAL // SEMANTIC_MEMORY_v3")
        self.window.set_default_size(1920, 1080)
        
        # Load CSS Provider
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self._init_ui()
        self.window.show_all()
        
        # Initially hide Method B components
        self.chat_right.container.hide()
        self.telemetry_right.container.hide()
        
        self._load_sessions()
        
        # Trigger Model Warm-up Protocol
        threading.Thread(target=self._warm_up_protocol, daemon=True).start()

    def _warm_up_protocol(self):
        GLib.idle_add(self.title_label.set_text, "WAKING MODEL...")
        if self.orchestrator.warm_up_ollama():
            GLib.idle_add(self.title_label.set_text, "READY // IDLE")
        else:
            GLib.idle_add(self.title_label.set_text, "CONNECTION ERROR // OLLAMA_OFFLINE")

    def _init_ui(self):
        # Main Layout split: Sidebar | Content
        self.main_split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.window.add(self.main_split)

        # --- Sidebar ---
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar.set_size_request(380, -1)
        self.main_split.pack1(self.sidebar, resize=False, shrink=False)

        sidebar_header = Gtk.Label(label="> CHAT_HISTORY", xalign=0)
        sidebar_header.get_style_context().add_class("header-label")
        sidebar_header.set_margin_top(60)
        sidebar_header.set_margin_bottom(40)
        sidebar_header.set_margin_start(40)
        self.sidebar.pack_start(sidebar_header, False, False, 0)

        # Buttons Box
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        btn_box.set_margin_start(30)
        btn_box.set_margin_end(30)
        self.sidebar.pack_start(btn_box, False, False, 0)

        self.new_chat_btn = Gtk.Button(label="[ + INITIALIZE_NEW ]")
        self.new_chat_btn.get_style_context().add_class("accent")
        self.new_chat_btn.set_size_request(-1, 65)
        self.new_chat_btn.connect("clicked", self._new_chat)
        btn_box.pack_start(self.new_chat_btn, False, False, 0)

        self.delete_chat_btn = Gtk.Button(label="[ ! DELETE_ACTIVE ]")
        self.delete_chat_btn.get_style_context().add_class("danger")
        self.delete_chat_btn.set_size_request(-1, 65)
        self.delete_chat_btn.connect("clicked", self._delete_active_session)
        btn_box.pack_start(self.delete_chat_btn, False, False, 0)

        archive_label = Gtk.Label(label="ARCHIVE_REGISTRY", xalign=0)
        archive_label.get_style_context().add_class("secondary-label")
        archive_label.set_margin_top(40)
        archive_label.set_margin_start(20)
        self.sidebar.pack_start(archive_label, False, False, 0)

        self.session_scroll = Gtk.ScrolledWindow()
        self.session_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.session_scroll.set_margin_start(20)
        self.session_scroll.set_margin_end(20)
        self.session_scroll.set_margin_bottom(40)
        
        self.session_list = Gtk.ListBox()
        self.session_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.session_list.connect("row-selected", self._on_session_selected)
        self.session_scroll.add(self.session_list)
        self.sidebar.pack_start(self.session_scroll, True, True, 0)

        # --- Main Area ---
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_container.set_margin_top(40)
        self.main_container.set_margin_bottom(40)
        self.main_container.set_margin_start(40)
        self.main_container.set_margin_end(40)
        self.main_split.pack2(self.main_container, resize=True, shrink=False)

        # Header Row
        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        header_row.set_margin_bottom(40)
        self.main_container.pack_start(header_row, False, False, 0)

        self.title_label = Gtk.Label(label="READY // IDLE", xalign=0)
        self.title_label.get_style_context().add_class("header-label")
        self.title_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        header_row.pack_start(self.title_label, True, True, 0)

        self.reset_btn = Gtk.Button(label="RESET_VIEW")
        self.reset_btn.set_size_request(150, 50)
        self.reset_btn.connect("clicked", lambda w: self._reset_view())
        header_row.pack_start(self.reset_btn, False, False, 0)

        compare_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        header_row.pack_start(compare_box, False, False, 0)
        
        compare_label = Gtk.Label(label="DUAL_QUERY_PIPELINE")
        compare_label.get_style_context().add_class("secondary-label")
        compare_box.pack_start(compare_label, False, False, 0)
        
        self.compare_switch = Gtk.Switch()
        self.compare_switch.connect("notify::active", self._toggle_comparison)
        compare_box.pack_start(self.compare_switch, False, False, 0)

        # Telemetry Dashboard (Horizontal Paned for alignment with chat)
        self.dashboard_split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.dashboard_split.set_margin_bottom(40)
        self.main_container.pack_start(self.dashboard_split, False, False, 0)

        self.telemetry_left = TelemetryBlock("CONTEXT // QDRANT_RAW")
        self.dashboard_split.pack1(self.telemetry_left.container, resize=True, shrink=False)

        self.telemetry_right = TelemetryBlock("CONTEXT // QDRANT_NLP_OPTIMIZED")
        self.dashboard_split.pack2(self.telemetry_right.container, resize=True, shrink=False)

        # Sync Expanders
        self.telemetry_left.container.connect("notify::expanded", self._sync_telemetry_expansion, "left")
        self.telemetry_right.container.connect("notify::expanded", self._sync_telemetry_expansion, "right")

        # Chat Panes (Resizable Split)
        self.chat_split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_container.pack_start(self.chat_split, True, True, 0)

        # Synchronize the two Paned positions (FIXED BindingFlags)
        self.chat_split.bind_property("position", self.dashboard_split, "position", GObject.BindingFlags.BIDIRECTIONAL)

        self.chat_left = ChatPane("RETRIEVAL_STREAM // METHOD_A")
        self.chat_split.pack1(self.chat_left.container, resize=True, shrink=False)

        self.chat_right = ChatPane("RETRIEVAL_STREAM // METHOD_B")
        self.chat_split.pack2(self.chat_right.container, resize=True, shrink=False)

        # Input Bar
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        input_row.set_margin_top(40)
        self.main_container.pack_start(input_row, False, False, 0)

        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("INPUT_CMD >>")
        self.input_entry.set_size_request(-1, 80)
        self.input_entry.connect("activate", self._send_message)
        input_row.pack_start(self.input_entry, True, True, 0)

        self.execute_btn = Gtk.Button(label="EXECUTE")
        self.execute_btn.get_style_context().add_class("execute")
        self.execute_btn.set_size_request(220, 80)
        self.execute_btn.connect("clicked", self._send_message)
        input_row.pack_start(self.execute_btn, False, False, 0)

    def _toggle_comparison(self, switch, gparam):
        self.comparison_mode = switch.get_active()
        if self.comparison_mode:
            self.chat_right.container.show_all()
            self.telemetry_right.container.show_all()
            
            # Use idle_add to ensure widgets are mapped and allocated before centering
            GLib.idle_add(self._recenter_splits)
            
            # Ensure both start with the same expansion state
            self.telemetry_right.container.set_expanded(self.telemetry_left.container.get_expanded())
            self._refresh_chat_history()
        else:
            self.chat_right.container.hide()
            self.telemetry_right.container.hide()

    def _recenter_splits(self):
        width = self.chat_split.get_allocated_width()
        if width > 1:
            # Subtract any internal spacing if necessary, but // 2 is the theoretical center
            self.chat_split.set_position(width // 2)
        return False # Only run once

    def _sync_telemetry_expansion(self, expander, gparam, source):
        state = expander.get_expanded()
        target = self.telemetry_right.container if source == "left" else self.telemetry_left.container
        if target.get_expanded() != state:
            target.set_expanded(state)

    def _load_sessions(self):
        # Clear ListBox
        for child in self.session_list.get_children():
            self.session_list.remove(child)

        sessions = self.orchestrator.sqlite.get_sessions()
        for s in sessions:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label=f"> {s['chat_title']}", xalign=0)
            row.add(lbl)
            row.session_id = s["session_id"]
            row.chat_title = s["chat_title"]
            self.session_list.add(row)
        self.session_list.show_all()

    def _on_session_selected(self, listbox, row):
        if row:
            self.current_session_id = row.session_id
            self.title_label.set_text(f"CONNECTED // {row.chat_title}")
            self._refresh_chat_history()

    def _new_chat(self, button):
        self.current_session_id = None
        self.title_label.set_text("STATUS // PENDING_HANDSHAKE")
        self._reset_view()

    def _reset_view(self):
        self.chat_left.set_text("")
        self.chat_right.set_text("")

    def _delete_active_session(self, button):
        if self.current_session_id:
            self.orchestrator.sqlite.delete_session(self.current_session_id)
            self.current_session_id = None
            self.title_label.set_text("READY // IDLE")
            self._load_sessions()
            self._reset_view()

    def _refresh_chat_history(self):
        if not self.current_session_id: return
        messages = self.orchestrator.sqlite.get_messages(self.current_session_id)
        
        panes = [self.chat_left]
        if self.comparison_mode:
            panes.append(self.chat_right)
            
        for pane in panes:
            pane.set_text("")
            for m in messages:
                role_tag = "USER" if m['role'] == 'user' else "AI"
                content = str(m['content'])
                pane.append_message(role_tag, content)

    def _send_message(self, widget):
        prompt = self.input_entry.get_text()
        if not prompt: return
        
        is_new_session = False
        if self.current_session_id is None:
            is_new_session = True
            title = f"HANDSHAKE_{time.strftime('%H%M%S')}"
            self.current_session_id = self.orchestrator.sqlite.create_session(title)
            self.title_label.set_text(f"CONNECTED // {title}")
            self._load_sessions()
            
        self.input_entry.set_text("")
        self.chat_left.append_message("USER", prompt)
        if self.comparison_mode:
            self.chat_right.append_message("USER", prompt)
            
        threading.Thread(target=self._generate_responses, args=(prompt, is_new_session)).start()

    def _generate_responses(self, prompt, is_new_session=False):
        # Method A
        res_a = self.orchestrator.generate_method_a(self.current_session_id, prompt)
        resp_a = res_a["response"]
        latency_a = res_a["latency_ms"]
        vram_a = res_a["vram_gb"]
        tokens_a = res_a["tokens"]
        
        # Method B
        res_b = self.orchestrator.generate_method_b(self.current_session_id, prompt)
        resp_b = res_b["response"]
        latency_b = res_b["latency_ms"]
        vram_b = res_b["vram_gb"]
        tokens_b = res_b["tokens"]
        
        GLib.idle_add(self.chat_left.append_message, "AI", resp_a)
        GLib.idle_add(self.telemetry_left.update, latency_a, tokens_a, vram_a)
        
        if self.comparison_mode:
            GLib.idle_add(self.chat_right.append_message, "AI", resp_b)
            GLib.idle_add(self.telemetry_right.update, latency_b, tokens_b, vram_b)
            
        self.orchestrator.store_interaction(self.current_session_id, prompt, resp_a)
        
        if is_new_session:
            new_title = self.orchestrator.summarize_session(prompt)
            self.orchestrator.sqlite.update_session_title(self.current_session_id, new_title)
            GLib.idle_add(self.title_label.set_text, f"CONNECTED // {new_title}")
            GLib.idle_add(self._load_sessions)

if __name__ == "__main__":
    app = SemanticMemoryApp()
    import sys
    app.run(sys.argv)
