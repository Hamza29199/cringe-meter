"""Copy the shared meter into the extension folder (the extension cannot reference ../web).
    python build_extension.py
Run after any change to web/meter.js."""
import shutil, os
here = os.path.dirname(os.path.abspath(__file__))
shutil.copyfile(os.path.join(here, "web", "meter.js"), os.path.join(here, "extension", "meter.js"))
print("extension/meter.js updated from web/meter.js")
