import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TelemetryBlock:
    def __init__(self, title):
        self.expander = Gtk.Expander()
        self.expander.set_expanded(False)
        self.expander.get_style_context().add_class("panel")
        self.expander.set_hexpand(True)
        
        # Custom label box to maintain the "accent" look
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_size_request(-1, 40)
        title_lbl = Gtk.Label(label=title, xalign=0)
        title_lbl.get_style_context().add_class("accent-label")
        header_box.pack_start(title_lbl, True, True, 0)
        self.expander.set_label_widget(header_box)
        
        # Internal Content
        self.inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.inner.set_margin_top(20)
        self.inner.set_margin_bottom(20)
        self.inner.set_margin_start(25)
        self.inner.set_margin_end(25)
        self.expander.add(self.inner)

        self.latency = self._add_metric("LATENCY_MS", "latency")
        self.tokens = self._add_metric("TOKENS_GEN", "tokens")
        self.vram = self._add_metric("VRAM_GB", "vram")

    def _add_metric(self, label, css_class):
        met_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.inner.pack_start(met_box, False, False, 0)
        
        lbl = Gtk.Label(label=label, xalign=0)
        lbl.get_style_context().add_class("secondary-label")
        met_box.pack_start(lbl, False, False, 0)
        
        # Using ProgressBar for reliable dynamic fill
        bar = Gtk.ProgressBar()
        bar.get_style_context().add_class(css_class)
        met_box.pack_start(bar, False, False, 0)
        
        val_lbl = Gtk.Label(label="[ 0.00 ]", xalign=1)
        val_lbl.get_style_context().add_class("primary-text")
        met_box.pack_start(val_lbl, False, False, 0)
        return {"bar": bar, "label": val_lbl}

    def update(self, latency, tokens, vram):
        # Progress bars use fraction [0.0 to 1.0]
        self.latency["bar"].set_fraction(min(1.0, latency / 2500.0)) # 2500ms max
        self.latency["label"].set_text(f"[ {latency:.1f} ms ]")
        
        self.tokens["bar"].set_fraction(min(1.0, tokens / 150.0)) # 150 tokens max
        self.tokens["label"].set_text(f"[ {int(tokens)} T ]")
        
        # Calibration: 8GB focus range for better visual density
        self.vram["bar"].set_fraction(min(1.0, vram / 8.0)) 
        self.vram["label"].set_text(f"[ {vram:.2f} GB ]")

    @property
    def container(self):
        return self.expander
