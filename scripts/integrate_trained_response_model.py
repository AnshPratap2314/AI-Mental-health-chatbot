from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / 'app'
RE = APP / 'response_engine.py'
RETRIEVER = APP / 'response_retriever_trained.py'
MODEL = ROOT / 'models' / 'response_model'

required = [
    APP / 'response_model.py',
    MODEL / 'response_classifier.joblib',
    MODEL / 'response_index.joblib',
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit('Missing trained model files:\n' + '\n'.join(missing))

if not RE.exists():
    raise SystemExit(f'Missing {RE}')

# Keep a backup before changing the existing response engine.
backup = RE.with_suffix('.py.before_response_model')
if not backup.exists():
    shutil.copy2(RE, backup)

text = RE.read_text(encoding='utf-8')
original = text

# 1. Add an optional trained retriever import without changing existing imports.
if 'from app.response_retriever_trained import ResponseRetriever' not in text:
    marker = 'from typing import Any, Dict, Optional\n'
    if marker not in text:
        raise SystemExit('Could not find the ResponseEngine import header.')
    text = text.replace(
        marker,
        marker + '\ntry:\n    from app.response_retriever_trained import ResponseRetriever\nexcept ImportError:\n    ResponseRetriever = None\n',
        1,
    )

# 2. Initialize the retriever and source metadata in __init__.
needle = '        self.llm_engine = llm_engine\n'
insert = '''        self.llm_engine = llm_engine\n\n        # Trained 10K-response model. It improves normal-response\n        # selection only; the deterministic safety layer remains authoritative.\n        self.response_retriever = None\n        self.last_source = "deterministic"\n        self.last_model = None\n        if ResponseRetriever is not None:\n            try:\n                self.response_retriever = ResponseRetriever(top_k=3)\n                self.last_model = "mindcare-response-10k"\n            except Exception:\n                self.response_retriever = None\n'''
if 'self.response_retriever = None' not in text:
    if needle not in text:
        raise SystemExit('Could not find ResponseEngine.__init__ endpoint.')
    text = text.replace(needle, insert, 1)

# 3. Add retrieved examples to the context before the LLM/fallback path.
needle = '''        if signals.get("serious"):\n            return self._serious_response(topic)\n\n        if self.llm_engine is not None:\n'''
replacement = '''        if signals.get("serious"):\n            return self._serious_response(topic)\n\n        # Normal-risk response retrieval. Never run this path for high risk.\n        response_context = dict(context)\n        examples = self._retrieve_response_examples(\n            message=message,\n            analysis=analysis,\n            context=response_context,\n        )\n        if examples:\n            response_context["response_examples"] = examples\n            response_context["response_model_context"] = self._format_response_examples(examples)\n\n        if self.llm_engine is not None:\n            context = response_context\n'''
if 'self._retrieve_response_examples(' not in text:
    if needle not in text:
        raise SystemExit('Could not find the normal response path in ResponseEngine.generate().')
    text = text.replace(needle, replacement, 1)

# 4. Ensure fallback sees the enriched context even when LLM is disabled.
needle = '''        return self._fallback_response(\n            message,\n            analysis,\n            context\n        )\n\n    def _try_llm(\n'''
replacement = '''        context = response_context\n        return self._fallback_response(\n            message,\n            analysis,\n            context\n        )\n\n    def _try_llm(\n'''
if 'context = response_context\n        return self._fallback_response' not in text:
    if needle not in text:
        raise SystemExit('Could not find fallback call in ResponseEngine.generate().')
    text = text.replace(needle, replacement, 1)

# 5. Insert helpers immediately before _try_llm.
helper_marker = '    def _try_llm(\n'
helpers = '''    def _retrieve_response_examples(\n        self,\n        message: str,\n        analysis: Dict[str, Any],\n        context: Dict[str, Any],\n    ):\n        """Retrieve normal-risk response examples from the trained 10K model."""\n        if self.response_retriever is None:\n            return []\n\n        risk_level = str(analysis.get("risk_level", "low") or "low").lower()\n        signals = analysis.get("signals", {}) or {}\n        if risk_level == "high" or signals.get("crisis") or signals.get("self_harm"):\n            return []\n\n        state = analysis.get("state", {}) or {}\n        mood = analysis.get("mood")\n        topic = state.get("last_topic") or analysis.get("topic")\n        intent = analysis.get("intent")\n\n        try:\n            return self.response_retriever.find_examples(\n                message=message,\n                mood=mood,\n                topic=topic,\n                intent=intent,\n                risk_level=risk_level,\n                top_k=3,\n            )\n        except Exception:\n            return []\n\n    @staticmethod\n    def _format_response_examples(examples) -> str:\n        if not examples:\n            return ""\n\n        lines = [\n            "Relevant examples from the trained MindCare response dataset:",\n            "Use them only as guidance. Write a fresh response specific to the current user; do not copy them verbatim.",\n            "",\n        ]\n        for i, item in enumerate(examples, 1):\n            lines.extend([\n                f"Example {i}:",\n                f"User pattern: {item.get('message', '')}",\n                f"Response style: {item.get('response', '')}",\n                f"Intent: {item.get('intent', '')}",\n                f"Mood: {item.get('mood', '')}",\n                f"Topic: {item.get('topic', '')}",\n                f"Retrieval score: {item.get('retrieval_score', item.get('similarity', 0))}",\n                "",\n            ])\n        return "\\n".join(lines)\n\n'''
if 'def _retrieve_response_examples(' not in text:
    if helper_marker not in text:
        raise SystemExit('Could not find _try_llm() marker.')
    text = text.replace(helper_marker, helpers + helper_marker, 1)

# 6. Use the best retrieved response as a deterministic fallback only if the
# existing fallback produced the generic response. This avoids replacing
# existing specialized safety responses.
needle = '''        return self._fallback_response(\n            message,\n            analysis,\n            context\n        )\n'''
# There can be multiple occurrences; replace the first remaining fallback in generate only was handled above.
# Add a targeted replacement inside _fallback_response's final return.
old = '''        return self._neutral_response(\n            topic,\n            previous_message\n        )\n'''
new = '''        # Prefer a high-quality trained example for normal conversations\n        # when no specialized deterministic response matched.\n        trained_examples = context.get("response_examples") or []\n        if trained_examples:\n            best = trained_examples[0].get("response")\n            if isinstance(best, str) and best.strip():\n                self.last_source = "trained_response_model"\n                return best.strip()\n\n        self.last_source = "deterministic"\n        return self._neutral_response(\n            topic,\n            previous_message\n        )\n'''
if 'trained_examples = context.get("response_examples")' not in text:
    if old not in text:
        raise SystemExit('Could not find _neutral_response fallback in current response_engine.py.')
    text = text.replace(old, new, 1)

# 7. Set source when LLM returns successfully.
needle = '''            if llm_reply:\n                return llm_reply\n'''
replacement = '''            if llm_reply:\n                self.last_source = "llm"\n                return llm_reply\n'''
if 'self.last_source = "llm"' not in text:
    if needle not in text:
        raise SystemExit('Could not find LLM return path.')
    text = text.replace(needle, replacement, 1)

if text == original:
    print('No changes were necessary; integration may already be installed.')
else:
    RE.write_text(text, encoding='utf-8')
    print('Integrated trained response model into app/response_engine.py')

print(f'Backup: {backup}')
print('Next: run the verification commands from the project root.')
