import customtkinter as ctk
import math

class CTkGauge(ctk.CTkCanvas):
    def __init__(self, master, label="Metric", min_val=0, max_val=100, unit="", color="#3B8ED0", **kwargs):
        super().__init__(master, highlightthickness=0, bg=master._apply_appearance_mode(master._fg_color), **kwargs)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.color = color
        self.value = min_val
        
        self.bind("<Configure>", lambda e: self.draw())

    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.draw()

    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1: return

        center_x = width / 2
        center_y = height * 0.8
        radius = min(width / 2, height * 0.7) - 10
        
        # Background arc
        self.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=0, extent=180, outline="#333333", width=10, style="arc"
        )
        
        # Value arc
        percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
        extent = 180 * percentage
        self.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=180, extent=-extent, outline=self.color, width=10, style="arc"
        )
        
        # Label and value text
        self.create_text(center_x, center_y - 20, text=f"{self.value:.1f}{self.unit}", fill="white", font=("Inter", 16, "bold"))
        self.create_text(center_x, center_y + 10, text=self.label, fill="#888888", font=("Inter", 10))
