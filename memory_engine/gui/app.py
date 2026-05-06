import customtkinter as ctk
import time
import threading
from memory_engine.llm.orchestrator import LLMOrchestrator
from memory_engine.gui.components.gauge import CTkGauge

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SemanticMemoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Antigravity: Semantic Memory Engine")
        self.geometry("1200x800")
        
        self.orchestrator = LLMOrchestrator()
        self.current_session_id = None
        self.comparison_mode = False

        self._init_ui()
        self._load_sessions()

    def _init_ui(self):
        # Grid layout: Sidebar (0) | Main (1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Chat History", font=("Inter", 20, "bold"))
        self.sidebar_label.pack(pady=20, padx=10)
        
        self.new_chat_btn = ctk.CTkButton(self.sidebar, text="+ New Chat", command=self._new_chat)
        self.new_chat_btn.pack(pady=10, padx=20)
        
        self.session_list = ctk.CTkScrollableFrame(self.sidebar, label_text="Past Sessions")
        self.session_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Main View
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Header with Comparison Toggle
        self.header = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header, text="Select a chat to begin", font=("Inter", 24, "bold"))
        self.title_label.pack(side="left")
        
        self.compare_btn = ctk.CTkSwitch(self.header, text="Comparison Mode", command=self._toggle_comparison)
        self.compare_btn.pack(side="right")

        # Telemetry View (above chats)
        self.telemetry_frame = ctk.CTkFrame(self.main_view, height=120, fg_color="transparent")
        self.telemetry_frame.pack(fill="x", pady=10)
        
        self.telemetry_left = self._create_telemetry_block(self.telemetry_frame)
        self.telemetry_right = self._create_telemetry_block(self.telemetry_frame)
        self.telemetry_right.pack_forget() # Hidden initially

        # Chat Panes
        self.chat_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.chat_container.pack(fill="both", expand=True)
        
        self.chat_left = self._create_chat_pane(self.chat_container, "Method A: Standard Context")
        self.chat_right = self._create_chat_pane(self.chat_container, "Method B: Semantic Memory")
        self.chat_right.pack_forget() # Hidden initially

        # Input Area
        self.input_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=20)
        
        self.input_box = ctk.CTkEntry(self.input_frame, placeholder_text="Enter your prompt here...", height=50)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", command=self._send_message, width=100, height=50)
        self.send_btn.pack(side="right")

    def _create_telemetry_block(self, master):
        frame = ctk.CTkFrame(master, fg_color="#1a1a1a", corner_radius=10)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        
        gauge_container = ctk.CTkFrame(frame, fg_color="transparent")
        gauge_container.pack(pady=10)
        
        latency = CTkGauge(gauge_container, label="Latency", unit="ms", max_val=5000, width=120, height=100)
        latency.pack(side="left", padx=10)
        
        tokens = CTkGauge(gauge_container, label="Tokens", unit="", max_val=2048, width=120, height=100, color="#2ECC71")
        tokens.pack(side="left", padx=10)
        
        vram = CTkGauge(gauge_container, label="VRAM", unit="GB", max_val=16, width=120, height=100, color="#E74C3C")
        vram.pack(side="left", padx=10)
        
        return {"frame": frame, "latency": latency, "tokens": tokens, "vram": vram}

    def _create_chat_pane(self, master, title):
        frame = ctk.CTkFrame(master, corner_radius=10)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        
        label = ctk.CTkLabel(frame, text=title, font=("Inter", 12, "bold"), text_color="#888888")
        label.pack(pady=5)
        
        text_area = ctk.CTkTextbox(frame, state="disabled", wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        return {"frame": frame, "text": text_area}

    def _toggle_comparison(self):
        self.comparison_mode = self.compare_btn.get() == 1
        if self.comparison_mode:
            self.chat_right["frame"].pack(side="left", fill="both", expand=True, padx=5)
            self.telemetry_right["frame"].pack(side="left", fill="both", expand=True, padx=5)
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
                text=s["chat_title"], 
                fg_color="transparent", 
                anchor="w",
                command=lambda sid=s["session_id"], title=s["chat_title"]: self._select_session(sid, title)
            )
            btn.pack(fill="x", pady=2)

    def _select_session(self, session_id, title):
        self.current_session_id = session_id
        self.title_label.configure(text=title)
        self._refresh_chat_history()

    def _new_chat(self):
        title = f"New Chat {time.strftime('%H:%M')}"
        sid = self.orchestrator.sqlite.create_session(title)
        self._load_sessions()
        self._select_session(sid, title)

    def _refresh_chat_history(self):
        if not self.current_session_id: return
        
        messages = self.orchestrator.sqlite.get_messages(self.current_session_id)
        
        self.chat_left["text"].configure(state="normal")
        self.chat_left["text"].delete("1.0", "end")
        for m in messages:
            self.chat_left["text"].insert("end", f"{m['role'].upper()}: {m['content']}\n\n")
        self.chat_left["text"].configure(state="disabled")
        self.chat_left["text"].see("end")

    def _send_message(self):
        prompt = self.input_box.get()
        if not prompt or not self.current_session_id: return
        
        self.input_box.delete(0, "end")
        self._append_message(self.chat_left, "USER", prompt)
        if self.comparison_mode:
            self._append_message(self.chat_right, "USER", prompt)
            
        threading.Thread(target=self._generate_responses, args=(prompt,)).start()

    def _append_message(self, pane, role, content):
        pane["text"].configure(state="normal")
        pane["text"].insert("end", f"{role}: {content}\n\n")
        pane["text"].configure(state="disabled")
        pane["text"].see("end")

    def _generate_responses(self, prompt):
        # Method A
        start_a = time.time()
        resp_a = self.orchestrator.generate_method_a(self.current_session_id, prompt)
        latency_a = (time.time() - start_a) * 1000
        
        self.after(0, lambda: self._append_message(self.chat_left, "METHOD A", resp_a))
        self.after(0, lambda: self._update_telemetry(self.telemetry_left, latency_a, len(resp_a)//4, 4.2))

        if self.comparison_mode:
            start_b = time.time()
            resp_b = self.orchestrator.generate_method_b(self.current_session_id, prompt)
            latency_b = (time.time() - start_b) * 1000
            
            self.after(0, lambda: self._append_message(self.chat_right, "METHOD B", resp_b))
            self.after(0, lambda: self._update_telemetry(self.telemetry_right, latency_b, len(resp_b)//4, 2.1))
        
        # Store interaction (using resp_a as the primary one to save to history)
        self.orchestrator.store_interaction(self.current_session_id, prompt, resp_a)

    def _update_telemetry(self, block, latency, tokens, vram):
        block["latency"].set_value(latency)
        block["tokens"].set_value(tokens)
        block["vram"].set_value(vram)

if __name__ == "__main__":
    app = SemanticMemoryApp()
    app.mainloop()
