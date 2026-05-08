import sys
from memory_engine.gui.app import SemanticMemoryApp

if __name__ == "__main__":
    app = SemanticMemoryApp()
    sys.exit(app.run(sys.argv))
