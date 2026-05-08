from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class PaginationSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.domain.dto"
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "EnquiryPageDto.java"
        write_text(destination, self._source(package_name))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import lombok.AllArgsConstructor;\n"
            f"import lombok.Data;\n"
            f"import lombok.EqualsAndHashCode;\n"
            f"import lombok.NoArgsConstructor;\n\n"
            f"import java.io.Serial;\n"
            f"import java.io.Serializable;\n"
            f"import java.util.Objects;\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f"@EqualsAndHashCode\n"
            f"public class EnquiryPageDto implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"    private Long currentPage;\n"
            f"    private Long pageSize;\n\n"
            f"    public Long getCurrentPage() {{\n"
            f"        return (Objects.isNull(currentPage) || currentPage < 1) ? 1L : currentPage;\n"
            f"    }}\n\n"
            f"    public Long getPageSize() {{\n"
            f"        return (Objects.isNull(pageSize) || pageSize < 1) ? 10L : pageSize;\n"
            f"    }}\n"
            f"}}\n"
        )
