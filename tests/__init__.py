def __init__(self, user_name: str = "friend"):

    self.user_name = user_name
    self.memory = ChatMemory(max_messages=10)
    self.risk_engine = RiskEngine()
    self.safety_engine = SafetyEngine()
    self.context_engine = ContextEngine(
        max_context_messages=3
    )