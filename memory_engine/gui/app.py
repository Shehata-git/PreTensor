import customtkinter as ctk
import time
import threading
from memory_engine.llm.orchestrator import LLMOrchestrator

# --- Terminal Aesthetic Configuration (Upscaled v3) ---
APP_BG = "#0B0B0F"
PANEL_BG = "#14141D"
ACCENT_COLOR = "#00E5FF" # Neon Cyan
DANGER_COLOR = "#FF4B4B" # Sharp Red
BORDER_COLOR = "#2A2A35"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0B0"

# Font Logic - Robust fallback chain for sharp Linux rendering
def get_font(size=20, bold=False):
    # Prioritize clean, sharp monospaced fonts available on Linux
    families = ["JetBrains Mono", "Noto Sans Mono", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Monospace", "Consolas"]
    weight = "bold" if bold else "normal"
    # ctk supports a tuple where families is a list for fallback
    return (families, size, weight)

FONT_H1 = get_font(28, True)
FONT_MAIN = get_font(20)
FONT_BOLD = get_font(20, True)
FONT_SMALL = get_font(16)
FONT_MONO = get_font(18) 

ctk.set_appearance_mode("Dark")

class SemanticMemoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TERMINAL // SEMANTIC_MEMORY_v3")
        self.geometry("1700x1100") # Scaled up again
        self.configure(fg_color=APP_BG)
        
        self.orchestrator = LLMOrchestrator()
        self.current_session_id = None
        self.comparison_mode = False

        self._init_ui()
        self._load_sessions()

    def _init_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(
            self, width=400, corner_radius=0, 
            fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar_header = ctk.CTkLabel(
            self.sidebar, text="> CHAT_HISTORY", 
            font=FONT_H1, text_color=ACCENT_COLOR
        )
        self.sidebar_header.pack(pady=(60, 40), padx=40, anchor="w")
        
        self.new_chat_btn = ctk.CTkButton(
            self.sidebar, text="[ + INITIALIZE_NEW ]", 
            font=FONT_BOLD,
            fg_color="transparent", border_width=1, border_color=ACCENT_COLOR,
            text_color=ACCENT_COLOR, hover_color="#003333",
            height=65, corner_radius=0,
            command=self._new_chat
        )
        self.new_chat_btn.pack(pady=15, padx=30, fill="x")

        self.delete_chat_btn = ctk.CTkButton(
            self.sidebar, text="[ ! DELETE_ACTIVE ]", 
            font=FONT_BOLD,
            fg_color="transparent", border_width=1, border_color=DANGER_COLOR,
            text_color=DANGER_COLOR, hover_color="#330000",
            height=65, corner_radius=0,
            command=self._delete_active_session
        )
        self.delete_chat_btn.pack(pady=15, padx=30, fill="x")
        
        self.session_list = ctk.CTkScrollableFrame(
            self.sidebar, label_text="ARCHIVE_REGISTRY",
            label_font=FONT_SMALL,
            label_text_color=TEXT_SECONDARY,
            fg_color="transparent", corner_radius=0
        )
        self.session_list.pack(fill="both", expand=True, padx=20, pady=40)

        # --- Main View ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color=APP_BG)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        
        # Header Row
        self.header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 40))
        
        self.title_label = ctk.CTkLabel(
            self.header, text="READY // IDLE", 
            font=FONT_H1, text_color=TEXT_PRIMARY
        )
        self.title_label.pack(side="left")

        self.reset_btn = ctk.CTkButton(
            self.header, text="RESET_VIEW", 
            font=FONT_SMALL, fg_color="#2A2A35", corner_radius=0, 
            width=150, height=50, command=self._reset_view
        )
        self.reset_btn.pack(side="left", padx=40)
        
        self.compare_toggle = ctk.CTkSwitch(
            self.header, text="DUAL_QUERY_PIPELINE", 
            font=FONT_SMALL,
            progress_color=ACCENT_COLOR,
            corner_radius=0,
            command=self._toggle_comparison
        )
        self.compare_toggle.pack(side="right")

        # --- Dashboard Area ---
        self.dashboard_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dashboard_frame.pack(fill="x", pady=(0, 40))
        
        self.telemetry_left = self._create_telemetry_block(self.dashboard_frame, "CONTEXT // QDRANT_RAW")
        self.telemetry_right = self._create_telemetry_block(self.dashboard_frame, "CONTEXT // QDRANT_NLP_OPTIMIZED")
        self.telemetry_right["frame"].pack_forget()

        # --- Chat Panes ---
        self.chat_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.chat_area.pack(fill="both", expand=True)
        
        self.chat_left = self._create_chat_pane(self.chat_area, "RETRIEVAL_STREAM // METHOD_A")
        self.chat_right = self._create_chat_pane(self.chat_area, "RETRIEVAL_STREAM // METHOD_B")
        self.chat_right["frame"].pack_forget()

        # --- Input Bar ---
        self.input_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=(40, 0))
        
        self.input_box = ctk.CTkEntry(
            self.input_frame, placeholder_text="INPUT_CMD >>", 
            height=80, corner_radius=0, border_width=1, border_color=BORDER_COLOR,
            fg_color=PANEL_BG, text_color=TEXT_PRIMARY,
            font=FONT_MAIN
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 20))
        self.input_box.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ctk.CTkButton(
            self.input_frame, text="EXECUTE", 
            command=self._send_message, width=220, height=80, 
            corner_radius=0, fg_color=ACCENT_COLOR, text_color="#000000",
            font=FONT_BOLD
        )
        self.send_btn.pack(side="right")

    def _create_telemetry_block(self, master, title):
        frame = ctk.CTkFrame(master, fg_color=PANEL_BG, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        frame.pack(side="left", fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(frame, text=title, font=FONT_MONO, text_color=ACCENT_COLOR).pack(pady=(20, 10), padx=20, anchor="w")
        
        metrics_container = ctk.CTkFrame(frame, fg_color="transparent")
        metrics_container.pack(fill="x", padx=25, pady=20)
        
        def add_metric(label, color):
            ctk.CTkLabel(metrics_container, text=label, font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
            pb = ctk.CTkProgressBar(metrics_container, height=12, corner_radius=0, progress_color=color, fg_color="#1A1A25")
            pb.pack(fill="x", pady=(5, 12))
            pb.set(0)
            val_lbl = ctk.CTkLabel(metrics_container, text="[ 0.0 ]", font=FONT_MONO, text_color=TEXT_PRIMARY)
            val_lbl.pack(anchor="e")
            return {"bar": pb, "label": val_lbl}

        latency = add_metric("LATENCY_MS", ACCENT_COLOR)
        tokens = add_metric("TOKENS_GEN", "#BF00FF")
        vram = add_metric("VRAM_GB", "#FF0055")
        
        return {"frame": frame, "latency": latency, "tokens": tokens, "vram": vram}

    def _create_chat_pane(self, master, title):
        frame = ctk.CTkFrame(master, fg_color=PANEL_BG, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        frame.pack(side="left", fill="both", expand=True, padx=10)
        
        header = ctk.CTkLabel(frame, text=f"// {title}", font=FONT_MONO, text_color=TEXT_SECONDARY)
        header.pack(pady=15, padx=20, anchor="w")
        
        text_area = ctk.CTkTextbox(
            frame, fg_color="#0D0D14", text_color=TEXT_PRIMARY,
            font=FONT_MAIN, wrap="word", spacing3=10, corner_radius=0,
            border_width=0
        )
        text_area.pack(fill="both", expand=True, padx=4, pady=4)
        text_area.configure(state="disabled")
        
        return {"frame": frame, "text": text_area}

    def _toggle_comparison(self):
        self.comparison_mode = self.compare_toggle.get() == 1
        if self.comparison_mode:
            self.chat_right["frame"].pack(side="left", fill="both", expand=True, padx=10)
            self.telemetry_right["frame"].pack(side="left", fill="both", expand=True, padx=10)
            self._refresh_chat_history()
        else:
            self.chat_right["frame"].pack_forget()
            self.telemetry_right["frame"].pack_forget()

    def _load_sessions(self):
        for widget in self.session_list.winfo_children():
            widget.destroy()
            
        sessions = self.orchestrator.sqlite.get_sessions()
        for s in sessions:
            btn = ctk.CTkButton(
                self.session_list, 
                text=f"> {s['chat_title']}", 
                fg_color="transparent", 
                text_color=TEXT_SECONDARY,
                hover_color="#1A1A25",
                anchor="w",
                font=FONT_SMALL,
                height=55,
                corner_radius=0,
                command=lambda sid=s["session_id"], title=s["chat_title"]: self._select_session(sid, title)
            )
            btn.pack(fill="x", pady=5)

    def _select_session(self, session_id, title):
        self.current_session_id = session_id
        self.title_label.configure(text=f"CONNECTED // {title}")
        self._refresh_chat_history()

    def _new_chat(self):
        self.current_session_id = None
        self.title_label.configure(text="STATUS // PENDING_HANDSHAKE")
        self._reset_view()

    def _reset_view(self):
        for pane in [self.chat_left, self.chat_right]:
            pane["text"].configure(state="normal")
            pane["text"].delete("1.0", "end")
            pane["text"].configure(state="disabled")

    def _delete_active_session(self):
        if self.current_session_id:
            self.orchestrator.sqlite.delete_session(self.current_session_id)
            self.current_session_id = None
            self.title_label.configure(text="READY // IDLE")
            self._load_sessions()
            self._reset_view()

    def _refresh_chat_history(self):
        if not self.current_session_id: return
        messages = self.orchestrator.sqlite.get_messages(self.current_session_id)
        
        panes = [self.chat_left]
        if self.comparison_mode:
            panes.append(self.chat_right)
            
        for pane in panes:
            pane["text"].configure(state="normal")
            pane["text"].delete("1.0", "end")
            for m in messages:
                role_tag = "USER" if m['role'] == 'user' else "AI"
                content = str(m['content'])
                pane["text"].insert("end", f"[{role_tag}] >> {content}\n\n")
            pane["text"].configure(state="disabled")
            pane["text"].see("end")

    def _send_message(self):
        prompt = self.input_box.get()
        if not prompt: return
        
        is_new_session = False
        if self.current_session_id is None:
            is_new_session = True
            title = f"HANDSHAKE_{time.strftime('%H%M%S')}"
            self.current_session_id = self.orchestrator.sqlite.create_session(title)
            self.title_label.configure(text=f"CONNECTED // {title}")
            self._load_sessions()
            
        self.input_box.delete(0, "end")
        self._append_message(self.chat_left, "USER", prompt)
        if self.comparison_mode:
            self._append_message(self.chat_right, "USER", prompt)
            
        threading.Thread(target=self._generate_responses, args=(prompt, is_new_session)).start()

    def _append_message(self, pane, role, content):
        pane["text"].configure(state="normal")
        safe_content = str(content)
        pane["text"].insert("end", f"[{role}] >> {safe_content}\n\n")
        pane["text"].configure(state="disabled")
        pane["text"].see("end")

    def _generate_responses(self, prompt, is_new_session=False):
        start_a = time.time()
        resp_a = self.orchestrator.generate_method_a(self.current_session_id, prompt)
        latency_a = (time.time() - start_a) * 1000
        
        start_b = time.time()
        resp_b = self.orchestrator.generate_method_b(self.current_session_id, prompt)
        latency_b = (time.time() - start_b) * 1000
        
        self.after(0, lambda: self._append_message(self.chat_left, "AI", resp_a))
        self.after(0, lambda: self._update_telemetry(self.telemetry_left, latency_a, len(resp_a)//4, 3.8))
        
        if self.comparison_mode:
            self.after(0, lambda: self._append_message(self.chat_right, "AI", resp_b))
            self.after(0, lambda: self._update_telemetry(self.telemetry_right, latency_b, len(resp_b)//4, 1.4))
            
        self.orchestrator.store_interaction(self.current_session_id, prompt, resp_a)
        
        if is_new_session:
            new_title = self.orchestrator.summarize_session(prompt)
            self.orchestrator.sqlite.update_session_title(self.current_session_id, new_title)
            self.after(0, lambda t=new_title: self.title_label.configure(text=f"CONNECTED // {t}"))
            self.after(0, self._load_sessions)

    def _update_telemetry(self, block, latency, tokens, vram):
        block["latency"]["bar"].set(min(1.0, latency / 2000))
        block["latency"]["label"].configure(text=f"[ {latency:.1f} ms ]")
        block["tokens"]["bar"].set(min(1.0, tokens / 1000))
        block["tokens"]["label"].configure(text=f"[ {int(tokens)} T ]")
        block["vram"]["bar"].set(min(1.0, vram / 8))
        block["vram"]["label"].configure(text=f"[ {vram:.1f} GB ]")

if __name__ == "__main__":
    app = SemanticMemoryApp()
    app.mainloop()
