from __future__ import annotations

from runtime.codegen.common import write_text


class ApplicationYamlSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        destination = context["output_root"] / "src" / "main" / "resources" / "application.yml"
        write_text(destination, self._source(context))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, context: dict[str, object]) -> str:
        return (
            "spring:\n"
            "  application:\n"
            f"    name: {context['project_name']}-generated-backend\n"
            "  datasource:\n"
            "    url: jdbc:h2:mem:specforge;MODE=MySQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE\n"
            "    driver-class-name: org.h2.Driver\n"
            "    username: sa\n"
            "    password:\n"
            "  sql:\n"
            "    init:\n"
            "      mode: never\n"
            "  data:\n"
            "    redis:\n"
            "      host: localhost\n"
            "      port: 6379\n"
            "server:\n"
            "  port: 0\n"
            "mybatis-flex:\n"
            "  mapper-locations:\n"
            "    - classpath*:mapper/**/*.xml\n"
            "specforge:\n"
            "  security:\n"
            "    jwt:\n"
            "      secret: specforge-secret-key\n"
            "      access-expire-minutes: 120\n"
            "      refresh-expire-days: 7\n"
            "  platform:\n"
            f"    source-database: {context['platform_schema']['database']['type']}\n"
        )
