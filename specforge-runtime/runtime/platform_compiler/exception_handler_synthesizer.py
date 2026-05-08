from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class ExceptionHandlerSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        exception_package = f"{context['platform_package']}.core.exception"
        business_package = f"{context['platform_package']}.core.exception.business"
        advice_package = f"{context['platform_package']}.core.exception.advice"
        business_path = context["output_root"] / "src" / "main" / "java" / Path(*exception_package.split(".")) / "BusinessException.java"
        field_path = context["output_root"] / "src" / "main" / "java" / Path(*business_package.split(".")) / "FieldValidationException.java"
        advice_path = context["output_root"] / "src" / "main" / "java" / Path(*advice_package.split(".")) / "GlobalExceptionHandler.java"
        write_text(business_path, self._business_exception(exception_package))
        write_text(field_path, self._field_exception(business_package, exception_package))
        write_text(advice_path, self._advice(advice_package, exception_package, business_package, context["platform_package"]))
        return {"artifact_count": 3, "artifacts": [str(business_path), str(field_path), str(advice_path)]}

    def _business_exception(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"public class BusinessException extends RuntimeException {{\n"
            f"    public BusinessException(String message) {{\n"
            f"        super(message);\n"
            f"    }}\n"
            f"}}\n"
        )

    def _field_exception(self, package_name: str, exception_package: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import {exception_package}.BusinessException;\n\n"
            f"public class FieldValidationException extends BusinessException {{\n\n"
            f"    private final String field;\n\n"
            f"    public FieldValidationException(String field, String message) {{\n"
            f"        super(message);\n"
            f"        this.field = field;\n"
            f"    }}\n\n"
            f"    public String getField() {{\n"
            f"        return field;\n"
            f"    }}\n"
            f"}}\n"
        )

    def _advice(self, package_name: str, exception_package: str, business_package: str, platform_package: str) -> str:
        vo_package = f"{platform_package}.core.domain.vo"
        return (
            f"package {package_name};\n\n"
            f"import {business_package}.FieldValidationException;\n"
            f"import {exception_package}.BusinessException;\n"
            f"import {vo_package}.FieldErrorVo;\n"
            f"import {vo_package}.ResponseVo;\n"
            f"import org.springframework.http.ResponseEntity;\n"
            f"import org.springframework.validation.BindException;\n"
            f"import org.springframework.web.bind.MethodArgumentNotValidException;\n"
            f"import org.springframework.web.bind.annotation.ExceptionHandler;\n"
            f"import org.springframework.web.bind.annotation.RestControllerAdvice;\n\n"
            f"import java.util.List;\n\n"
            f"@RestControllerAdvice\n"
            f"public class GlobalExceptionHandler {{\n\n"
            f"    @ExceptionHandler(FieldValidationException.class)\n"
            f"    public ResponseEntity<ResponseVo<Void>> handleFieldValidation(FieldValidationException exception) {{\n"
            f"        return ResponseEntity.badRequest().body(ResponseVo.fail(List.of(new FieldErrorVo(exception.getField(), exception.getMessage()))));\n"
            f"    }}\n\n"
            f"    @ExceptionHandler(BusinessException.class)\n"
            f"    public ResponseEntity<ResponseVo<Void>> handleBusiness(BusinessException exception) {{\n"
            f"        return ResponseEntity.badRequest().body(ResponseVo.fail(exception.getMessage()));\n"
            f"    }}\n\n"
            f"    @ExceptionHandler({{MethodArgumentNotValidException.class, BindException.class}})\n"
            f"    public ResponseEntity<ResponseVo<Void>> handleValidation(Exception exception) {{\n"
            f"        return ResponseEntity.badRequest().body(ResponseVo.fail(\"VALIDATION_FAILED\"));\n"
            f"    }}\n\n"
            f"    @ExceptionHandler(Exception.class)\n"
            f"    public ResponseEntity<ResponseVo<Void>> handleUnexpected(Exception exception) {{\n"
            f"        return ResponseEntity.internalServerError().body(ResponseVo.fail(exception.getMessage()));\n"
            f"    }}\n"
            f"}}\n"
        )
