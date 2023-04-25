from collections import defaultdict

from config import OPENAI_API_TOKEN
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory

template = """Вы являетесь Эльзой, снежной королевой из мультфильма Frozen.
Отвечайте на вопросы и помогайте советами, используя свои знания и магические способности, чтобы создать теплую и заботливую атмосферу.
Демонстрируйте мудрость и опыт Эльзы, учитывая ее историю, семейные связи и дружбу с персонажами во вселенной Frozen.
Отвечает на языке собеседника.

{history}
Человек: {human_input}
Эльза:"""

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)


def _build_memory() -> ConversationBufferWindowMemory:
    return ConversationBufferWindowMemory(
        human_prefix="Человек", ai_prefix="Эльза", k=3
    )


MEMORY_BY_USER_ID = defaultdict(_build_memory)


def _get_chain(user_id: int):
    return LLMChain(
        llm=ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=OPENAI_API_TOKEN,
            max_tokens=1000,
        ),
        prompt=prompt,
        verbose=True,
        memory=MEMORY_BY_USER_ID[user_id],
    )


async def get_answer(human_input: str, user_id: int):
    chatgpt_chain = _get_chain(user_id)
    return await chatgpt_chain.apredict(human_input=human_input)
