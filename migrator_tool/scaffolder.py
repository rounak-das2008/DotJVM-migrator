import os
from pathlib import Path
from .models import MigrationPlan

class ProjectScaffolder:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir).resolve()

    def create_structure(self, plan: MigrationPlan):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Create standard maven layout
        (self.output_dir / "src/main/java").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "src/main/resources").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "src/test/java").mkdir(parents=True, exist_ok=True)

    def write_file(self, relative_path: str, content: str):
        full_path = self.output_dir / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def generate_pom(self, plan: MigrationPlan) -> str:
        deps = ""
        for d in plan.dependencies:
            deps += f"""
        <dependency>
            <groupId>{d.group_id}</groupId>
            <artifactId>{d.artifact_id}</artifactId>
            <version>{d.version}</version>
        </dependency>"""

        pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>{plan.spring_boot_version}</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>{plan.group_id}</groupId>
    <artifactId>{plan.artifact_id}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>{plan.project_name}</name>
    <description>Migrated Project</description>
    <properties>
        <java.version>{plan.java_version}</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        {deps}
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""
        return pom_content

    def generate_application_properties(self, plan: MigrationPlan) -> str:
        props = ""
        for k, v in plan.application_properties.items():
            props += f"{k}={v}\n"
        return props
