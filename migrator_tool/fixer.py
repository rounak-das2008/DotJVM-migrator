import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from .llm_client import LLMClient
from rich.console import Console

console = Console()

class FixerAgent:
    def __init__(self, project_dir: str, llm_client: LLMClient):
        self.project_dir = Path(project_dir).resolve()
        self.llm = llm_client

    def run_build(self) -> Tuple[bool, str]:
        """
        Runs 'mvn clean install' and returns (success, output).
        """
        console.print("[yellow]Running Build...[/yellow]")
        try:
            # Using -DskipTests to focus on compilation errors first if needed, 
            # but let's run full install for now.
            result = subprocess.run(
                ["mvn", "clean", "install", "-e"], 
                cwd=self.project_dir, 
                capture_output=True, 
                text=True
            )
            output = result.stdout + "\n" + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            return (False, str(e))

    def parse_errors(self, build_output: str) -> Dict[str, List[str]]:
        """
        Parses Maven output and returns a dict: {file_path: [error_messages]}.
        """
        errors = {}
        # Regex to capture standard javac errors:
        # [ERROR] /path/to/File.java:[line,col] error message
        # We need to adapt it to the actual absolute paths in the log
        
        # Example: [ERROR] /Users/rounakdas/.../WeatherForecastController.java:[18,50] <identifier> expected
        pattern = re.compile(r"\[ERROR\] (.*?):\[(\d+),(\d+)\] (.*)")
        
        for line in build_output.splitlines():
            match = pattern.search(line)
            if match:
                file_path = match.group(1)
                line_no = match.group(2)
                col_no = match.group(3)
                msg = match.group(4)
                
                # Make relative path for cleaner context if possible
                try:
                    rel_path = str(Path(file_path).relative_to(self.project_dir))
                except ValueError:
                    rel_path = file_path # Absolute if not in project dir

                if rel_path not in errors:
                    errors[rel_path] = []
                errors[rel_path].append(f"Line {line_no}: {msg}")
                
        return errors

    def fix_file(self, file_path: str, error_msgs: List[str]):
        """
        Uses LLM to fix a single file based on error messages.
        """
        full_path = self.project_dir / file_path
        if not full_path.exists():
            console.print(f"[red]File not found: {full_path}[/red]")
            return

        with open(full_path, "r") as f:
            code = f.read()

        prompt = f"""
        The following Java code failed to compile.
        
        File: {file_path}
        
        Errors:
        {chr(10).join(error_msgs)}
        
        Code:
        ```java
        {code}
        ```
        
        Task:
        Fix the compilation errors. Retain the logic. 
        Output ONLY the fixed Java code (complete file).
        """
        
        system_instruction = "You are an expert Java debugger. You fix compilation errors accurately."
        
        console.print(f"[cyan]Fixing {file_path}...[/cyan]")
        fixed_code = self.llm.generate(prompt, system_instruction)
        
        # Strip markdown
        if "```java" in fixed_code:
            fixed_code = fixed_code.split("```java")[1].split("```")[0].strip()
        elif "```" in fixed_code:
             fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
             
        # Backup? Maybe later.
        with open(full_path, "w") as f:
            f.write(fixed_code)

    def auto_heal(self, max_retries: int = 3):
        """
        Main loop: Build -> Detect -> Fix -> Repeat.
        """
        for attempt in range(1, max_retries + 1):
            console.print(f"\n[bold blue]--- Auto-Heal Attempt {attempt}/{max_retries} ---[/bold blue]")
            
            success, output = self.run_build()
            
            if success:
                console.print("[bold green]Build Succeeded![/bold green]")
                return True
            
            console.print("[red]Build Failed. Analyzing errors...[/red]")
            errors = self.parse_errors(output)
            
            if not errors:
                console.print("[red]Build failed but no parseable compiler errors found. Check logs.[/red]")
                # Could be a pom error, missing dependency, etc.
                # In a robust system, we would feed the whole log to LLM.
                return False
                
            for file_path, msgs in errors.items():
                self.fix_file(file_path, msgs)
        
        console.print("[bold red]Max retries reached. Auto-heal failed.[/bold red]")
        return False
