import re
from typing import Any, Dict, List, Optional

from app.context_state import ContextState

try:
    from app.crisis_manager import CrisisManager
except ImportError:
    CrisisManager = None

try:
    from app.safety_resources import SafetyResources
except ImportError:
    SafetyResources = None

try:
    from app.safety_audit import SafetyAudit
except ImportError:
    SafetyAudit = None

try:
    from app.user_profile import UserProfile
except ImportError:
    UserProfile = None

try:
    from app.personalization_engine import PersonalizationEngine
except ImportError:
    PersonalizationEngine = None

try:
    from app.privacy_manager import PrivacyManager
except ImportError:
    PrivacyManager = None

try:
    from app.security import SecurityManager
except ImportError:
    SecurityManager = None

try:
    from app.response_engine import ResponseEngine
except ImportError:
    ResponseEngine = None


class BehaviorEngine:

    def __init__(
        self,
        user_name="friend",
        max_memory=10,
        response_engine=None,
        llm_engine=None,
        session_id=None
    ):
        self.user_name = user_name or "friend"
        self.max_memory = max(1, int(max_memory))
        self.memory: List[Dict[str, Any]] = []
        self.turn_count = 0
        self.session_id = session_id

        self.context_state = ContextState()

        self.crisis_manager = (
            CrisisManager()
            if CrisisManager is not None
            else None
        )

        self.safety_resources = (
            SafetyResources()
            if SafetyResources is not None
            else None
        )

        self.safety_audit = (
            SafetyAudit()
            if SafetyAudit is not None
            else None
        )

        self.user_profile = (
            UserProfile(self.user_name)
            if UserProfile is not None
            else None
        )

        self.personalization_engine = (
            PersonalizationEngine()
            if PersonalizationEngine is not None
            else None
        )

        self.privacy_manager = (
            PrivacyManager()
            if PrivacyManager is not None
            else None
        )

        self.security_manager = (
            SecurityManager()
            if SecurityManager is not None
            else None
        )

        if response_engine is not None:
            self.response_engine = response_engine
        elif ResponseEngine is not None:
            try:
                self.response_engine = ResponseEngine(
                    user_name=self.user_name,
                    llm_engine=llm_engine
                )
            except TypeError:
                try:
                    self.response_engine = ResponseEngine(
                        user_name=self.user_name
                    )
                except Exception:
                    self.response_engine = None
        else:
            self.response_engine = None

        self.llm_engine = llm_engine

    def generate_reply(self, message: str) -> Dict[str, Any]:
        message = self._clean_message(message)

        if self.security_manager is not None:
            try:
                message = self.security_manager.sanitize_message(message)
            except Exception:
                pass

            try:
                if not self.security_manager.validate_message(message):
                    return self._invalid_message_result()
            except Exception:
                pass

        if not message:
            return self._invalid_message_result()

        context = self._build_context()

        context_risk_boost = self._calculate_context_risk_boost(
            context
        )

        analysis = self._analyze_message(
            message,
            context,
            context_risk_boost
        )

        crisis_result = self._evaluate_crisis(analysis)

        analysis["crisis"] = crisis_result

        self._update_state(analysis)

        analysis["state"] = self.get_context_state()

        self._store_message(message)

        reply = self._generate_response(
            message,
            analysis,
            context
        )

        if self.personalization_engine is not None:
            try:
                reply = self.personalization_engine.personalize(
                    reply,
                    self._get_profile(),
                    analysis["state"].get("last_topic")
                )
            except Exception:
                pass

        result = {
            "reply": reply,
            "response": reply,
            "mode": analysis["mode"],
            "analysis": analysis,
            "state": analysis["state"]
        }

        if analysis["risk_level"] == "high":
            result["safety"] = self._build_safety_response(
                analysis["risk_level"]
            )

        if crisis_result:
            result["crisis"] = crisis_result

        if self.safety_resources is not None:
            if crisis_result.get("immediate_guidance", False):
                try:
                    result["resources"] = (
                        self.safety_resources.build_crisis_guidance()
                    )
                except Exception:
                    pass

        if self.user_profile is not None:
            result["profile"] = self._get_profile()

        return result

    def _invalid_message_result(self):
        state = self.get_context_state()

        analysis = {
            "message": "",
            "risk_level": "low",
            "risk_score": 0.0,
            "context_risk_boost": 0.0,
            "mood": "neutral",
            "mode": "normal",
            "topic": state.get("last_topic"),
            "topic_detected": False,
            "signals": {},
            "context": self._build_context(),
            "state": state
        }

        reply = (
            "Please enter a message so I can listen and respond."
        )

        return {
            "reply": reply,
            "response": reply,
            "mode": "normal",
            "analysis": analysis,
            "state": state
        }

    def _clean_message(self, message: str) -> str:
        if message is None:
            return ""

        message = str(message).strip()

        return re.sub(
            r"\s+",
            " ",
            message
        )

    def _normalize(self, text: str) -> str:
        text = str(text or "").lower().strip()

        text = re.sub(
            r"[^\w\s']",
            " ",
            text
        )

        return re.sub(
            r"\s+",
            " ",
            text
        )

    def _analyze_message(
        self,
        message: str,
        context: Dict[str, Any],
        context_risk_boost: float
    ) -> Dict[str, Any]:

        text = self._normalize(message)

        signals = self._detect_signals(text)

        risk_score = self._calculate_risk_score(
            signals,
            context_risk_boost
        )

        risk_level = self._determine_risk_level(
            risk_score,
            signals
        )

        mood = self._detect_mood(
            text,
            signals
        )

        detected_topic = self._detect_topic(text)

        previous_topic = self.context_state.last_topic

        topic = detected_topic

        if topic is None:
            topic = previous_topic

        is_follow_up = detected_topic is None and bool(
            previous_topic
        )

        mode = self._determine_mode(
            risk_level,
            mood,
            signals
        )

        previous_mood = self.context_state.current_mood or "unknown"
        mood_intensity = self._estimate_mood_intensity(
            mood=mood,
            signals=signals,
            risk_score=risk_score,
        )

        return {
            "message": message,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "context_risk_boost": context_risk_boost,
            "mood": mood,
            "mood_intensity": mood_intensity,
            "mood_previous": previous_mood,
            "mood_changed": previous_mood not in {"unknown", mood},
            "mode": mode,
            "topic": topic,
            "detected_topic": detected_topic,
            "topic_detected": detected_topic is not None,
            "is_follow_up": is_follow_up,
            "signals": signals,
            "context": context
        }

    def _estimate_mood_intensity(
        self,
        mood: str,
        signals: Dict[str, bool],
        risk_score: float,
    ) -> str:
        """Estimate emotional intensity for response style, not diagnosis."""
        strong = bool(
            signals.get("crisis")
            or signals.get("self_harm")
            or signals.get("plan")
            or signals.get("hopelessness")
        )
        moderate = bool(
            signals.get("serious")
            or signals.get("worthlessness")
            or signals.get("anxiety")
            or signals.get("sad")
            or risk_score >= 0.20
        )

        if strong:
            return "high"
        if moderate:
            return "moderate"
        if mood == "positive":
            return "positive"
        return "low"

    def _detect_signals(self, text: str) -> Dict[str, bool]:
        """Detect safety-relevant signals conservatively.

        Important: a negation anywhere in a sentence must not erase an
        explicit suicidal/self-harm statement. For example, "I am suicidal
        but I won't act" still contains suicidal ideation and should receive
        a safety-oriented response.
        """
        normalized = self._normalize(text)

        contextual_suicide = self._contains_any(
            normalized,
            [
                "movie about suicide",
                "film about suicide",
                "watched a movie about suicide",
                "watched a film about suicide",
                "read a news article about suicide",
                "news article about suicide",
                "news about suicide",
                "article about suicide",
                "story about suicide",
                "documentary about suicide",
                "documentary on suicide",
            ],
        )

        # Explicit ideation / self-harm language. These are intentionally
        # broader than the old keyword list so passive and conversational
        # formulations are not missed.
        crisis_patterns = [
            "suicidal",
            "suicidal thoughts",
            "thinking about suicide",
            "thinking of suicide",
            "thinking about killing myself",
            "thinking of killing myself",
            "thinking about ending my life",
            "thinking of ending my life",
            "kill myself",
            "killing myself",
            "end my life",
            "ending my life",
            "take my own life",
            "taking my own life",
            "want to die",
            "wanna die",
            "wish i was dead",
            "wish i were dead",
            "wish i could die",
            "better off dead",
            "no reason to live",
            "no reason for me to live",
            "no point in living",
            "life is not worth living",
            "life isn't worth living",
            "don't want to live anymore",
            "do not want to live anymore",
            "don't want to be alive",
            "do not want to be alive",
            "can't go on living",
            "cannot go on living",
        ]

        self_harm_patterns = [
            "hurt myself",
            "harm myself",
            "self harm",
            "self-harm",
            "cut myself",
            "cutting myself",
            "injure myself",
            "injuring myself",
            "burn myself",
            "hit myself",
        ]

        crisis = self._contains_any(normalized, crisis_patterns)
        self_harm = self._contains_any(normalized, self_harm_patterns)

        serious = self._contains_any(
            normalized,
            [
                "hopeless",
                "worthless",
                "useless",
                "helpless",
                "can't handle this",
                "cannot handle this",
                "can't cope",
                "cannot cope",
                "falling apart",
                "feel trapped",
                "nothing is working",
                "everything is falling apart",
                "no way out",
            ],
        )

        sad = self._contains_any(
            normalized,
            [
                "sad",
                "sadness",
                "lonely",
                "loneliness",
                "unhappy",
                "depressed",
                "depressing",
                "crying",
                "cry",
                "hurt",
                "broken",
                "empty",
                "down",
                "miserable",
                "hopeless",
                "worthless",
                "useless",
            ],
        )

        anxiety = self._contains_any(
            normalized,
            [
                "anxious",
                "anxiety",
                "panic",
                "panicking",
                "worried",
                "worry",
                "nervous",
                "overthinking",
                "stress",
                "stressed",
                "stressing",
                "overwhelmed",
            ],
        )

        hopelessness = self._contains_any(
            normalized,
            [
                "hopeless",
                "no hope",
                "nothing will get better",
                "nothing matters",
                "no point",
                "pointless",
                "can't go on",
                "cannot go on",
                "no way out",
            ],
        )

        worthlessness = self._contains_any(
            normalized,
            [
                "worthless",
                "useless",
                "good for nothing",
                "i am a failure",
                "i'm a failure",
                "nobody needs me",
            ],
        )

        # Intent is stronger when it is explicitly connected to a harmful
        # action. Generic help-seeking phrases should not be treated as
        # suicidal intent.
        intent = self._contains_any(
            normalized,
            [
                "i might do it",
                "i may do it",
                "i could do it",
                "i think i will",
                "i'm going to do it",
                "i am going to do it",
                "i want to do it",
                "i can't stop myself",
                "i cannot stop myself",
                "i don't think i can stop",
                "i do not think i can stop",
                "i've decided to die",
                "i have decided to die",
                "i've decided to kill myself",
                "i have decided to kill myself",
                "i'm going to kill myself",
                "i am going to kill myself",
                "i'm going to hurt myself",
                "i am going to hurt myself",
                "i plan to kill myself",
                "i have a plan to kill myself",
                "i plan to hurt myself",
                "i have a plan to hurt myself",
                "suicide plan",
                "plan to end my life",
                "plan to die",
            ],
        )

        help_seeking = self._contains_any(
            normalized,
            [
                "i need help",
                "help me",
                "what should i do",
                "what can i do",
                "i don't know what to do",
                "i do not know what to do",
                "i need someone",
                "i need support",
            ],
        )

        plan = self._contains_any(
            normalized,
            [
                "suicide plan",
                "plan to kill myself",
                "plan to hurt myself",
                "plan to end my life",
                "plan to die",
                "have a plan to kill myself",
                "have a plan to hurt myself",
                "made a plan to kill myself",
                "made a plan to hurt myself",
            ],
        )

        protective = self._contains_any(
            normalized,
            [
                "i want to live",
                "i want to get better",
                "i want help",
                "i'm safe",
                "i am safe",
                "i don't want to hurt myself",
                "i do not want to hurt myself",
                "i don't want to die",
                "i do not want to die",
            ],
        )

        temporal = self._contains_any(
            normalized,
            [
                "right now",
                "tonight",
                "today",
                "currently",
                "at this moment",
                "immediately",
                "soon",
                "later tonight",
                "tomorrow",
            ],
        )

        context_reference = self._contains_any(
            normalized,
            [
                "tell me more",
                "explain more",
                "what do you mean",
                "continue",
                "go on",
                "what else",
                "more about that",
                "and then",
                "what should i do",
                "what can i do",
            ],
        )

        # Only suppress an explicit safety signal when the harmful statement
        # itself is clearly negated. Do NOT use a global negation switch.
        negated_crisis = self._is_negated_crisis(normalized)
        negated_self_harm = self._is_negated_self_harm(normalized)
        negated = negated_crisis or negated_self_harm

        if contextual_suicide and not crisis and not self_harm:
            crisis = False
            self_harm = False

        if negated_crisis:
            explicit_positive_signal = self._contains_any(
                normalized,
                [
                    "suicidal",
                    "suicidal thoughts",
                    "thinking about suicide",
                    "thinking of suicide",
                    "thinking about killing myself",
                    "thinking of killing myself",
                    "thinking about ending my life",
                    "thinking of ending my life",
                    "end my life",
                    "ending my life",
                    "want to die",
                    "no reason to live",
                    "no reason for me to live",
                    "life isn't worth living",
                    "life is not worth living",
                ],
            )
            # The positive phrase "want to die" is itself present inside
            # "don't want to die", so exact protective statements need an
            # explicit exception. Mixed statements such as "I'm suicidal
            # but I don't want to die" remain safety-significant.
            only_protective = normalized in {
                "i don't want to die",
                "i do not want to die",
                "i don't want to hurt myself",
                "i do not want to hurt myself",
                "i'm not suicidal",
                "i am not suicidal",
                "not suicidal",
            }
            if only_protective or not explicit_positive_signal:
                crisis = False

        if negated_self_harm:
            self_harm = False

        return {
            "crisis": bool(crisis),
            "serious": bool(serious),
            "sad": bool(sad),
            "anxiety": bool(anxiety),
            "hopelessness": bool(hopelessness),
            "worthlessness": bool(worthlessness),
            "self_harm": bool(self_harm),
            "intent": bool(intent),
            "help_seeking": bool(help_seeking),
            "plan": bool(plan),
            "temporal": bool(temporal),
            "protective": bool(protective),
            "negated": bool(negated),
            "negated_crisis": bool(negated_crisis),
            "negated_self_harm": bool(negated_self_harm),
            "context_reference": bool(context_reference),
            "contextual_suicide": bool(contextual_suicide),
        }

    def _detect_topic(self, text: str) -> Optional[str]:
        topic_patterns = {
            "college": [
                "college",
                "exam",
                "exams",
                "study",
                "studies",
                "semester",
                "assignment",
                "university",
                "class",
                "professor",
                "course",
                "marks",
                "grades"
            ],
            "work": [
                "internship",
                "interview",
                "job",
                "career",
                "work",
                "office",
                "company",
                "resume",
                "cv",
                "recruiter",
                "placement"
            ],
            "future": [
                "future",
                "tomorrow",
                "next year",
                "life ahead",
                "what will happen",
                "career path"
            ],
            "relationships": [
                "relationship",
                "girlfriend",
                "boyfriend",
                "partner",
                "breakup",
                "dating",
                "love"
            ],
            "family": [
                "family",
                "mother",
                "father",
                "mom",
                "dad",
                "parents",
                "brother",
                "sister"
            ],
            "health": [
                "health",
                "doctor",
                "illness",
                "sick",
                "pain",
                "sleep"
            ],
            "finance": [
                "money",
                "financial",
                "finance",
                "debt",
                "salary",
                "rent",
                "expenses"
            ],
            "friends": [
                "friend",
                "friends",
                "friendship",
                "best friend"
            ],
            "social": [
                "social",
                "people",
                "community",
                "isolated",
                "isolation"
            ]
        }

        scores = {}

        for topic, patterns in topic_patterns.items():
            score = 0

            for pattern in patterns:
                if pattern in text:
                    score += 1

            if score:
                scores[topic] = score

        if not scores:
            return None

        return max(
            scores,
            key=scores.get
        )

    def _detect_negation(self, text: str) -> bool:
        return self._contains_any(
            text,
            [
                "not suicidal",
                "i am not suicidal",
                "i'm not suicidal",
                "not suicide",
                "don't want to die",
                "do not want to die",
                "i don't want to die",
                "i do not want to die",
                "not going to die",
                "not planning suicide",
                "not self harm",
                "not self-harm",
                "don't want to hurt myself",
                "do not want to hurt myself",
                "i don't want to hurt myself",
                "i do not want to hurt myself"
            ]
        )

    def _is_negated_crisis(self, text: str) -> bool:
        return self._contains_any(
            text,
            [
                "not suicidal",
                "i am not suicidal",
                "i'm not suicidal",
                "don't want to die",
                "do not want to die",
                "i don't want to die",
                "i do not want to die",
                "not planning suicide"
            ]
        )

    def _is_negated_self_harm(self, text: str) -> bool:
        return self._contains_any(
            text,
            [
                "don't want to hurt myself",
                "do not want to hurt myself",
                "i don't want to hurt myself",
                "i do not want to hurt myself",
                "not self harm",
                "not self-harm"
            ]
        )

    def _calculate_risk_score(
        self,
        signals: Dict[str, bool],
        context_risk_boost: float
    ) -> float:

        score = 0.0

        if signals["crisis"]:
            score += 0.70

        if signals["self_harm"]:
            score += 0.60

        if signals["intent"]:
            score += 0.35

        if signals.get("plan"):
            score += 0.25

        if signals["hopelessness"]:
            score += 0.30
        elif signals["worthlessness"]:
            score += 0.25
        elif signals["serious"]:
            score += 0.25

        if signals["sad"] and not (
            signals["hopelessness"]
            or signals["worthlessness"]
            or signals["serious"]
        ):
            score += 0.05

        if signals["anxiety"]:
            score += 0.08

        if signals["temporal"] and signals["crisis"]:
            score += 0.10

        # Protective factors are important context, but they must not erase
        # an explicit current suicidal/self-harm signal.
        if signals["protective"] and not (
            signals["crisis"] or signals["self_harm"] or signals.get("plan")
        ):
            score -= 0.10

        if signals["contextual_suicide"] and not (
            signals["crisis"] or signals["self_harm"]
        ):
            score = 0.0

        score += context_risk_boost

        if signals["crisis"] or signals["self_harm"]:
            score = max(score, 0.70)

        if signals.get("plan"):
            score = max(score, 0.85)

        return round(
            max(
                0.0,
                min(score, 1.0)
            ),
            3
        )

    def _determine_risk_level(
        self,
        score: float,
        signals: Dict[str, bool]
    ) -> str:

        if signals["contextual_suicide"]:
            return "low"

        if signals["crisis"]:
            return "high"

        if signals["self_harm"]:
            return "high"

        if signals.get("plan"):
            return "high"

        if score >= 0.60:
            return "high"

        if score >= 0.20:
            return "moderate"

        return "low"

    def _detect_mood(
        self,
        text: str,
        signals: Dict[str, bool]
    ) -> str:

        if signals["crisis"]:
            return "distressed"

        if signals["hopelessness"]:
            return "hopeless"

        if signals["worthlessness"]:
            return "low_self_worth"

        if signals["anxiety"]:
            return "anxious"

        if signals["sad"]:
            return "sad"

        if signals["intent"]:
            return "seeking_support"

        if signals["context_reference"]:
            return "reflective"

        if self._contains_any(
            text,
            [
                "happy",
                "great",
                "good",
                "excited",
                "wonderful",
                "better",
                "feeling better",
                "grateful",
                "relieved"
            ]
        ):
            return "positive"

        return "neutral"

    def _determine_mode(
        self,
        risk_level: str,
        mood: str,
        signals: Dict[str, bool]
    ) -> str:

        if signals["crisis"] or signals["self_harm"]:
            return "crisis"

        if signals["worthlessness"] or signals["serious"]:
            return "serious"

        if signals["sad"]:
            return "sad"

        if signals["anxiety"]:
            return "anxiety"

        if signals["intent"] or signals.get("help_seeking"):
            return "supportive"

        if signals["context_reference"]:
            return "contextual"

        if mood == "positive":
            return "positive"

        return "normal"

    def _evaluate_crisis(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:

        risk_level = analysis.get(
            "risk_level",
            "low"
        )

        signals = analysis.get(
            "signals",
            {}
        )

        if self.crisis_manager is None:
            immediate = (
                risk_level == "high"
                and (
                    signals.get("crisis")
                    or signals.get("self_harm")
                    or signals.get("intent")
                    or signals.get("temporal")
                )
            )

            return {
                "risk_level": risk_level,
                "crisis_detected": bool(
                    signals.get("crisis")
                ),
                "self_harm_detected": bool(
                    signals.get("self_harm")
                ),
                "intent_detected": bool(
                    signals.get("intent")
                ),
                "temporal_signal": bool(
                    signals.get("temporal")
                ),
                "protective_signal": bool(
                    signals.get("protective")
                ),
                "immediate_guidance": immediate,
                "action": (
                    "immediate_human_support"
                    if immediate
                    else "supportive_conversation"
                ),
                "mode": (
                    "crisis"
                    if immediate
                    else "normal"
                ),
                "llm_allowed": not immediate,
                "normal_response_allowed": not immediate
            }

        try:
            result = self.crisis_manager.evaluate(
                risk_level,
                signals,
                analysis.get(
                    "safety_policy",
                    {}
                )
            )

            if isinstance(result, dict):
                return result
        except Exception:
            pass

        immediate = (
            risk_level == "high"
            and (
                signals.get("crisis")
                or signals.get("self_harm")
                or signals.get("intent")
                or signals.get("temporal")
            )
        )

        return {
            "risk_level": risk_level,
            "crisis_detected": bool(
                signals.get("crisis")
            ),
            "self_harm_detected": bool(
                signals.get("self_harm")
            ),
            "intent_detected": bool(
                signals.get("intent")
            ),
            "temporal_signal": bool(
                signals.get("temporal")
            ),
            "protective_signal": bool(
                signals.get("protective")
            ),
            "immediate_guidance": immediate,
            "action": (
                "immediate_human_support"
                if immediate
                else "supportive_conversation"
            ),
            "mode": (
                "crisis"
                if immediate
                else "normal"
            ),
            "llm_allowed": not immediate,
            "normal_response_allowed": not immediate
        }

    def _update_state(
        self,
        analysis: Dict[str, Any]
    ):
        mood = analysis.get(
            "mood",
            "neutral"
        )

        risk_level = analysis.get(
            "risk_level",
            "low"
        )

        detected_topic = analysis.get(
            "detected_topic"
        )

        if detected_topic is None:
            self.context_state.record_follow_up(
                mood=mood,
                risk_level=risk_level
            )
        else:
            self.context_state.update(
                mood=mood,
                risk_level=risk_level,
                topic=detected_topic
            )

        if self.user_profile is not None:
            try:
                self.user_profile.add_topic(
                    self.context_state.last_topic
                )
            except Exception:
                pass

            try:
                self.user_profile.add_mood(
                    self.context_state.current_mood
                )
            except Exception:
                pass

    def _build_context(self) -> Dict[str, Any]:
        messages = [
            item["message"]
            for item in self.memory[-self.max_memory:]
        ]

        return {
            "has_previous_context": bool(messages),
            "message_count": len(messages),
            "recent_user_messages": messages,
            "state": self.get_context_state(),
            "user_profile": self._get_profile()
        }

    def _calculate_context_risk_boost(
        self,
        context: Dict[str, Any]
    ) -> float:

        messages = context.get(
            "recent_user_messages",
            []
        )

        if not messages:
            return 0.0

        boost = 0.0

        for message in messages[-3:]:
            text = self._normalize(message)

            if self._contains_any(
                text,
                [
                    "hopeless",
                    "worthless",
                    "helpless",
                    "lonely",
                    "loneliness",
                    "can't cope",
                    "cannot cope",
                    "can't handle this",
                    "cannot handle this",
                    "feel trapped"
                ]
            ):
                boost += 0.10

            safety_signals = self._detect_signals(text)

            if safety_signals.get("crisis") or safety_signals.get("self_harm"):
                boost += 0.25

        return round(
            min(boost, 0.50),
            3
        )

    def _store_message(
        self,
        message: str
    ):
        if not message:
            return

        normalized = self._normalize(message)

        for item in self.memory:
            if self._normalize(
                item["message"]
            ) == normalized:
                return

        self.turn_count += 1

        stored_message = message

        if self.privacy_manager is not None:
            try:
                stored_message = (
                    self.privacy_manager.sanitize_text(
                        message
                    )
                )
            except Exception:
                stored_message = message

        self.memory.append(
            {
                "message": stored_message,
                "turn": self.turn_count
            }
        )

        if len(self.memory) > self.max_memory:
            self.memory = self.memory[
                -self.max_memory:
            ]

    def _generate_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:

        crisis = analysis.get(
            "crisis",
            {}
        )

        if crisis.get(
            "immediate_guidance",
            False
        ):
            return self._crisis_response()

        if self.response_engine is not None:
            try:
                response = self.response_engine.generate(
                    message,
                    analysis,
                    context
                )

                if isinstance(response, dict):
                    response = response.get(
                        "reply",
                        response.get(
                            "response",
                            ""
                        )
                    )

                if response:
                    return str(response)
            except Exception:
                pass

        mode = analysis["mode"]

        topic = analysis.get(
            "state",
            {}
        ).get(
            "last_topic"
        )

        if mode == "crisis":
            return self._crisis_response()

        if mode == "serious":
            return self._serious_response(topic)

        if mode == "sad":
            return self._sad_response(
                message.lower(),
                topic
            )

        if mode == "anxiety":
            return self._anxiety_response(topic)

        if mode == "supportive":
            return self._intent_response(topic)

        if mode == "contextual":
            return self._contextual_response(
                context,
                topic
            )

        if mode == "positive":
            return self._positive_response(topic)

        if self._is_greeting(message):
            return self._greeting_response()

        if self._is_gratitude(message):
            return self._gratitude_response()

        return self._neutral_response(
            topic,
            context
        )

    def _contextual_response(
        self,
        context: Dict[str, Any],
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "Your college situation seems to be weighing "
                "on you. What part of it feels hardest right now?"
            )

        if topic == "work":
            return (
                "Your internship or career situation seems "
                "important right now. What part feels hardest?"
            )

        if topic == "future":
            return (
                "It sounds like your future is on your mind. "
                "What part feels most uncertain right now?"
            )

        messages = context.get(
            "recent_user_messages",
            []
        )

        if messages:
            return (
                "I'm following what you've shared. "
                "Tell me a little more about that."
            )

        return (
            "I'm listening. Tell me a little more."
        )

    def _serious_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It sounds like your college situation is "
                "becoming difficult to carry. You don't have "
                "to handle everything at once. What feels "
                "most difficult right now?"
            )

        if topic == "work":
            return (
                "It sounds like your work or internship situation "
                "is becoming difficult to carry. You don't have "
                "to handle everything at once. What feels "
                "most difficult right now?"
            )

        return (
            "It sounds like you're going through something "
            "very difficult. You don't have to handle "
            "everything at once. What feels hardest right now?"
        )

    def _sad_response(
        self,
        text: str,
        topic: Optional[str]
    ) -> str:

        if "lonely" in text:
            return (
                "I'm sorry you're feeling lonely. "
                "It can help to talk about what is making "
                "you feel disconnected. What's been happening?"
            )

        if "hopeless" in text:
            return (
                "I'm sorry things feel so difficult right now. "
                "You don't have to explain everything at once. "
                "What feels hardest at the moment?"
            )

        if "worthless" in text:
            return (
                "I'm sorry you're carrying that feeling. "
                "Feeling worthless can be very heavy. "
                "What led you to feel this way?"
            )

        if topic == "college":
            return (
                "I'm sorry you're having a difficult time "
                "with college. What has been weighing on you?"
            )

        if topic == "work":
            return (
                "I'm sorry you're having a difficult time "
                "with work or your internship. What has "
                "been weighing on you?"
            )

        return (
            "I'm sorry you're going through this. "
            "I'm here to listen. What has been weighing on you?"
        )

    def _anxiety_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It sounds like your college and exams are "
                "making you anxious. Let's focus on one part "
                "of your studies at a time. What is worrying "
                "you most?"
            )

        if topic == "work":
            return (
                "It sounds like your internship or career "
                "situation is making you anxious. Let's focus "
                "on one part at a time. What concerns you most?"
            )

        if topic == "future":
            return (
                "It sounds like uncertainty about your future "
                "is making you anxious. Let's focus on what "
                "you can deal with right now. What concerns "
                "you most?"
            )

        return (
            "It sounds like things are feeling overwhelming. "
            "Let's slow things down and focus on one thing "
            "at a time. What is worrying you the most?"
        )

    def _intent_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "I'm here with you. Let's take your college "
                "situation one step at a time. What would "
                "you like help with first?"
            )

        if topic == "work":
            return (
                "I'm here with you. Let's take your internship "
                "or career situation one step at a time. "
                "What would you like help with first?"
            )

        if topic == "future":
            return (
                "I'm here with you. Let's take your future "
                "concerns one step at a time. What would "
                "you like to work through first?"
            )

        return (
            "I'm here with you. Let's slow things down "
            "and focus on what is happening right now."
        )

    def _positive_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It's good to hear that you're feeling better "
                "about college. What has been going well?"
            )

        if topic == "work":
            return (
                "It's good to hear that you're feeling better "
                "about your work or career situation. "
                "What has been going well?"
            )

        if topic == "future":
            return (
                "It's good to hear that you're feeling more "
                "positive about your future. What are you "
                "looking forward to?"
            )

        return (
            "That's good to hear. Tell me more about "
            "what's going well."
        )

    def _neutral_response(
        self,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:

        if topic == "college":
            return (
                "I'm following your college situation. "
                "Tell me a little more about your exams, "
                "studies, or what has been difficult."
            )

        if topic == "work":
            return (
                "I'm following your work and career situation. "
                "Tell me a little more about your internship, "
                "interview, or what has been difficult."
            )

        if topic == "future":
            return (
                "I'm following what you've shared about your "
                "future. Tell me a little more about what's "
                "on your mind."
            )

        if topic == "relationships":
            return (
                "I'm following what you've shared about your "
                "relationship situation. Tell me a little "
                "more about what happened."
            )

        if topic == "family":
            return (
                "I'm following what you've shared about your "
                "family situation. Tell me a little more."
            )

        if topic:
            return (
                f"I'm following your {topic} situation. "
                "Tell me a little more about what's happening."
            )

        if context.get(
            "has_previous_context",
            False
        ):
            return (
                "I'm following what you've shared. "
                "Tell me a little more about what is happening."
            )

        return (
            "I'm here to listen. Tell me what's on your mind."
        )

    def _greeting_response(self) -> str:
        return (
            f"Hi {self.user_name}. "
            "I'm here to listen. What's on your mind?"
        )

    def _gratitude_response(self) -> str:
        return (
            "You're welcome. I'm glad you felt comfortable "
            "sharing that with me."
        )

    def _crisis_response(self) -> str:
        return (
            "I'm really sorry you're going through this. "
            "Your safety is important. If you think you might "
            "act on these thoughts or you're in immediate danger, "
            "please move toward a safe person or place and "
            "contact your local emergency services or a qualified "
            "crisis service. You can keep talking to me while "
            "you reach human support."
        )

    def _build_safety_response(
        self,
        risk_level: str
    ) -> Dict[str, Any]:

        return {
            "risk_level": risk_level,
            "policy": {
                "require_safety_response": True,
                "allow_random_response": False,
                "allow_normal_response": False,
                "require_human_support": True
            },
            "require_safety_response": True,
            "requires_human_support": True,
            "emergency_guidance": (
                "If there is immediate danger, contact local "
                "emergency services or an appropriate crisis service."
            ),
            "do_not": [
                "Do not provide instructions for self-harm.",
                "Do not encourage harmful behavior.",
                "Do not minimize the user's distress."
            ]
        }

    def _get_profile(self) -> Dict[str, Any]:

        if self.user_profile is None:
            return {
                "user_name": self.user_name,
                "preferred_tone": "supportive",
                "preferred_language": "en",
                "preferences": {},
                "interests": [],
                "topic_history": [],
                "mood_history": []
            }

        try:
            return self.user_profile.get()
        except Exception:
            return {
                "user_name": self.user_name,
                "preferred_tone": "supportive",
                "preferred_language": "en",
                "preferences": {},
                "interests": [],
                "topic_history": [],
                "mood_history": []
            }

    def _contains_any(
        self,
        text: str,
        patterns: List[str]
    ) -> bool:

        return any(
            pattern in text
            for pattern in patterns
        )

    def _is_greeting(
        self,
        message: str
    ) -> bool:

        return self._normalize(message) in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
        }

    def _is_gratitude(
        self,
        message: str
    ) -> bool:

        return self._contains_any(
            self._normalize(message),
            [
                "thank you",
                "thanks",
                "thank u"
            ]
        )

    def clear_memory(self):
        self.memory.clear()
        self.turn_count = 0
        self.context_state.reset()

        if self.user_profile is not None:
            try:
                self.user_profile.reset()
            except Exception:
                pass

    def get_memory(self):
        return list(self.memory)

    def get_context(self):
        return self._build_context()

    def get_context_state(
        self
    ) -> Dict[str, Any]:
        return self.context_state.get_state()

    def get_last_message(self):
        if not self.memory:
            return ""

        return self.memory[-1]["message"]

    def get_turn_count(self):
        return self.turn_count

    def get_profile(self):
        return self._get_profile()

    def get_safety_audit(self):
        if self.safety_audit is None:
            return []

        try:
            return self.safety_audit.get_records()
        except Exception:
            return []

    def clear_safety_audit(self):
        if self.safety_audit is not None:
            try:
                self.safety_audit.clear()
            except Exception:
                pass