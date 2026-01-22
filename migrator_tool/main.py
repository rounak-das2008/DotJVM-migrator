import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import os
from .llm_client import LLMClient
from .scanner import ProjectScanner
from .planner import MigrationPlanner
from .translator import CodeTranslator
from .scaffolder import ProjectScaffolder
from .fixer import FixerAgent

app = typer.Typer()
console = Console()

@app.command()
def fix(project_dir: str, project_id: str = None, retries: int = 3):
    """
    Iteratively attempts to fix compilation errors in a Maven project.
    """
    llm = LLMClient(project_id=project_id)
    agent = FixerAgent(project_dir, llm)
    agent.auto_heal(max_retries=retries)

@app.command()
def analyze(input_dir: str, project_id: str = None):
    """
    Analyzes the .NET project and proposes a migration plan.
    """
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Scanning project...", total=None)
        scanner = ProjectScanner(input_dir)
        scan_result = scanner.scan()
        
        progress.add_task(description="Planning migration (consulting AI)...", total=None)
        llm = LLMClient(project_id=project_id)
        planner = MigrationPlanner(llm)
        plan = planner.create_plan(scan_result)

    console.print("[green]Analysis Complete![/green]")
    console.print_json(plan.model_dump_json())

@app.command()
def migrate(input_dir: str, output_dir: str, project_id: str = None):
    """
    Full migration: Analysis -> Planning -> Translation -> Code Generation.
    """
    llm = LLMClient(project_id=project_id)
    
    # 1. Scan
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task1 = progress.add_task(description="Scanning project...", total=None)
        scanner = ProjectScanner(input_dir)
        scan_result = scanner.scan()
        
    # 2. Plan
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task2 = progress.add_task(description="Generating Migration Plan...", total=None)
        planner = MigrationPlanner(llm)
        plan = planner.create_plan(scan_result)
        
    console.print(f"[blue]Plan generated: {plan.project_name} -> {plan.artifact_id}[/blue]")

    # 3. Scaffold
    scaffolder = ProjectScaffolder(output_dir)
    scaffolder.create_structure(plan)
    
    # 4. Translate
    translator = CodeTranslator(llm)
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task3 = progress.add_task(description="Translating files...", total=len(plan.file_mappings))
        
        for mapping in plan.file_mappings:
            # Find content
            source_content = scan_result['contents'].get(mapping.source_file)
            if not source_content:
                console.print(f"[red]Warning: Could not find content for {mapping.source_file}[/red]")
                continue
                
            progress.update(task3, description=f"Translating {mapping.source_file}...")
            
            # Translate
            java_code = translator.translate_file(source_content, mapping, plan)
            
            # Write
            scaffolder.write_file(mapping.target_path, java_code)
            progress.advance(task3)

    # 5. Metadata
    console.print("[yellow]Generating Build Files...[/yellow]")
    pom_xml = scaffolder.generate_pom(plan)
    scaffolder.write_file("pom.xml", pom_xml)
    
    props = scaffolder.generate_application_properties(plan)
    scaffolder.write_file("src/main/resources/application.properties", props)
    
    console.print(f"[green]Migration Complete! Output at: {output_dir}[/green]")
    console.print("Try running: [bold]mvn clean install[/bold] in the output directory.")

if __name__ == "__main__":
    app()
