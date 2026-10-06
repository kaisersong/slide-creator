"""Limited writing-rule diagnostics. Never claims full STE dictionary compliance."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

COMPLEX = re.compile(r"\b(utilize|leverage|commence|terminate|obtain|however|additionally)\b|\b(prior to|in order to)\b", re.I)
PASSIVE = re.compile(r"\b(is|are|was|were|be|been)\s+(\w+ed|sent|written|given|shown|built)\b", re.I)
PERFECT = re.compile(r"\b(has|have|had)\s+(?:been\s+)?(\w+ed|sent|written|given|shown|built)\b", re.I)


def analyze_technical_language(brief, technical=True):
    language = brief.get("language", "")
    report = {"applicable":technical,"language":language,"scope":"English writing-rule hints" if language.startswith("en") else "Chinese clarity adaptation",
              "official_dictionary_verified":False,"standard_compliance_score":None,"warnings":[],"review_required":["approved word meaning and part of speech","terminology consistency","one topic per sentence","actor and condition clarity","numeric units and source meaning"]}
    if not technical:
        return report
    fields=[]
    for i,slide in enumerate(brief.get("narrative",{}).get("slides",[]),1):
        for key in ("title","key_point","claim","explanation"):
            if isinstance(slide.get(key),str):
                fields.append((f"slides[{i}].{key}",slide[key]))
        for key in ("supporting_facts","numeric_facts"):
            fields.extend((f"slides[{i}].{key}[{j}]",text) for j,text in enumerate(slide.get(key,[])) if isinstance(text,str))
    nonempty=[(path,text) for path,text in fields if text.strip()]
    if not nonempty:
        report["warnings"].append({"code":"empty_technical_prose","path":"narrative.slides"})
    lengths=[]
    for path,text in nonempty:
        # Literal commands/code are technical names, not controlled prose.
        prose=re.sub(r"```[\s\S]*?```|`[^`]*`", "", text)
        if language.startswith("en"):
            for sentence in re.split(r"(?<=[.!?])\s+",prose):
                count=len(re.findall(r"[A-Za-z0-9]+(?:[-_'.][A-Za-z0-9]+)*",sentence))
                lengths.append(count)
                imperative=bool(re.match(r"\s*(run|open|close|set|save|remove|use|disable|enable|revoke|check)\b",sentence,re.I))
                limit=20 if imperative else 25
                if count>limit:
                    report["warnings"].append({"code":"sentence_too_long","path":path,"words":count,"limit":limit})
            for code,pattern in (("complex_word_hint",COMPLEX),("passive_voice_hint",PASSIVE),("perfect_tense_hint",PERFECT)):
                for match in pattern.finditer(prose):
                    report["warnings"].append({"code":code,"path":path,"text":match.group(0)})
        if len(re.findall(r"[.!?。！？](?:\s|$)",prose))>6:
            report["warnings"].append({"code":"paragraph_too_many_sentences","path":path})
    report.update(prose_field_count=len(nonempty),max_english_sentence_words=max(lengths,default=None))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief",type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze_technical_language(json.loads(args.brief.read_text())),ensure_ascii=False,indent=2))


if __name__=="__main__":main()
