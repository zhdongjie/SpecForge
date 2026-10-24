"""Capacity is a generic spec capability; examples and packs only supply business data."""

import copy
import tempfile
import unittest
from pathlib import Path
import yaml
import test_core
from specforge.spec import load, validate, SpecError
from specforge.generate import generate
from specforge.acceptance_packs import get_pack
from specforge.acceptance_packs.support import AcceptanceClient

ROOT = Path(__file__).resolve().parents[1]


class CapacitySpecTests(unittest.TestCase):
    def setUp(self):
        self.spec = load(ROOT / "examples/book_lending.yaml")

    def invalid(self, change):
        spec = copy.deepcopy(self.spec)
        change(spec)
        with self.assertRaises(SpecError):
            validate(spec)

    def test_book_spec_and_pack_agree(self):
        get_pack("book-lending").validate(self.spec)

    def test_quantity_must_be_positive(self):
        self.invalid(lambda s: s["entities"][1]["fields"][1].update(min=0))

    def test_capacity_must_be_nonnegative(self):
        self.invalid(lambda s: s["entities"][0]["fields"][2].update(min=-1))

    def test_minimum_requires_integer_type(self):
        self.invalid(lambda s: s["entities"][0]["fields"][0].update(min=0))

    def test_boolean_is_not_an_integer_minimum(self):
        self.invalid(lambda s: s["entities"][0]["fields"][2].update(min=False))

    def test_default_cannot_be_below_minimum(self):
        self.invalid(lambda s: s["entities"][1]["fields"][1].update(default=0))

    def test_capacity_guard_is_inferred_not_a_single_item_flag(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"]["transitions"][0].update(
                exclusive=True
            )
        )

    def test_invalid_capacity_field(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"]["capacity_reference"].update(
                capacity_field="missing"
            )
        )

    def test_invalid_quantity_field(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"]["capacity_reference"].update(
                quantity_field="reason"
            )
        )

    def test_nullable_quantity_rejected(self):
        self.invalid(lambda s: s["entities"][1]["fields"][1].update(required=False))

    def test_two_resource_modes_rejected(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"].update(
                exclusive_reference={
                    "field": "book_id",
                    "active_state": "APPROVED",
                    "terminal_states": ["RETURNED", "REJECTED"],
                }
            )
        )

    def test_initial_state_cannot_consume_without_approval(self):
        self.invalid(lambda s: s["entities"][1]["workflow"].update(initial="APPROVED"))

    def test_availability_name_collision_rejected(self):
        self.invalid(
            lambda s: s["entities"][0]["fields"].append(
                {"name": "stock_available", "label": "冲突", "type": "integer"}
            )
        )

    def test_resource_cannot_mix_exclusive_and_quantity_modes(self):
        def mix(s):
            other = copy.deepcopy(s["entities"][1])
            other["name"] = "other_loan"
            w = other["workflow"]
            ref = w.pop("capacity_reference")
            w["exclusive_reference"] = {
                key: ref[key] for key in ["field", "active_state", "terminal_states"]
            }
            s["entities"].append(other)

        self.invalid(mix)

    def test_shared_capacity_consumers_are_valid(self):
        spec = copy.deepcopy(self.spec)
        other = copy.deepcopy(spec["entities"][1])
        other["name"] = "other_loan"
        spec["entities"].append(other)
        validate(spec)

    def test_book_pack_does_not_accept_device_business(self):
        with self.assertRaises(ValueError):
            get_pack("book-lending").validate(
                load(ROOT / "examples/device_borrow.yaml")
            )

    def test_client_cannot_target_nonisolated_stack(self):
        with self.assertRaises(ValueError):
            AcceptanceClient(
                "http://127.0.0.1:1234", "secret", "openclaw-preflight", Path("/tmp")
            )


class CapacityGenerationTests(unittest.TestCase):
    def test_generation_has_quantity_constraints_and_available_column(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = generate(
                ROOT / "examples/book_lending.yaml",
                test_core.CoreTests().fixture(root),
                root / "w",
            )
            sql = (
                run
                / "source/backend/src/main/resources/db/migration/SF001__business.sql"
            ).read_text()
            self.assertIn("CHECK (`quantity` >= 1)", sql)
            self.assertIn("CHECK (`stock` >= 0)", sql)
            self.assertNotIn("sf_one_active", sql)
            page = (
                run / "source/frontend/src/pages/business/sf_book/index.vue"
            ).read_text()
            self.assertIn("stock_available", page)
            self.assertIn(
                "capacity_reference",
                (
                    run / "source/frontend/src/pages/business/sf_loan/index.vue"
                ).read_text(),
            )

    def test_same_capability_generates_for_unrelated_entity_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = load(ROOT / "examples/book_lending.yaml")
            catalog, child = spec["entities"]
            catalog["name"] = "warehouse"
            child["name"] = "claim"
            catalog["fields"][2]["name"] = "units"
            catalog["page"] = {
                "list": ["code", "name", "units"],
                "form": ["code", "name", "units"],
            }
            child["fields"][0].update(name="warehouse_id", reference="warehouse")
            child["fields"][1]["name"] = "amount"
            child["page"] = {
                "list": ["warehouse_id", "amount", "reason"],
                "form": ["warehouse_id", "amount", "reason"],
            }
            child["workflow"]["capacity_reference"].update(
                field="warehouse_id", capacity_field="units", quantity_field="amount"
            )
            path = root / "spec.yaml"
            path.write_text(yaml.safe_dump(spec, allow_unicode=True))
            run = generate(path, test_core.CoreTests().fixture(root), root / "w")
            self.assertIn(
                "units_available",
                (
                    run / "source/frontend/src/pages/business/sf_warehouse/index.vue"
                ).read_text(),
            )
            self.assertIn(
                "amount",
                (
                    run
                    / "source/backend/src/main/java/com/original/business/generated/ClaimInput.java"
                ).read_text(),
            )


if __name__ == "__main__":
    unittest.main()
