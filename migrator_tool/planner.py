import json
from .llm_client import LLMClient
from .models import MigrationPlan
from .scanner import ProjectScanner

class MigrationPlanner:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def create_plan(self, scan_result: dict) -> MigrationPlan:
        # 1. Prepare context
        # We focus on project files to determine dependencies and structure
        important_files = {}
        for path, content in scan_result['contents'].items():
            # CSPROJ, Program, Startup are critical for planning
            if path.endswith('.csproj') or path.endswith('Program.cs') or path.endswith('Startup.cs') or path.endswith('appsettings.json'):
                important_files[path] = content
        
        # files_list for structure mapping
        file_list = scan_result['structure']['files']

        prompt = f"""
        Analyze this .NET Core project and create a precise migration plan to a Spring Boot Java application.
        
        Input Files:
        {json.dumps(important_files, indent=2)}
        
        All File Paths:
        {json.dumps(file_list, indent=2)}
        
        Goal:
        1. Identify equivalent Maven dependencies for the NuGet packages.
        2. Map every .cs file to a corresponding Java path following standard Maven layout (src/main/java/com/example/...).
        3. Extract configuration from appsettings.json to application.properties key-values.
        
        Output:
        Return ONLY valid JSON that matches the following schema:
        {{
            "project_name": "...",
            "group_id": "com.example",
            "artifact_id": "migrated-app",
            "java_version": "17",
            "spring_boot_version": "3.2.0",
            "dependencies": [
                {{"group_id": "...", "artifact_id": "...", "version": "..."}}
            ],
            "file_mappings": [
                {{"source_file": "...", "target_path": "...", "package_name": "..."}}
            ],
            "application_properties": {{ "key": "value" }}
        }}
        """

        system_instruction = "You are a Senior Architect specializing in .NET to Java migrations. You output strictly JSON."

        # Call LLM
        response_text = self.llm.generate(prompt, system_instruction)
        
        # Strip markdown if present
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0]
        elif response_text.startswith("```"):
             response_text = response_text.split("```")[1].split("```")[0]

        return MigrationPlan.model_validate_json(response_text)
