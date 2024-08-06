# debugger.py
import os

DEBUG_MODE = bool(int(os.getenv('FLASK_DEBUG', 0)))
print ("Debug Mode is enabled? " + str(DEBUG_MODE))

def init():
    if True:
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
            import debugpy

            debugpy.listen(("0.0.0.0", 5768))
            print("⏳ VS Code debugger can now be attached, press F5 in VS Code ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 VS Code debugger attached, enjoy debugging 🎉", flush=True)