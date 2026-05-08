from __future__ import annotations

from typing import Any


class PaginationLowering:
    def lower(self, expanded: dict[str, Any], entities: dict[str, dict[str, Any]]) -> dict[str, Any]:
        paginated_entities = []
        sortable_fields: dict[str, list[str]] = {}
        for aggregate, aggregate_info in sorted(expanded["aggregates"].items(), key=lambda item: item[0]):
            if "page" not in aggregate_info["patterns"]:
                continue
            paginated_entities.append(aggregate)
            entity_fields = entities.get(aggregate, {}).get("fields", [])
            sortable_fields[aggregate] = [
                field["name"]
                for field in entity_fields
                if field["name"] not in {"id", "remark"} and field.get("type") in {"string", "integer", "long", "enum"}
            ]
        return {
            "pagination_contract": {
                "page_query_base": "EnquiryPageDto",
                "page_number_field": "currentPage",
                "page_size_field": "pageSize",
                "page_wrapper": "PageVo",
                "paginated_entities": paginated_entities,
                "sortable_fields": sortable_fields,
            }
        }
