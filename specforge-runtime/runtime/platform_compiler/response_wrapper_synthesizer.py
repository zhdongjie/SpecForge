from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class ResponseWrapperSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.domain.vo"
        field_error_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "FieldErrorVo.java"
        response_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "ResponseVo.java"
        page_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "PageVo.java"
        write_text(field_error_path, self._field_error_source(package_name))
        write_text(response_path, self._response_source(package_name))
        write_text(page_path, self._page_source(package_name))
        return {"artifact_count": 3, "artifacts": [str(field_error_path), str(response_path), str(page_path)]}

    def _field_error_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import lombok.AllArgsConstructor;\n"
            f"import lombok.Data;\n"
            f"import lombok.NoArgsConstructor;\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f"public class FieldErrorVo {{\n"
            f"    private String field;\n"
            f"    private String message;\n"
            f"}}\n"
        )

    def _response_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import lombok.AllArgsConstructor;\n"
            f"import lombok.Data;\n"
            f"import lombok.NoArgsConstructor;\n\n"
            f"import java.util.List;\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f"public class ResponseVo<T> {{\n\n"
            f"    private Integer code;\n"
            f"    private String message;\n"
            f"    private List<FieldErrorVo> errors;\n"
            f"    private T data;\n"
            f"    private Long timestamp;\n\n"
            f"    public static <T> ResponseVo<T> success() {{\n"
            f"        return success(null);\n"
            f"    }}\n\n"
            f"    public static <T> ResponseVo<T> success(T data) {{\n"
            f"        return new ResponseVo<>(200, \"OK\", null, data, System.currentTimeMillis());\n"
            f"    }}\n\n"
            f"    public static <T> ResponseVo<T> fail(String message) {{\n"
            f"        return new ResponseVo<>(400, message, null, null, System.currentTimeMillis());\n"
            f"    }}\n\n"
            f"    public static <T> ResponseVo<T> fail(List<FieldErrorVo> errors) {{\n"
            f"        return new ResponseVo<>(400, \"VALIDATION_FAILED\", errors, null, System.currentTimeMillis());\n"
            f"    }}\n\n"
            f"    public static <T> ResponseVo<T> unauthorized() {{\n"
            f"        return new ResponseVo<>(401, \"UNAUTHORIZED\", null, null, System.currentTimeMillis());\n"
            f"    }}\n\n"
            f"    public static <T> ResponseVo<T> forbidden() {{\n"
            f"        return new ResponseVo<>(403, \"FORBIDDEN\", null, null, System.currentTimeMillis());\n"
            f"    }}\n"
            f"}}\n"
        )

    def _page_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import lombok.AllArgsConstructor;\n"
            f"import lombok.Data;\n"
            f"import lombok.NoArgsConstructor;\n\n"
            f"import java.util.List;\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f"public class PageVo<T> {{\n"
            f"    private Long total;\n"
            f"    private List<T> records;\n"
            f"}}\n"
        )
