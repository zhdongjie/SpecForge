from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class MapperSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        artifacts: list[str] = []
        for entity_name in sorted(context["schema"].get("entities", {})):
            mapper_name = f"{entity_name}Mapper"
            package_name = f"{context['package_root']}.mapper"
            source = (
                f"package {package_name};\n\n"
                f"import com.mybatisflex.core.BaseMapper;\n"
                f"import {context['package_root']}.domain.entity.{entity_name};\n"
                f"import org.apache.ibatis.annotations.Mapper;\n\n"
                f"@Mapper\n"
                f"public interface {mapper_name} extends BaseMapper<{entity_name}> {{\n"
                f"}}\n"
            )
            destination = (
                context["output_root"]
                / "src"
                / "main"
                / "java"
                / Path(*package_name.split("."))
                / f"{mapper_name}.java"
            )
            write_text(destination, source)
            artifacts.append(str(destination))
        return {"artifact_count": len(artifacts), "artifacts": artifacts}
