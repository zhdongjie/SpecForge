from __future__ import annotations

from typing import Any


class DtoContractLowering:
    def lower(self, expanded: dict[str, Any]) -> dict[str, Any]:
        contracts: dict[str, dict[str, Any]] = {}
        for aggregate, aggregate_info in sorted(expanded["aggregates"].items(), key=lambda item: item[0]):
            patterns = set(aggregate_info["patterns"])
            contracts[aggregate] = {
                "create_dto": f"Create{aggregate}Dto" if "create" in patterns else None,
                "update_dto": f"Update{aggregate}Dto" if "update" in patterns else None,
                "query_dto": f"Enquiry{aggregate}PageDto" if "page" in patterns else None,
                "page_vo": f"{aggregate}PageVo" if "page" in patterns else None,
                "list_vo": f"{aggregate}ListVo" if "list" in patterns else None,
                "details_vo": f"{aggregate}DetailsVo" if "details" in patterns else None,
                "validation_dtos": sorted(
                    capability["input_dto"]
                    for capability in aggregate_info["capabilities"]
                    if capability["deterministic_pattern"] == "uniqueness-check"
                ),
            }
        return {"dto_contracts": contracts}
