from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class DatasourceSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.config"
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "MyBatisFlexConfiguration.java"
        write_text(destination, self._source(package_name, context["platform_package"]))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str, platform_package: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import org.mybatis.spring.annotation.MapperScan;\n"
            f"import org.springframework.context.annotation.Configuration;\n\n"
            f"@Configuration\n"
            f'@MapperScan(basePackages = "{platform_package}")\n'
            f"public class MyBatisFlexConfiguration {{\n"
            f"}}\n"
        )
