import sys
import os

# Define current_dir and ensure it is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Ensure parent of src is in python path to allow 'from src...' imports
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.infrastructure.container import Container

def verify_wiring():
    print("Initializing Container...")
    try:
        container = Container()
    except Exception as e:
        print(f"Failed to initialize Container: {e}")
        return

    # We need to set environment variables or mock them for resources
    # But for wiring check, we assume env vars might be missing but container definition is valid.
    
    print("Checking BotController...")
    try:
        # We need to manually wire or provide resources if they are Resources
        # providers.Resource executes the function. 'get_db' and 'get_redis_client' might fail if env vars are missing.
        # However, we are just checking if they are wired.
        controller = container.bot_controller()
        print(f"BotController resolved: {controller}")
    except Exception as e:
        print(f"Failed to resolve BotController: {e}")
        # Detailed error might help
        import traceback
        traceback.print_exc()

    print("Checking Session Repository...")
    try:
        repo = container.session_repository()
        print(f"SessionRepository resolved: {repo}")
    except Exception as e:
        print(f"Failed to resolve SessionRepository: {e}")

    print("Verification execution finished.")

if __name__ == "__main__":
    verify_wiring()
