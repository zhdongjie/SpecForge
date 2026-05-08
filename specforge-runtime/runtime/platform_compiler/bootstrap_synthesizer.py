from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class BootstrapSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = context["application_package"]
        class_name = context["application_class"]
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / f"{class_name}.java"
        write_text(destination, self._source(package_name, class_name))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str, class_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import org.springframework.boot.SpringApplication;\n"
            f"import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
            f"@SpringBootApplication\n"
            f"public class {class_name} {{\n\n"
            f"    public static void main(String[] args) {{\n"
            f"        SpringApplication.run({class_name}.class, args);\n"
            f"    }}\n"
            f"}}\n"
        )
