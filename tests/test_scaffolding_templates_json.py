import pytest

from ellar_cli.scaffolding.scaffolding_json_validator import (
    SCAFFOLDING_TEMPLATES,
    ScaffoldingJSONValidator,
)


@pytest.mark.parametrize("root_path, json_path", SCAFFOLDING_TEMPLATES)
def test_scaffolding_template_jsons(root_path, json_path):
    validator = ScaffoldingJSONValidator(root_path, json_path)
    validator.validate_json()
