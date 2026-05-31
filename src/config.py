import os
import weave
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

WANDB_API_KEY = os.environ["WANDB_API_KEY"]
WEAVE_PROJECT = os.getenv("WEAVE_PROJECT", "legal-letter-triage")
MODEL = os.getenv("MODEL", "Qwen/Qwen3-Coder-480B-A35B-Instruct")

weave.init(WEAVE_PROJECT)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.inference.wandb.ai/v1"),
)
