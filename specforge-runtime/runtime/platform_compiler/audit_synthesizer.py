from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class AuditSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        annotation_package = f"{context['platform_package']}.core.annotation"
        aspect_package = f"{context['platform_package']}.core.aspectj"
        annotation_path = context["output_root"] / "src" / "main" / "java" / Path(*annotation_package.split(".")) / "AccessLog.java"
        aspect_path = context["output_root"] / "src" / "main" / "java" / Path(*aspect_package.split(".")) / "AccessLogAspect.java"
        write_text(annotation_path, self._annotation_source(annotation_package))
        write_text(aspect_path, self._aspect_source(aspect_package, annotation_package))
        return {"artifact_count": 2, "artifacts": [str(annotation_path), str(aspect_path)]}

    def _annotation_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import java.lang.annotation.ElementType;\n"
            f"import java.lang.annotation.Retention;\n"
            f"import java.lang.annotation.RetentionPolicy;\n"
            f"import java.lang.annotation.Target;\n\n"
            f"@Target(ElementType.METHOD)\n"
            f"@Retention(RetentionPolicy.RUNTIME)\n"
            f"public @interface AccessLog {{\n"
            f"    String value() default \"\";\n"
            f"}}\n"
        )

    def _aspect_source(self, package_name: str, annotation_package: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import {annotation_package}.AccessLog;\n"
            f"import org.aspectj.lang.JoinPoint;\n"
            f"import org.aspectj.lang.annotation.Aspect;\n"
            f"import org.aspectj.lang.annotation.Before;\n"
            f"import org.slf4j.Logger;\n"
            f"import org.slf4j.LoggerFactory;\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"@Aspect\n"
            f"@Component\n"
            f"public class AccessLogAspect {{\n\n"
            f"    private static final Logger LOGGER = LoggerFactory.getLogger(AccessLogAspect.class);\n\n"
            f"    @Before(\"@annotation(accessLog)\")\n"
            f"    public void before(JoinPoint joinPoint, AccessLog accessLog) {{\n"
            f"        LOGGER.info(\"[ACCESS] method={{}} label={{}}\", joinPoint.getSignature().toShortString(), accessLog.value());\n"
            f"    }}\n"
            f"}}\n"
        )
