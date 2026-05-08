from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class BaseEntitySynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.domain.entity"
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "PrimaryKeyEntity.java"
        write_text(destination, self._source(package_name))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import com.mybatisflex.annotation.Id;\n"
            f"import com.mybatisflex.annotation.KeyType;\n"
            f"import com.mybatisflex.core.keygen.KeyGenerators;\n"
            f"import lombok.AllArgsConstructor;\n"
            f"import lombok.Data;\n"
            f"import lombok.NoArgsConstructor;\n\n"
            f"import java.io.Serial;\n"
            f"import java.io.Serializable;\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f"public class PrimaryKeyEntity implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"    @Id(keyType = KeyType.Generator, value = KeyGenerators.flexId)\n"
            f"    private Long id;\n"
            f"}}\n"
        )
