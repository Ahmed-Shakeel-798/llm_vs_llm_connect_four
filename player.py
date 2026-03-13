import json
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"

class LLMPlayer:
    
    def __init__(self, model, mark):
        self.model = model
        self.mark = mark
        self.client = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

        self.system_prompt = f"""
You are a Connect Four player.

You are playing as: {mark}

Board representation:
- 6 rows
- 7 columns
- columns indexed 0–6
- pieces drop downward

Symbols:
X = player X
O = player O
. = empty

Your job:
1. Analyze the board
2. Identify threats (yours and opponent)
3. Explain your strategy
4. Choose a legal move

Respond ONLY in JSON with the format:

{{
  "assessment": "...",
  "threats": "...",
  "strategy": "...",
  "move": <column_number>
}}
"""
        
    def build_user_prompt(self, board_state):

        return f"""
Current board state:

{json.dumps(board_state, indent=2)}

You are player {self.mark}.

Choose your move.
"""
    
    def make_move(self, board):

        state = board.to_llm_json()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.build_user_prompt(state)}
            ],
            response_format={"type": "json_object"}
        )

        output = json.loads(response.choices[0].message.content)

        return output
