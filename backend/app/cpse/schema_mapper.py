"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Schema Mapper & Column Auto-Detector
Description: Dynamically maps disparate CPSE export columns into the internal normalized schema.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from backend.app.cpse.models import CPSE_SCHEMA_FIELDS, REQUIRED_FIELDS

# Comprehensive dictionary of real enterprise ERP/SAP aliases for material fields
COLUMN_ALIASES: Dict[str, List[str]] = {
    "material_code": [
        "material_code", "mat_code", "matcode", "item_no", "item_code", "item_num",
        "material_id", "mat_id", "matnr", "part_no", "part_number", "partno",
        "code", "item_id", "product_code", "article_no", "catalog_no"
    ],
    "description": [
        "description", "mat_desc", "material_description", "item_desc",
        "item_description", "long_description", "short_description", "maktx",
        "desc", "product_description", "item_name", "material_name", "title"
    ],
    "specification": [
        "specification", "tech_spec", "technical_specification", "specs", "spec",
        "item_specification", "standard_spec", "technical_data", "details"
    ],
    "material_type": [
        "material_type", "mat_type", "type", "item_type", "commodity_type", "mtart"
    ],
    "material_grade": [
        "material_grade", "grade", "mat_grade", "steel_grade", "metallurgical_grade",
        "spec_grade", "class_grade"
    ],
    "dimensions": [
        "dimensions", "dimension", "size", "dim", "sizes", "measurements", "rating"
    ],
    "unit_of_measure": [
        "unit_of_measure", "uom", "base_uom", "unit", "meins", "units", "uom_code",
        "order_unit", "measuring_unit"
    ],
    "manufacturer": [
        "manufacturer", "mfg", "mfg_name", "make", "brand", "vendor", "vendor_name",
        "supplier", "oem"
    ],
    "part_number": [
        "part_number", "part_no", "model_no", "model_number", "part_num", "oem_part_no",
        "mfr_part_no", "cat_no"
    ],
    "category": [
        "category", "material_group", "mat_group", "group", "matkl", "item_group",
        "commodity_code", "hsn_code", "sac_code"
    ],
}


def normalize_header(col_name: str) -> str:
    """
    Normalizes a column header string for robust matching:
    converts to lower case, replaces dashes/spaces with underscores, and trims.
    """
    if not col_name:
        return ""
    norm = col_name.strip().lower()
    norm = re.sub(r"[\s\-\.]+", "_", norm)
    norm = re.sub(r"_+", "_", norm)
    return norm


class SchemaMapper:
    """
    Intelligently maps column headers from arbitrary CPSE formats (SAP, Oracle, Excel)
    to the standardized national CPSE material schema.
    """

    def __init__(self, alias_dict: Optional[Dict[str, List[str]]] = None):
        self.aliases = alias_dict or COLUMN_ALIASES

    def detect_mappings(
        self,
        raw_columns: List[str],
        user_overrides: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes raw columns from an uploaded file and produces a mapping plan:
        - Maps each source column to a target schema field (or marks unmapped)
        - Applies user overrides if provided
        - Identifies missing required fields
        """
        user_overrides = user_overrides or {}
        mappings: Dict[str, str] = {}
        assigned_targets: Set[str] = set()

        # 1. Apply user overrides first
        for raw_col, target in user_overrides.items():
            if raw_col in raw_columns and target in CPSE_SCHEMA_FIELDS:
                mappings[raw_col] = target
                assigned_targets.add(target)

        # 2. Automated rule-based matching for remaining columns
        for raw_col in raw_columns:
            if raw_col in mappings:
                continue

            norm_col = normalize_header(raw_col)

            # A) Exact match against schema field
            if norm_col in CPSE_SCHEMA_FIELDS and norm_col not in assigned_targets:
                mappings[raw_col] = norm_col
                assigned_targets.add(norm_col)
                continue

            # B) Alias lookup
            matched_target = None
            for target_field, alias_list in self.aliases.items():
                if target_field in assigned_targets:
                    continue
                # Check exact alias match
                if norm_col in alias_list:
                    matched_target = target_field
                    break

            # C) Substring/partial match if no exact alias found
            if not matched_target:
                for target_field, alias_list in self.aliases.items():
                    if target_field in assigned_targets:
                        continue
                    for alias in alias_list:
                        if (alias in norm_col or norm_col in alias) and len(alias) >= 3:
                            matched_target = target_field
                            break
                    if matched_target:
                        break

            if matched_target:
                mappings[raw_col] = matched_target
                assigned_targets.add(matched_target)

        # 3. Identify unmapped and missing required fields
        unmapped = [col for col in raw_columns if col not in mappings]
        mapped_targets = set(mappings.values())
        missing_required = [req for req in REQUIRED_FIELDS if req not in mapped_targets]

        is_valid = len(missing_required) == 0
        if is_valid:
            validation_message = "All required fields (material_code, description) successfully mapped."
        else:
            validation_message = f"Missing required fields: {', '.join(missing_required)}."

        return {
            "detected_columns": raw_columns,
            "suggested_mappings": mappings,
            "unmapped_columns": unmapped,
            "missing_required_fields": missing_required,
            "is_valid": is_valid,
            "validation_message": validation_message,
        }


# Singleton mapper instance
_mapper_instance: Optional[SchemaMapper] = None


def get_schema_mapper() -> SchemaMapper:
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = SchemaMapper()
    return _mapper_instance


if __name__ == "__main__":
    mapper = get_schema_mapper()

    print("--- Test CPSE A (ONGC Style) ---")
    cols_a = ["MAT_CODE", "MAT_DESC", "UOM", "TECH_SPEC", "GRADE", "MFG"]
    plan_a = mapper.detect_mappings(cols_a)
    print("Mappings:", plan_a["suggested_mappings"])
    print("Unmapped:", plan_a["unmapped_columns"])
    print("Valid:", plan_a["is_valid"])

    print("\n--- Test CPSE B (BHEL Style) ---")
    cols_b = ["ITEM_NO", "LONG_DESCRIPTION", "BASE_UOM", "SPECIFICATION", "STEEL_GRADE"]
    plan_b = mapper.detect_mappings(cols_b)
    print("Mappings:", plan_b["suggested_mappings"])
    print("Unmapped:", plan_b["unmapped_columns"])
    print("Valid:", plan_b["is_valid"])
