import json
import os
import tempfile
from typing import Any
from unittest import TestCase, mock

from intelliterm.chat import Chat
from intelliterm.prompt import Prompt


class TestChat(TestCase):
    test_chat_title: str = "title"

    def setUp(self) -> None:
        self.chat = Chat()

        self.chat.context([
            Prompt(content="one"),
            Prompt(content="two"),
            Prompt(content="three")
        ])

    @mock.patch.object(Chat, 'create_title')
    def test_save(self, test_create_title: Any) -> None:
        test_create_title.return_value = self.test_chat_title

        with tempfile.TemporaryDirectory() as test_dir:
            with mock.patch('intelliterm.chat.SAVED_CHATS_DIR', test_dir):
                self.chat.save()

                with open(
                    os.path.join(test_dir, f"{self.test_chat_title}.json")
                ) as tmp_file:
                    contents = tmp_file.read()
                    contents_json = json.loads(contents)

                    for i, prompt in enumerate(self.chat._context):
                        self.assertEqual(
                            prompt.content,
                            contents_json['_context'][i]['content'],
                        )
