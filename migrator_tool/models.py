from pydantic import BaseModel, Field
from typing import List, Dict

class MavenDependency(BaseModel):
    group_id: str
    artifact_id: str
    version: str | None = Field(default=None, description="Can be explicit version or 'managed' if using BOM")
    scope: str = "compile"

class FileMapping(BaseModel):
    source_file: str = Field(description="Relative path of the source .NET file")
    target_path: str = Field(description="Relative path of the target Java file (e.g. src/main/java/...)")
    package_name: str = Field(description="Java package name for this file")

class MigrationPlan(BaseModel):
    project_name: str
    group_id: str = "com.example"
    artifact_id: str = "demo"
    java_version: str = "17"
    spring_boot_version: str = "3.2.0"
    dependencies: List[MavenDependency]
    file_mappings: List[FileMapping]
    application_properties: Dict[str, str] = Field(description="Key-value pairs for application.properties")
