import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"scripts"))
from technical_language import analyze_technical_language


def brief(text,language="en-US"):
    return {"language":language,"narrative":{"slides":[{"explanation":text}]}}


def test_empty_prose_is_not_a_perfect_score():
    result=analyze_technical_language(brief(""))
    assert result["standard_compliance_score"] is None
    assert result["warnings"][0]["code"]=="empty_technical_prose"


def test_english_rule_hints_are_traceable():
    result=analyze_technical_language(brief("The token has been revoked. However, operators utilize the old token."))
    assert {"perfect_tense_hint","passive_voice_hint","complex_word_hint"}<={w["code"] for w in result["warnings"]}
    assert all(w["path"].endswith("explanation") for w in result["warnings"])
    assert not result["official_dictionary_verified"]


def test_chinese_does_not_claim_english_word_count():
    result=analyze_technical_language(brief("如果 token 泄漏，先撤销旧 token。","zh-CN"))
    assert result["max_english_sentence_words"] is None
    assert result["scope"]=="Chinese clarity adaptation"


def test_code_names_are_exempt_and_nontechnical_is_not_scored():
    assert not analyze_technical_language(brief("Run `utilize()` to save the job."))["warnings"]
    assert not analyze_technical_language(brief("Brand story"),technical=False)["applicable"]
