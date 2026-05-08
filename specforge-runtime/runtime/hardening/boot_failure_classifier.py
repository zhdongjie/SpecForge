from __future__ import annotations

from typing import Any


class BootFailureClassifier:
    def classify(self, output: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if "Error creating bean" in output:
            findings.append({"category": "bean_creation_failure"})
        if "Failed to configure a DataSource" in output:
            findings.append({"category": "datasource_failure"})
        if "Mapper" in output and "not found" in output:
            findings.append({"category": "mapper_scan_failure"})
        if "sqlSessionFactory" in output or "sqlSessionTemplate" in output:
            findings.append({"category": "mapper_scan_failure"})
        if "RedisConnectionFailureException" in output:
            findings.append({"category": "redis_connection_failure"})
        if "Failed to bind properties" in output or "Could not resolve placeholder" in output:
            findings.append({"category": "missing_property"})
        if "The dependencies of some of the beans in the application context form a cycle" in output:
            findings.append({"category": "circular_dependency"})
        if "Ambiguous mapping" in output:
            findings.append({"category": "controller_mapping_conflict"})
        if "SecurityFilterChain" in output and "BeanCreationException" in output:
            findings.append({"category": "security_initialization_failure"})
        return findings
