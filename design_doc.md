# Project Ideation: .NET to Java AI Migration Agent

## 1. Executive Summary
**Project Name:** (Proposed) `TransmuteAI` or `BridgeMigrator`
**Goal:** A standalone command-line interface (CLI) tool that accepts a .NET Core project directory as input and produces a fully functional, buildable Java (Spring Boot) project directory as output, preserving file structure, logic, and functionality.
**Core Tech:** Python (for the tool logic), Google Vertex AI (Gemini models), Google Cloud Storage (optional, mostly local processing with ADC).

## 2. Architecture Overview

The tool will operate in a pipeline of 4 distinct phases:

### Phase 1: Discovery & Analysis (The "Scanner")
*   **Input:** Path to .NET project.
*   **Action:**
    *   Recursively maps the folder structure.
    *   Identifies key files: `.csproj` (dependencies), `appsettings.json` (config), `Program.cs`/`Startup.cs` (Entry point & DI).
    *   Constructs a "Context map" of the existing application.
*   **Output:** A JSON representation of the project structure and key components.

### Phase 2: Migration Planning (The "Architect")
*   **Input:** Phase 1 JSON + Key file contents.
*   **Action:**
    *   Uses Vertex AI (Gemini 1.5 Pro) to analyze the dependencies.
    *   **Mapping Strategy:**
        *   `ASP.NET Core` -> `Spring Boot Web`
        *   `Entity Framework` -> `Spring Data JPA / Hibernate`
        *   `xUnit/NUnit` -> `JUnit 5`
        *   `NuGet` packages -> `Maven` dependencies
    *   Generates a `MigrationPlan` object: detailed instructions on which libraries to use in Java.
*   **Output:** A `migration_plan.json` and a draft `pom.xml`.

### Phase 3: Structural Synthesis (The "Builder")
*   **Action:**
    *   Creates the target Java directory structure.
    *   Respects standard Java conventions (e.g., `src/main/java/com/example/...`) while trying to mirror the logical structure of the .NET app (Controllers, Models, Services).
    *   Generates the build files (`pom.xml` or `build.gradle`).
    *   Generates the configuration (`application.properties` from `appsettings.json`).

### Phase 4: Intelligent Translation (The "Coder")
*   **Action:**
    *   Iterates through each source C# file.
    *   **Prompt Engineering:** Sends the C# code + The Migration Plan + Reference Project Context to the LLM.
    *   **Task:** "Translate this C# class to a Java class using Spring Boot annotations as defined in the plan."
    *   Writes the resulting Java files to their corresponding new paths.

## 3. Technical Decisions for POC

### A. The Tool Language: Python
*   **Why:** Excellent ecosystem for string manipulation, file I/O, and Vertex AI SDK support. Easy to package as a standalone executable (using PyInstaller) for Windows/Mac/Linux distribution later.

### B. The Target Stack: Spring Boot
*   **Why:** It is the closest "enterprise standard" equivalent to ASP.NET Core. 1:1 mappings are conceptually easier (Controller -> Controller, Service -> Service, Dependency Injection is built-in).

### C. LLM Strategy: Google Vertex AI (Gemini 1.5 Pro)
*   **Why:** Huge context window (1M-2M tokens). You can potentially fit the *entire* small .NET project into context to ensure the translation of one file understands the references to another (like Models).
*   **Cost Optimization:** Use `Gemini 1.5 Flash` for file discovery/simple mappings, `Gemini 1.5 Pro` for complex logic translation.

## 4. Proposed POC Workflow (What we will build now)

We will build a `migrator.py` script with the following commands:

1.  `python migrator.py analyze ./MyDotNetApp`
    *   Prints out the detected structure and proposed Java dependencies.
2.  `python migrator.py migrate ./MyDotNetApp ./OutputJavaApp`
    *   Executes the full translation.

## 5. Development Roadmap

1.  **Setup**: Initialize Python environment and Vertex AI connection.
2.  **Mock Data**: Create a tiny "Hello World" ASP.NET Core Web API (WeatherForecast is the standard).
3.  **Discovery Module**: Write code to walk the directory and identify `.cs` files.
4.  **Translation Module**: Implement the prompt to convert C# -> Java.
5.  **Assembly**: Glue it together to write the files.
6.  **Verification**: Attempt to run `mvn clean install` on the output.

## 6. Prompt Engineering Strategy

We will use a **System Instruction** for the LLM:
> "You are an expert Backend Engineer fluent in both C#/.NET Core and Java/Spring Boot. Your task is to port code accurately, preserving logic but adapting idioms. You will change PascalCase to camelCase for methods, use Lombok for POJOs, and map attributes to annotations."
