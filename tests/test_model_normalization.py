"""
Unit tests for model name normalization.

These tests verify that model names are correctly normalized across the codebase,
ensuring compatibility with OpenGPU Relay API.
"""


def normalize_model(model: str) -> str:
    """
    Normalize model name for OpenGPU Relay.
    
    Only removes "openai/" prefix. Other providers like "moonshotai/", "Qwen/",
    "deepseek-ai/" are NOT standard litellm providers and should be kept as part
    of the model name.
    
    Args:
        model: Model name (e.g., "openai/gpt-5.2", "Qwen/Qwen3-Coder", "moonshotai/kimi-k2.5")
    
    Returns:
        Normalized model name
    """
    if model.startswith("openai/"):
        return model[7:]  # Remove "openai/" prefix
    return model  # Keep full model name


class TestModelNormalization:
    """Test cases for model name normalization."""
    
    # Standard OpenAI models - should strip "openai/" prefix
    def test_openai_gpt5(self):
        assert normalize_model("openai/gpt-5.2") == "gpt-5.2"
    
    def test_openai_gpt4(self):
        assert normalize_model("openai/gpt-4") == "gpt-4"
    
    def test_openai_o1(self):
        assert normalize_model("openai/o1-preview") == "o1-preview"
    
    # Anthropic models - keep full name (not standard litellm provider)
    def test_anthropic_claude(self):
        assert normalize_model("anthropic/claude-opus-4-6") == "anthropic/claude-opus-4-6"
    
    def test_anthropic_sonnet(self):
        assert normalize_model("anthropic/claude-sonnet-4-6") == "anthropic/claude-sonnet-4-6"
    
    # Ollama models - keep full name (not standard litellm provider)
    def test_ollama_llama(self):
        assert normalize_model("ollama/llama3.2:3b") == "ollama/llama3.2:3b"
    
    def test_ollama_deepseek(self):
        assert normalize_model("ollama/deepseek-r1:8b") == "ollama/deepseek-r1:8b"
    
    # Qwen models - keep full name (Qwen is part of model name)
    def test_qwen_qwen3_coder(self):
        assert normalize_model("Qwen/Qwen3-Coder") == "Qwen/Qwen3-Coder"
    
    def test_qwen_qwen25_vl(self):
        assert normalize_model("qwen/qwen2.5-vl-72b-instruct") == "qwen/qwen2.5-vl-72b-instruct"
    
    # Moonshot models - keep full name
    def test_moonshot_kimi(self):
        assert normalize_model("moonshotai/kimi-k2.5") == "moonshotai/kimi-k2.5"
    
    # DeepSeek models - keep full name
    def test_deepseek_v3(self):
        assert normalize_model("deepseek-ai/DeepSeek-V3.1") == "deepseek-ai/DeepSeek-V3.1"
    
    # Models without provider prefix - should remain unchanged
    def test_no_prefix_gpt5(self):
        assert normalize_model("gpt-5.2") == "gpt-5.2"
    
    def test_no_prefix_llama(self):
        assert normalize_model("llama3.2:3b") == "llama3.2:3b"
    
    # Edge cases
    def test_empty_string(self):
        assert normalize_model("") == ""
    
    def test_slash_only(self):
        assert normalize_model("/") == "/"
    
    def test_openai_slash_only(self):
        assert normalize_model("openai/") == ""


def run_tests():
    """Run all test cases."""
    test = TestModelNormalization()
    tests_passed = 0
    tests_failed = 0
    
    test_methods = [m for m in dir(test) if m.startswith("test_")]
    for method_name in test_methods:
        try:
            getattr(test, method_name)()
            print(f"✓ {method_name}")
            tests_passed += 1
        except AssertionError as e:
            print(f"✗ {method_name}: {e}")
            tests_failed += 1
    
    print(f"\n{tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
