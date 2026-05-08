from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class CompileErrorClassifier:
    def classify(self, output: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        findings.extend(self._classify_environment(output))
        findings.extend(self._classify_duplicate_constructor(output))
        findings.extend(self._classify_unresolved_symbol(output))
        findings.extend(self._classify_package_errors(output))
        findings.extend(self._classify_dependency_errors(output))
        return self._deduplicate(findings)

    def _classify_environment(self, output: str) -> list[dict[str, Any]]:
        if "class file has wrong version 61.0" in output or "release version 17 not supported" in output:
            return [
                {
                    "category": "environment_jdk_mismatch",
                    "message": "Compiler requires JDK 17 or newer",
                    "evidence": "java-class-version-mismatch",
                }
            ]
        return []

    def _classify_duplicate_constructor(self, output: str) -> list[dict[str, Any]]:
        pattern = re.compile(
            r"\[ERROR\]\s+(?P<file>.+?\.java):\[(?P<line>\d+),(?P<column>\d+)\]\s+constructor\s+"
            r"(?P<constructor>[A-Za-z0-9_]+)\s+in class .* cannot be applied to given types;",
            re.MULTILINE,
        )
        findings: list[dict[str, Any]] = []
        for match in pattern.finditer(output):
            path = match.group("file").replace("\\", "/")
            if not Path(path).name.startswith("Enquiry"):
                continue
            findings.append(
                {
                    "category": "duplicate_constructor",
                    "file": path,
                    "line": int(match.group("line")),
                    "column": int(match.group("column")),
                    "symbol": match.group("constructor"),
                }
            )
        return findings

    def _classify_unresolved_symbol(self, output: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        lines = output.splitlines()
        for index, line in enumerate(lines):
            if (
                "cannot find symbol" not in line
                and "找不到符号" not in line
                and "鎵句笉鍒扮鍙" not in line
            ):
                continue
            file_match = re.search(r"\[ERROR\]\s+(.+?\.java):\[(\d+),(\d+)\]", line)
            symbol_line = lines[index + 1] if index + 1 < len(lines) else ""
            location_line = lines[index + 2] if index + 2 < len(lines) else ""
            symbol_match = re.search(r"(?:symbol|绗﹀彿):\s+(?:variable\s+)?([A-Za-z0-9_\-]+)", symbol_line)
            location_match = re.search(r"(?:location|浣嶇疆):\s+(?:class\s+)?([A-Za-z0-9_.$?]+)", location_line)
            if not file_match:
                continue
            findings.append(
                {
                    "category": "unresolved_symbol",
                    "file": file_match.group(1).replace("\\", "/"),
                    "line": int(file_match.group(2)),
                    "column": int(file_match.group(3)),
                    "symbol": symbol_match.group(1) if symbol_match else None,
                    "location": location_match.group(1) if location_match else None,
                }
            )
        return findings

    def _classify_package_errors(self, output: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if "package " in output and "does not exist" in output:
            findings.append(
                {
                    "category": "package_mismatch",
                    "message": "One or more imported packages do not exist",
                }
            )
        if "duplicate class:" in output:
            findings.append(
                {
                    "category": "duplicate_class",
                    "message": "Duplicate class declaration detected",
                }
            )
        return findings

    def _classify_dependency_errors(self, output: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if "dependencies.dependency.version" in output or "Could not resolve dependencies" in output:
            findings.append(
                {
                    "category": "missing_dependency",
                    "message": "Maven dependency resolution failed",
                }
            )
        if "expected" in output and "found" in output and "cannot be converted" in output:
            findings.append(
                {
                    "category": "generic_mismatch",
                    "message": "Generic type mismatch detected",
                }
            )
        return findings

    def _deduplicate(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[Any, ...]] = set()
        deduped: list[dict[str, Any]] = []
        for finding in findings:
            key = (
                finding.get("category"),
                finding.get("file"),
                finding.get("line"),
                finding.get("symbol"),
                finding.get("message"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(finding)
        return deduped
