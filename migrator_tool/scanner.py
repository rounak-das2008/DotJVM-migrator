import os
import json
from pathlib import Path
from typing import Dict, List, Any
import pathspec

class ProjectScanner:
    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        self.ignore_spec = pathspec.PathSpec.from_lines(
            'gitwildmatch', 
            ['bin/', 'obj/', '.git/', '.idea/', '.vscode/', '__pycache__/', '*.exe', '*.dll', '*.pdb']
        )

    def scan(self) -> Dict[str, Any]:
        """
        Scans the project directory and returns a dictionary representation
        of the structure and file contents.
        """
        project_structure = {
            "root_name": self.root.name,
            "files": [],
            "directories": []
        }
        
        files_content = {}
        
        for root, dirs, files in os.walk(self.root):
            # Filtering directories in-place
            rel_root = Path(root).relative_to(self.root)
            dirs[:] = [d for d in dirs if not self.ignore_spec.match_file(str(rel_root / d) + "/")]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.root))
                
                if self.ignore_spec.match_file(rel_path):
                    continue
                
                project_structure["files"].append(rel_path)
                
                # We mainly care about .cs, .csproj, .json, .xml, .config
                if file.endswith(('.cs', '.csproj', '.json', '.xml', 'config')):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            files_content[rel_path] = f.read()
                    except Exception:
                        files_content[rel_path] = "<BINARY_OR_UNREADABLE>"

        return {
            "structure": project_structure,
            "contents": files_content
        }

if __name__ == "__main__":
    import sys
    scanner = ProjectScanner(sys.argv[1])
    print(json.dumps(scanner.scan(), indent=2))
