# backend/routes/run_gui.py

import subprocess
from flask import Blueprint, jsonify, request

gui_bp = Blueprint('gui', __name__)

# New route to launch tkinter app automatically when dashboard is accessed
@gui_bp.route('/auto-launch', methods=['GET'])
def auto_launch_gui():
    try:
        # Launch the tkinter GUI app as a subprocess
        import sys
        import os
        import subprocess
        import platform
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sign_model", "final_pred.py"))
        working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sign_model"))
        python_executable = sys.executable or "python"
        try:
            if platform.system() == "Windows":
                DETACHED_PROCESS = 0x00000008
                subprocess.Popen([python_executable, script_path], cwd=working_dir, creationflags=DETACHED_PROCESS)
            else:
                subprocess.Popen([python_executable, script_path], cwd=working_dir)
            return jsonify({"status": "success", "message": "Sign Language GUI auto-launched."}), 200
        except Exception as sub_e:
            return jsonify({"status": "error", "message": f"Subprocess error: {str(sub_e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
