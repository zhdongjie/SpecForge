from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class ControllerSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        artifacts: list[str] = []
        skipped_entities: list[dict[str, Any]] = []
        permission_class = context["permission_class"]
        for entity_name, entity_spec in sorted(context["schema"].get("entities", {}).items()):
            missing = [
                key
                for key in ["route_segment", "permission_namespace"]
                if not entity_spec.get(key)
            ]
            if missing:
                skipped_entities.append({"entity": entity_name, "missing": missing})
                continue
            route_prefix = f"{context['schema']['module']['route_base']}/{entity_spec['route_segment']}"
            source = self._source(context, entity_name, entity_spec, route_prefix, permission_class)
            package_name = f"{context['package_root']}.resource"
            destination = (
                context["output_root"]
                / "src"
                / "main"
                / "java"
                / Path(*package_name.split("."))
                / f"{entity_name}Resource.java"
            )
            write_text(destination, source)
            artifacts.append(str(destination))
        return {
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "skipped_entities": skipped_entities,
        }

    def _source(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any], route_prefix: str, permission_class: str) -> str:
        entity_var = entity_name[:1].lower() + entity_name[1:]
        plural_param = f"{entity_var}Ids"
        permission_namespace = entity_spec["permission_namespace"].replace(":", "_").replace("-", "_").upper()
        return (
            f"package {context['package_root']}.resource;\n\n"
            f"import org.eu.originalkeen.core.annotation.OperateLog;\n"
            f"import org.eu.originalkeen.core.domain.vo.PageVo;\n"
            f"import org.eu.originalkeen.core.domain.vo.ResponseVo;\n"
            f"import org.eu.originalkeen.core.enums.OperateType;\n"
            f"import {context['package_root']}.constant.{permission_class};\n"
            f"import {context['package_root']}.domain.dto.Create{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.dto.Enquiry{entity_name}PageDto;\n"
            f"import {context['package_root']}.domain.dto.Update{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}DetailsVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}ListVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}PageVo;\n"
            f"import {context['package_root']}.manager.{entity_name}Manager;\n"
            f"import jakarta.annotation.Resource;\n"
            f"import jakarta.validation.constraints.NotEmpty;\n"
            f"import org.springframework.http.ResponseEntity;\n"
            f"import org.springframework.security.access.prepost.PreAuthorize;\n"
            f"import org.springframework.validation.annotation.Validated;\n"
            f"import org.springframework.web.bind.annotation.*;\n\n"
            f"import java.util.List;\n"
            f"import java.util.Set;\n\n"
            f"@CrossOrigin\n"
            f"@Validated\n"
            f"@RestController\n"
            f'@RequestMapping("{route_prefix}")\n'
            f"public class {entity_name}Resource {{\n\n"
            f"    @Resource\n"
            f"    private {entity_name}Manager {entity_var}Manager;\n\n"
            f"    @PostMapping\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_CREATE + \"')\")\n"
            f'    @OperateLog(title = "Create {entity_name}", operateType = OperateType.INSERT)\n'
            f"    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated Create{entity_name}Dto dto) {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.create(dto));\n"
            f"    }}\n\n"
            f"    @PutMapping\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_UPDATE + \"')\")\n"
            f'    @OperateLog(title = "Update {entity_name}", operateType = OperateType.UPDATE)\n'
            f"    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated Update{entity_name}Dto dto) {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.update(dto));\n"
            f"    }}\n\n"
            f"    @DeleteMapping\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_DELETE + \"')\")\n"
            f'    @OperateLog(title = "Delete {entity_name}", operateType = OperateType.DELETE)\n'
            f"    public ResponseEntity<ResponseVo<Void>> batchDelete(@RequestParam(\"{plural_param}\") @NotEmpty Set<Long> {plural_param}) {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.batchDelete({plural_param}));\n"
            f"    }}\n\n"
            f"    @GetMapping(\"/page\")\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_PAGE + \"')\")\n"
            f"    public ResponseEntity<ResponseVo<PageVo<{entity_name}PageVo>>> enquiryPage(@Validated Enquiry{entity_name}PageDto dto) {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.enquiryPage(dto));\n"
            f"    }}\n\n"
            f"    @GetMapping(\"/{{id}}\")\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_DETAILS + \"')\")\n"
            f"    public ResponseEntity<ResponseVo<{entity_name}DetailsVo>> enquiryDetails(@PathVariable(\"id\") Long id) {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.enquiryDetails(id));\n"
            f"    }}\n\n"
            f"    @GetMapping(\"/list\")\n"
            f"    @PreAuthorize(\"hasAuthority('\" + {permission_class}.{permission_namespace}_LIST + \"')\")\n"
            f"    public ResponseEntity<ResponseVo<List<{entity_name}ListVo>>> enquiryList() {{\n"
            f"        return ResponseEntity.ok({entity_var}Manager.enquiryList());\n"
            f"    }}\n"
            f"}}\n"
        )
