import customtkinter as ctk
import math

class CTkGauge(ctk.CTkCanvas):
    def __init__(self, master, label="Metric", min_val=0, max_val=100, unit="", color="#6C63FF", **kwargs):
        # Resolve the background color properly from customtkinter
        bg_color = self._get_bg_color(master)
        
        super().__init__(master, highlightthickness=0, bg=bg_color, **kwargs)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.color = color
        self.value = min_val
        
        self.bind("<Configure>", lambda e: self.draw())

    def _get_bg_color(self, master):
        try:
            fg_color = master.cget("fg_color")
            if fg_color == "transparent":
                return self._get_bg_color(master.master)
            return master._apply_appearance_mode(fg_color)
        except (AttributeError, ValueError):
            try:
                return master.cget("bg")
            except Exception:
                return "#13131A"

    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.draw()

    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1: return

        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 15
        thickness = 12
        
        # Background Ring (Darker shade)
        self.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="#333345", width=thickness
        )
        
        # Progress Arc (Doughnut style)
        percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
        extent = 359.99 * percentage # Almost full circle
        
        if extent > 0:
            self.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=90, extent=-extent, outline=self.color, width=thickness, style="arc"
            )
        
        # Center Text (Value)
        val_text = f"{self.value:.1f}{self.unit}" if self.unit else f"{int(self.value)}"
        self.create_text(
            center_x, center_y - 5, 
            text=val_text, 
            fill="white", 
            font=("Roboto", 14, "bold")
        )
        
        # Label Text (Below Value)
        self.create_text(
            center_x, center_y + 15, 
            text=self.label, 
            fill="#A0A0B0", 
            font=("Roboto", 10)
        )
