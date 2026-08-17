"""Read-only diagnostic for the ITR main-table Checkbox `加入ITR待办`.

Uses the project's normal config/OAuth path through feishu_api.  It never
creates, updates, or deletes Feishu records or fields, and it prints no case
values other than the Checkbox's safe boolean state/type.
"""
import sys

import feishu_api


FIELD_NAME = "加入ITR待办"
FIELD_TYPE_NAMES = {7: "Checkbox"}


def _value_shape(value):
    if value is None:
        return "None"
    if isinstance(value, bool):
        return f"bool / {value}"
    if isinstance(value, int):
        return f"int / {value}"
    if isinstance(value, str):
        safe_value = value if value.casefold() in {"true", "false"} else "<non-boolean string>"
        return f"str / {safe_value}"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return f"dict / keys: {', '.join(sorted(map(str, value.keys())))}"
    return type(value).__name__


def _fail(message):
    print("===== ITR TODO CHECKBOX DIAGNOSTIC =====")
    print(message)
    print("Safe to implement: NO")
    print("===== END =====")
    return 1


def main():
    try:
        metadata = feishu_api.get_table_fields_metadata()
    except Exception as exc:
        return _fail("Network request failed." if feishu_api.is_network_error(exc) else "Authentication failed.")

    field = next((item for item in metadata if item.get("field_name") == FIELD_NAME), None)
    if not field:
        return _fail(f"Field not found: {FIELD_NAME}")

    field_type = field.get("type")
    type_name = FIELD_TYPE_NAMES.get(field_type, "Unknown")
    property_keys = sorted((field.get("property") or {}).keys())
    try:
        records = feishu_api.get_records_sample([FIELD_NAME], limit=10)
    except Exception as exc:
        return _fail("Network request failed." if feishu_api.is_network_error(exc) else "Authentication failed.")

    observed = []
    for record in records:
        shape = _value_shape((record.get("fields") or {}).get(FIELD_NAME))
        if shape not in observed:
            observed.append(shape)

    inferred_write = "INFERRED: bool (True/False)" if field_type == 7 else "UNKNOWN"
    print("===== ITR TODO CHECKBOX DIAGNOSTIC =====")
    print(f"Field: {FIELD_NAME}")
    print("Field found: YES")
    print(f"Field type: {field_type} / {type_name}")
    print("Checkbox metadata keys: " + (", ".join(property_keys) if property_keys else "<none>"))
    print("Read shape:")
    for shape in observed or ["No sampled value"]:
        print(f"- {shape}")
    print(f"Write shape: {inferred_write}")
    print("Safe to implement: YES" if field_type == 7 and observed else "Safe to implement: NO")
    print("===== END =====")
    return 0 if field_type == 7 and observed else 1


if __name__ == "__main__":
    sys.exit(main())
