from .llm_client import LLMClient
from .models import MigrationPlan

class CodeTranslator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def translate_file(self, source_code: str, file_mapping: dict, plan: MigrationPlan) -> str:
        prompt = f"""
        Translate the following C#/.NET Core code to a SINGLE Java class (Spring Boot/Lombok).
        
        Target Context:
        - Package Name: {file_mapping.package_name}
        - Spring Boot Version: {plan.spring_boot_version}
        - Dependencies available: {[d.artifact_id for d in plan.dependencies]}
        
        CRITICAL RULES:
        1. Output ONLY the Java code for the one class corresponding to the input file. 
        2. Do NOT include any other classes in the same response.
        3. Do NOT include markdown formatting or comments like '// Path: ...'.
        4. Ensure the package declaration matches `{file_mapping.package_name}`.
        5. Use Lombok @Data for models, @RestController for controllers.
        
        Source C# Code:
        {source_code}
        """
        
        system_instruction = "You are an expert Java Developer. Output strictly valid Java code."
        
        response = self.llm.generate(prompt, system_instruction)
        
        # Cleanup
        if "```java" in response:
            return response.split("```java")[1].split("```")[0].strip()
        if "```" in response:
            return response.split("```")[1].split("```")[0].strip()
            
        return response.strip()
