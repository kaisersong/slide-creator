import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/"scripts"))
from low_context import _extract_numbers, _metric_value_for_item, _primary_numbers_from_numeric_facts


@pytest.mark.parametrize("text,expected",[
    ("API p95 latency: 310 ms",["310"]),
    ("p99 450ms and p95 310ms",["450","310"]),
    ("APIv2 and model v2.30.1",[]),
    ("峰值120请求，目标99.9%，延迟下降18%",["120","99.9%","18%"]),
    ("52.5% activation, +7.1 points, 3 cohorts",["52.5%","7.1","3"]),
    ("2026年、2万、5亿、90/9/1",["2026年","2万","5亿","90","9","1"]),
])
def test_only_values_become_chart_numbers(text,expected):
    assert _extract_numbers(text)==expected


def test_p95_card_and_numeric_fact_keep_measured_latency():
    spec={"title":"Latency improved","key_point":"API p95 latency is 310 ms","supporting_facts":[],"supporting_items":[],"evidence_items":[],"numeric_facts":["API p95 latency: 310 ms"]}
    assert _metric_value_for_item("API p95 latency: 310 ms",spec)=="310"
    assert _primary_numbers_from_numeric_facts(spec)==["310"]
