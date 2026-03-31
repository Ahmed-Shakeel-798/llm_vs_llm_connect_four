from connect_four import ConnectFour
from player import LLMPlayer

OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

board = ConnectFour()

player_x = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "X")
player_o = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "O")

players = {
    "X": player_x,
    "O": player_o
}

board.print_board()

while True:

    current_mark = board.current_player
    player = players[current_mark]

    print(f"\nPlayer {current_mark}'s turn")

    try:
        result = player.make_move(board)

        print("LLM response:")
        print(result)

        move = result["move"]

        row, col, player_mark, win = board.move(move)

        board.print_board()

        if win:
            print(f"\nPlayer {player_mark} wins!")
            break

        if not board.legal_moves():
            print("\nGame is a draw.")
            break

    except Exception as e:

        print(f"\nError occurred: {e}")

        winner = "O" if current_mark == "X" else "X"
        print(f"Player {winner} wins by opponent error.")

        break