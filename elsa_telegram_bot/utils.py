import re
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader
from telegram.helpers import escape_markdown


@asynccontextmanager
async def temp_file(suffix: str) -> AsyncIterator[AsyncBufferedReader]:
    async with aiofiles.tempfile.NamedTemporaryFile(mode="w+b", suffix=suffix) as file:
        yield file


def escape_markdown_except_code(text: str) -> str:
    escape_chars = r"\_*[]()~>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def quoted_response(question: str, answer: str) -> str:
    safe_question = escape_markdown(question, version=2)
    safe_answer = escape_markdown_except_code(answer)
    return f"\\> _{safe_question}_\n\n{safe_answer}"
