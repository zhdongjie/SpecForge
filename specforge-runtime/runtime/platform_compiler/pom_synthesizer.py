from __future__ import annotations

import re
from pathlib import Path

from runtime.codegen.common import read_text, write_text


class PomSynthesizer:
    DEFAULTS = {
        "spring_boot_version": "3.5.0",
        "java_version": "17",
        "mybatis_flex_version": "1.10.9",
    }

    def emit(self, context: dict[str, object]) -> dict[str, object]:
        versions = self._discover_versions(context.get("backend_root"))
        destination = context["output_root"] / "pom.xml"
        write_text(destination, self._source(context, versions))
        return {"artifact_count": 1, "artifacts": [str(destination)], "versions": versions}

    def _discover_versions(self, backend_root: object) -> dict[str, str]:
        versions = dict(self.DEFAULTS)
        if not isinstance(backend_root, Path):
            return versions
        pom_path = backend_root / "pom.xml"
        if not pom_path.exists():
            return versions
        source = read_text(pom_path)
        patterns = {
            "spring_boot_version": r"<version>([^<]+)</version>",
            "java_version": r"<java.version>([^<]+)</java.version>",
            "mybatis_flex_version": r"<mybatis-flex-spring-boot3-starter.version>([^<]+)</mybatis-flex-spring-boot3-starter.version>",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, source)
            if match:
                versions[key] = match.group(1).strip()
        return versions

    def _source(self, context: dict[str, object], versions: dict[str, str]) -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<project xmlns=\"http://maven.apache.org/POM/4.0.0\"\n"
            "         xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
            "         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd\">\n"
            "    <modelVersion>4.0.0</modelVersion>\n"
            "    <parent>\n"
            "        <groupId>org.springframework.boot</groupId>\n"
            "        <artifactId>spring-boot-starter-parent</artifactId>\n"
            f"        <version>{versions['spring_boot_version']}</version>\n"
            "        <relativePath/>\n"
            "    </parent>\n"
            f"    <groupId>{context['platform_package']}</groupId>\n"
            f"    <artifactId>{context['artifact_id']}</artifactId>\n"
            "    <version>0.0.1-SNAPSHOT</version>\n"
            "    <packaging>jar</packaging>\n"
            "    <properties>\n"
            f"        <java.version>{versions['java_version']}</java.version>\n"
            f"        <mybatis-flex-spring-boot3-starter.version>{versions['mybatis_flex_version']}</mybatis-flex-spring-boot3-starter.version>\n"
            "    </properties>\n"
            "    <dependencies>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-web</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-security</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-validation</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-aop</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-jdbc</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-data-redis</artifactId>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-configuration-processor</artifactId>\n"
            "            <scope>provided</scope>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>com.mybatis-flex</groupId>\n"
            "            <artifactId>mybatis-flex-spring-boot3-starter</artifactId>\n"
            "            <version>${mybatis-flex-spring-boot3-starter.version}</version>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>com.mybatis-flex</groupId>\n"
            "            <artifactId>mybatis-flex-processor</artifactId>\n"
            "            <version>${mybatis-flex-spring-boot3-starter.version}</version>\n"
            "            <scope>provided</scope>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>com.mysql</groupId>\n"
            "            <artifactId>mysql-connector-j</artifactId>\n"
            "            <scope>runtime</scope>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>com.h2database</groupId>\n"
            "            <artifactId>h2</artifactId>\n"
            "            <scope>runtime</scope>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.projectlombok</groupId>\n"
            "            <artifactId>lombok</artifactId>\n"
            "            <optional>true</optional>\n"
            "        </dependency>\n"
            "        <dependency>\n"
            "            <groupId>org.springframework.boot</groupId>\n"
            "            <artifactId>spring-boot-starter-test</artifactId>\n"
            "            <scope>test</scope>\n"
            "        </dependency>\n"
            "    </dependencies>\n"
            "    <build>\n"
            "        <plugins>\n"
            "            <plugin>\n"
            "                <groupId>org.springframework.boot</groupId>\n"
            "                <artifactId>spring-boot-maven-plugin</artifactId>\n"
            "            </plugin>\n"
            "        </plugins>\n"
            "    </build>\n"
            "</project>\n"
        )
