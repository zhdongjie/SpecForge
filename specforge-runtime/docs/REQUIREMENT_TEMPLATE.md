# Requirement Template

Use this template when you do not want to rely on a one-line requirement only.

Save it as a markdown file and pass it with:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement-file "<file>" --run-id <run-id> --force
```

## Template

```md
# Project Name

<project name>

## Project Goal

Build a complete graduation-project-grade Spring Boot backend.

## Domain

<domain name>

## Core Business Centers

- <business center 1>
- <business center 2>
- <business center 3>
- <business center 4>
- <business center 5>

## Primary Roles

- administrator
- operator
- reviewer
- end user

## Core Flows

- <core flow 1>
- <core flow 2>
- <core flow 3>

## Required Platform Rules

- modular-monolith architecture
- JWT authentication
- business modules under org.eu.originalkeen.business.*
- business routes under /v1/business/*
- business authorities under business:*

## Completeness Expectations

- do not generate a thin CRUD skeleton
- prefer business-center level module splitting
- include user/role/menu linkage as a project-level concern
- include database initialization SQL organization as a project-level concern
- require compile verification
- require boot verification

## Optional Domain Notes

- <note 1>
- <note 2>
```

## Laboratory Example

```md
# Project Name

Laboratory Management Platform

## Project Goal

Build a complete graduation-project-grade Spring Boot backend.

## Domain

laboratory management

## Core Business Centers

- laboratory resource management
- experiment project management
- equipment management
- consumable inventory management
- laboratory reservation management
- reservation approval management
- laboratory access management
- notification management
- schedule calendar management
- report statistics management

## Primary Roles

- system administrator
- laboratory administrator
- teacher
- student
- reviewer

## Core Flows

- laboratory resource maintenance
- reservation submission and approval
- equipment and consumable coordination
- access control and notification delivery
- statistics and reporting

## Required Platform Rules

- modular-monolith architecture
- JWT authentication
- business modules under org.eu.originalkeen.business.*
- business routes under /v1/business/*
- business authorities under business:*

## Completeness Expectations

- do not generate a thin CRUD skeleton
- prefer business-center level module splitting
- include user/role/menu linkage as a project-level concern
- include database initialization SQL organization as a project-level concern
- require compile verification
- require boot verification
```
