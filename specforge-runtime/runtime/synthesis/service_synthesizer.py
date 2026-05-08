from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class ServiceSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        artifacts: list[str] = []
        for entity_name, entity_spec in sorted(context["schema"].get("entities", {}).items()):
            artifacts.append(self._write(context, f"{entity_name}Service", "service", self._service_interface(context, entity_name, entity_spec)))
            artifacts.append(self._write(context, f"{entity_name}ServiceImpl", "service.impl", self._service_impl(context, entity_name, entity_spec)))
            artifacts.append(self._write(context, f"{entity_name}Manager", "manager", self._manager(context, entity_name, entity_spec)))
        return {"artifact_count": len(artifacts), "artifacts": artifacts}

    def _service_interface(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        unique_methods = []
        for field in entity_spec.get("fields", []):
            if field.get("unique"):
                field_name = field["name"]
                unique_methods.append(
                    f"    boolean existsBy{field_name[:1].upper() + field_name[1:]}({context['field_type_system'].resolve(field).java_type} value, Long excludeId);"
                )
        unique_text = "\n".join(unique_methods)
        return (
            f"package {context['package_root']}.service;\n\n"
            f"import com.mybatisflex.core.service.IService;\n"
            f"import org.eu.originalkeen.core.domain.vo.PageVo;\n"
            f"import {context['package_root']}.domain.dto.Create{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.dto.Enquiry{entity_name}PageDto;\n"
            f"import {context['package_root']}.domain.dto.Update{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.entity.{entity_name};\n"
            f"import {context['package_root']}.domain.vo.{entity_name}DetailsVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}ListVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}PageVo;\n\n"
            f"import java.util.List;\n"
            f"import java.util.Set;\n\n"
            f"public interface {entity_name}Service extends IService<{entity_name}> {{\n"
            f"    void create(Create{entity_name}Dto createDto);\n\n"
            f"    void update(Update{entity_name}Dto updateDto);\n\n"
            f"    void batchDelete(Set<Long> ids);\n\n"
            f"    PageVo<{entity_name}PageVo> enquiryPage(Enquiry{entity_name}PageDto enquiryDto);\n\n"
            f"    {entity_name}DetailsVo enquiryDetails(Long id);\n\n"
            f"    List<{entity_name}ListVo> enquiryList();\n\n"
            f"    boolean existsEntity(Long id);\n\n"
            f"{unique_text}\n"
            f"}}\n"
        )

    def _service_impl(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        entity_var = entity_name[:1].lower() + entity_name[1:]
        unique_bodies = []
        for field in entity_spec.get("fields", []):
            if field.get("unique"):
                getter = f"get{field['name'][:1].upper() + field['name'][1:]}()"
                method_name = f"existsBy{field['name'][:1].upper() + field['name'][1:]}"
                unique_bodies.append(
                    f"    @Override\n"
                    f"    public boolean {method_name}({context['field_type_system'].resolve(field).java_type} value, Long excludeId) {{\n"
                    f"        return list().stream().anyMatch(entity -> Objects.equals(entity.{getter}, value) && !Objects.equals(entity.getId(), excludeId));\n"
                    f"    }}\n"
                )
        unique_text = "\n".join(unique_bodies)
        return (
            f"package {context['package_root']}.service.impl;\n\n"
            f"import com.mybatisflex.core.paginate.Page;\n"
            f"import com.mybatisflex.spring.service.impl.ServiceImpl;\n"
            f"import org.eu.originalkeen.core.domain.vo.PageVo;\n"
            f"import {context['package_root']}.domain.dto.Create{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.dto.Enquiry{entity_name}PageDto;\n"
            f"import {context['package_root']}.domain.dto.Update{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.entity.{entity_name};\n"
            f"import {context['package_root']}.domain.vo.{entity_name}DetailsVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}ListVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}PageVo;\n"
            f"import {context['package_root']}.mapper.{entity_name}Mapper;\n"
            f"import {context['package_root']}.service.{entity_name}Service;\n"
            f"import org.springframework.stereotype.Service;\n\n"
            f"import java.util.List;\n"
            f"import java.util.Objects;\n"
            f"import java.util.Set;\n"
            f"import java.util.stream.Collectors;\n\n"
            f"@Service\n"
            f"public class {entity_name}ServiceImpl extends ServiceImpl<{entity_name}Mapper, {entity_name}> implements {entity_name}Service {{\n\n"
            f"    @Override\n"
            f"    public void create(Create{entity_name}Dto createDto) {{\n"
            f"        save({entity_name}.of(createDto));\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public void update(Update{entity_name}Dto updateDto) {{\n"
            f"        updateById({entity_name}.of(updateDto));\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public void batchDelete(Set<Long> ids) {{\n"
            f"        removeByIds(ids);\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public PageVo<{entity_name}PageVo> enquiryPage(Enquiry{entity_name}PageDto enquiryDto) {{\n"
            f"        Page<{entity_name}> entityPage = page(Page.of(enquiryDto.getCurrentPage(), enquiryDto.getPageSize()));\n"
            f"        List<{entity_name}PageVo> items = entityPage.getRecords().stream()\n"
            f"                .map({entity_name}PageVo::fromEntity)\n"
            f"                .collect(Collectors.toList());\n"
            f"        return new PageVo<>(entityPage.getTotalRow(), items);\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public {entity_name}DetailsVo enquiryDetails(Long id) {{\n"
            f"        return {entity_name}DetailsVo.fromEntity(getById(id));\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public List<{entity_name}ListVo> enquiryList() {{\n"
            f"        return list().stream().map({entity_name}ListVo::fromEntity).collect(Collectors.toList());\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    public boolean existsEntity(Long id) {{\n"
            f"        return getById(id) != null;\n"
            f"    }}\n\n"
            f"{unique_text}\n"
            f"}}\n"
        )

    def _manager(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        create_validations = []
        update_validations = []
        for field in entity_spec.get("fields", []):
            if field.get("unique"):
                getter = f"get{field['name'][:1].upper() + field['name'][1:]}()"
                service_method = f"existsBy{field['name'][:1].upper() + field['name'][1:]}"
                create_validations.append(
                    f"        if ({entity_name[:1].lower() + entity_name[1:]}Service.{service_method}(dto.{getter}, null)) {{\n"
                    f'            throw new FieldValidationException("{field["name"]}", "field.{entity_name[:1].lower() + entity_name[1:]}.{field["name"]}.unique");\n'
                    f"        }}\n"
                )
                update_validations.append(
                    f"        if ({entity_name[:1].lower() + entity_name[1:]}Service.{service_method}(dto.{getter}, dto.getId())) {{\n"
                    f'            throw new FieldValidationException("{field["name"]}", "field.{entity_name[:1].lower() + entity_name[1:]}.{field["name"]}.unique");\n'
                    f"        }}\n"
                )
        create_validation_text = "".join(create_validations)
        update_validation_text = "".join(update_validations)
        return (
            f"package {context['package_root']}.manager;\n\n"
            f"import org.eu.originalkeen.core.domain.vo.PageVo;\n"
            f"import org.eu.originalkeen.core.domain.vo.ResponseVo;\n"
            f"import org.eu.originalkeen.core.exception.BusinessException;\n"
            f"import org.eu.originalkeen.core.exception.business.FieldValidationException;\n"
            f"import {context['package_root']}.domain.dto.Create{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.dto.Enquiry{entity_name}PageDto;\n"
            f"import {context['package_root']}.domain.dto.Update{entity_name}Dto;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}DetailsVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}ListVo;\n"
            f"import {context['package_root']}.domain.vo.{entity_name}PageVo;\n"
            f"import {context['package_root']}.service.{entity_name}Service;\n"
            f"import jakarta.annotation.Resource;\n"
            f"import org.springframework.stereotype.Component;\n"
            f"import org.springframework.transaction.annotation.Transactional;\n\n"
            f"import java.util.List;\n"
            f"import java.util.Objects;\n"
            f"import java.util.Set;\n\n"
            f"@Component\n"
            f"public class {entity_name}Manager {{\n\n"
            f"    @Resource\n"
            f"    private {entity_name}Service {entity_name[:1].lower() + entity_name[1:]}Service;\n\n"
            f"    @Transactional\n"
            f"    public ResponseVo<Void> create(Create{entity_name}Dto dto) {{\n"
            f"        validateCreate(dto);\n"
            f"        {entity_name[:1].lower() + entity_name[1:]}Service.create(dto);\n"
            f"        return ResponseVo.success();\n"
            f"    }}\n\n"
            f"    @Transactional\n"
            f"    public ResponseVo<Void> update(Update{entity_name}Dto dto) {{\n"
            f"        if (!{entity_name[:1].lower() + entity_name[1:]}Service.existsEntity(dto.getId())) {{\n"
            f'            throw new BusinessException("form.{entity_name[:1].lower() + entity_name[1:]}.notFound");\n'
            f"        }}\n"
            f"        validateUpdate(dto);\n"
            f"        {entity_name[:1].lower() + entity_name[1:]}Service.update(dto);\n"
            f"        return ResponseVo.success();\n"
            f"    }}\n\n"
            f"    @Transactional\n"
            f"    public ResponseVo<Void> batchDelete(Set<Long> ids) {{\n"
            f"        {entity_name[:1].lower() + entity_name[1:]}Service.batchDelete(ids);\n"
            f"        return ResponseVo.success();\n"
            f"    }}\n\n"
            f"    @Transactional(readOnly = true)\n"
            f"    public ResponseVo<PageVo<{entity_name}PageVo>> enquiryPage(Enquiry{entity_name}PageDto dto) {{\n"
            f"        return ResponseVo.success({entity_name[:1].lower() + entity_name[1:]}Service.enquiryPage(dto));\n"
            f"    }}\n\n"
            f"    @Transactional(readOnly = true)\n"
            f"    public ResponseVo<{entity_name}DetailsVo> enquiryDetails(Long id) {{\n"
            f"        {entity_name}DetailsVo detailsVo = {entity_name[:1].lower() + entity_name[1:]}Service.enquiryDetails(id);\n"
            f"        if (Objects.isNull(detailsVo)) {{\n"
            f'            throw new BusinessException("form.{entity_name[:1].lower() + entity_name[1:]}.notFound");\n'
            f"        }}\n"
            f"        return ResponseVo.success(detailsVo);\n"
            f"    }}\n\n"
            f"    @Transactional(readOnly = true)\n"
            f"    public ResponseVo<List<{entity_name}ListVo>> enquiryList() {{\n"
            f"        return ResponseVo.success({entity_name[:1].lower() + entity_name[1:]}Service.enquiryList());\n"
            f"    }}\n\n"
            f"    private void validateCreate(Create{entity_name}Dto dto) {{\n"
            f"{create_validation_text}"
            f"    }}\n\n"
            f"    private void validateUpdate(Update{entity_name}Dto dto) {{\n"
            f"{update_validation_text}"
            f"    }}\n"
            f"}}\n"
        )

    def _write(self, context: dict[str, Any], class_name: str, package_suffix: str, source: str) -> str:
        package_name = f"{context['package_root']}.{package_suffix}"
        destination = (
            context["output_root"]
            / "src"
            / "main"
            / "java"
            / Path(*package_name.split("."))
            / f"{class_name}.java"
        )
        write_text(destination, source)
        return str(destination)
