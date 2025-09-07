import sys
import os
import subprocess
import platform

def launch_final_pred():
    python_executable = sys.executable or "python"
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sign_language_app", "final_pred.py"))
    working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "sign_language_app"))
    log_out_path = os.path.join(working_dir, "final_pred_out.log")
    log_err_path = os.path.join(working_dir, "final_pred_err.log")
    with open(log_out_path, "a") as log_out, open(log_err_path, "a") as log_err:
        if platform.system() == "Windows":
            # Use DETACHED_PROCESS flag to detach from parent console
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen([python_executable, script_path], cwd=working_dir,
                             stdout=log_out, stderr=log_err,
                             creationflags=DETACHED_PROCESS)
        else:
            subprocess.Popen([python_executable, script_path], cwd=working_dir,
                             stdout=log_out, stderr=log_err)

if __name__ == "__main__":
    launch_final_pred()
