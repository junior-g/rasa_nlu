from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tempfile

import pytest

from rasa_nlu import config, utils
from rasa_nlu.registry import registered_pipeline_templates
from rasa_nlu.components import ComponentBuilder
from tests.conftest import CONFIG_DEFAULTS_PATH
from tests.utilities import write_file_config

defaults = utils.read_yaml_file(CONFIG_DEFAULTS_PATH)


def test_default_config(default_config):
    assert default_config.as_dict() == defaults


def test_blank_config():
    file_config = {}
    f = write_file_config(file_config)
    final_config = config.load(f.name)
    assert final_config.as_dict() == defaults


def test_invalid_config_json():
    file_config = """pipeline: [spacy_sklearn"""  # invalid yaml
    with tempfile.NamedTemporaryFile("w+",
                                     suffix="_tmp_config_file.json") as f:
        f.write(file_config)
        f.flush()
        with pytest.raises(config.InvalidConfigError):
            config.load(f.name)


def test_invalid_pipeline_template():
    args = {"pipeline": "my_made_up_name"}
    f = write_file_config(args)
    with pytest.raises(config.InvalidConfigError) as execinfo:
        config.load(f.name)
    assert "unknown pipeline template" in str(execinfo.value)


def test_pipeline_looksup_registry():
    pipeline_template = list(registered_pipeline_templates)[0]
    args = {"pipeline": pipeline_template}
    f = write_file_config(args)
    final_config = config.load(f.name)
    components = [c.get("name") for c in final_config.pipeline]
    assert components == registered_pipeline_templates[pipeline_template]


def test_default_config_file():
    final_config = config.RasaNLUModelConfig()
    assert len(final_config) > 1


def test_set_attr_on_component(default_config):
    cfg = config.load("sample_configs/config_spacy.yml")
    cfg.set_component_attr("intent_classifier_sklearn", C=324)

    expected = {"C": 324, "name": "intent_classifier_sklearn"}

    assert cfg.for_component("intent_classifier_sklearn") == expected
    assert cfg.for_component("tokenizer_spacy") == {"name": "tokenizer_spacy"}


def test_override_defaults_tensorflow_embedding_pipeline():
    cfg = config.load("data/test/config_embedding_test.yml")
    builder = ComponentBuilder()

    name1 = "intent_featurizer_count_vectors"

    component1 = builder.create_component(name1, cfg)
    assert component1.max_ngram == 3

    name2 = "intent_classifier_tensorflow_embedding"
    component2 = builder.create_component(name2, cfg)
    assert component2.epochs == 10
