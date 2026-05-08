import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ChatPane:
    def __init__(self, title):
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.container.get_style_context().add_class("panel")
        self.container.set_hexpand(True)

        header = Gtk.Label(label=f"// {title}", xalign=0)
        header.get_style_context().add_class("secondary-label")
        header.set_margin_top(15)
        header.set_margin_start(20)
        header.set_margin_bottom(10)
        self.container.pack_start(header, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.container.pack_start(scrolled, True, True, 0)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_left_margin(20)
        self.text_view.set_right_margin(20)
        self.text_view.set_top_margin(20)
        self.text_view.set_bottom_margin(20)
        scrolled.add(self.text_view)

    def append_message(self, role, content):
        buffer = self.text_view.get_buffer()
        safe_content = str(content)
        buffer.insert(buffer.get_end_iter(), f"[{role}] >> {safe_content}\n\n")
        self.scroll_to_end()

    def set_text(self, text):
        self.text_view.get_buffer().set_text(text)

    def scroll_to_end(self):
        buffer = self.text_view.get_buffer()
        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
