# --- Brutalist Dark Mode CSS ---
CSS = b"""
* {
    font-family: "JetBrains Mono", "monospace";
    border-radius: 0;
    outline: none;
}

window {
    background-color: #0B0B0F;
}

.sidebar {
    background-color: #14141D;
    border-right: 1px solid #2A2A35;
}

.main-view {
    background-color: #0B0B0F;
}

.panel {
    background-color: #14141D;
    border: 1px solid #2A2A35;
}

label {
    color: #FFFFFF;
}

.header-label {
    font-size: 24px;
    font-weight: bold;
    color: #00E5FF;
}

.accent-label {
    color: #00E5FF;
}

.secondary-label {
    color: #A0A0B0;
}

.primary-text {
    color: #FFFFFF;
}

button {
    background-color: transparent;
    border: 1px solid #2A2A35;
    color: #FFFFFF;
    padding: 8px 16px;
    transition: background-color 0.2s;
}

button:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

button.accent {
    border-color: #00E5FF;
    color: #00E5FF;
}

button.accent:hover {
    background-color: rgba(0, 229, 255, 0.1);
}

button.danger {
    border-color: #FF4B4B;
    color: #FF4B4B;
}

button.danger:hover {
    background-color: rgba(255, 75, 75, 0.1);
}

button.execute {
    background-color: #00E5FF;
    color: #000000;
    font-weight: bold;
    font-size: 18px;
    border: none;
}

button.execute:hover {
    background-color: #00B2CC;
}

entry {
    background-color: #14141D;
    border: 1px solid #2A2A35;
    color: #FFFFFF;
    padding: 12px;
    font-size: 16px;
}

entry:focus {
    border-color: #00E5FF;
}

textview text {
    background-color: #0D0D14;
    color: #FFFFFF;
}

scrolledwindow {
    border: 1px solid #2A2A35;
}

progressbar trough {
    background-color: #0D0D14;
    border: 1px solid #2A2A35;
    min-height: 12px;
}

progressbar progress {
    background-color: #00E5FF;
    border: none;
}

.latency progress { background-color: #00E5FF; }
.tokens progress { background-color: #BF00FF; }
.vram progress { background-color: #FF0055; }

list {
    background-color: transparent;
}

row {
    background-color: transparent;
    padding: 12px;
    border-bottom: 1px solid #1A1A25;
}

row:selected {
    background-color: #1A1A25;
}

row label {
    color: #A0A0B0;
}

row:selected label {
    color: #00E5FF;
}

paned separator {
    background-color: #2A2A35;
    min-width: 2px;
    min-height: 2px;
}

expander {
    background-color: #14141D;
    border: 1px solid #2A2A35;
}

expander > title {
    padding: 10px 20px;
}

switch {
    background-color: #14141D;
    border: 1px solid #2A2A35;
    color: #00E5FF;
}

switch:checked {
    background-color: #00E5FF;
}
"""
