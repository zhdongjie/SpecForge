from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class OperationLogSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        annotation_package = f"{context['platform_package']}.core.annotation"
        enum_package = f"{context['platform_package']}.core.enums"
        aspect_package = f"{context['platform_package']}.core.aspectj"
        annotation_path = context["output_root"] / "src" / "main" / "java" / Path(*annotation_package.split(".")) / "OperateLog.java"
        enum_path = context["output_root"] / "src" / "main" / "java" / Path(*enum_package.split(".")) / "OperateType.java"
        aspect_path = context["output_root"] / "src" / "main" / "java" / Path(*aspect_package.split(".")) / "OperateLogAspect.java"
        write_text(annotation_path, self._annotation_source(annotation_package, enum_package))
        write_text(enum_path, self._enum_source(enum_package))
        write_text(aspect_path, self._aspect_source(aspect_package, annotation_package))
        return {"artifact_count": 3, "artifacts": [str(annotation_path), str(enum_path), str(aspect_path)]}

    def _annotation_source(self, annotation_package: str, enum_package: str) -> str:
        return (
            f"package {annotation_package};\n\n"
            f"import {enum_package}.OperateType;\n"
            f"import java.lang.annotation.ElementType;\n"
            f"import java.lang.annotation.Retention;\n"
            f"import java.lang.annotation.RetentionPolicy;\n"
            f"import java.lang.annotation.Target;\n\n"
            f"@Target(ElementType.METHOD)\n"
            f"@Retention(RetentionPolicy.RUNTIME)\n"
            f"public @interface OperateLog {{\n"
            f"    String title();\n"
            f"    OperateType operateType();\n"
            f"}}\n"
        )

    def _enum_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"public enum OperateType {{\n"
            f"    INSERT,\n"
            f"    UPDATE,\n"
            f"    DELETE,\n"
            f"    QUERY\n"
            f"}}\n"
        )

    def _aspect_source(self, package_name: str, annotation_package: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import {annotation_package}.OperateLog;\n"
            f"import org.aspectj.lang.JoinPoint;\n"
            f"import org.aspectj.lang.annotation.AfterReturning;\n"
            f"import org.aspectj.lang.annotation.Aspect;\n"
            f"import org.slf4j.Logger;\n"
            f"import org.slf4j.LoggerFactory;\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"@Aspect\n"
            f"@Component\n"
            f"public class OperateLogAspect {{\n\n"
            f"    private static final Logger LOGGER = LoggerFactory.getLogger(OperateLogAspect.class);\n\n"
            f"    @AfterReturning(\"@annotation(operateLog)\")\n"
            f"    public void afterReturning(JoinPoint joinPoint, OperateLog operateLog) {{\n"
            f"        LOGGER.info(\"[OPERATE] method={{}} title={{}} type={{}}\", joinPoint.getSignature().toShortString(), operateLog.title(), operateLog.operateType());\n"
            f"    }}\n"
            f"}}\n"
        )
