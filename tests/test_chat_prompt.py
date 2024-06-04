from unittest import TestCase

from intelliterm.prompt import Prompt


class TestPrompt(TestCase):
    def test_count_tokens(self) -> None:
        dummy_prompt = Prompt(content="this prompt is exactly seven tokens long")
        num_tokens = dummy_prompt.token_count()

        self.assertEqual(7, num_tokens)
