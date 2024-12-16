"""Check langgraph package structure."""
import os
import langgraph

def inspect_package():
    """Inspect langgraph package location and contents."""
    print("Langgraph package location:", langgraph.__file__)
    print("\nContents of langgraph directory:")
    package_dir = os.path.dirname(langgraph.__file__)
    for item in sorted(os.listdir(package_dir)):
        print(f"- {item}")

if __name__ == "__main__":
    inspect_package()
