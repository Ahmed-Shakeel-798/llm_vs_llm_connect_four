from connect_four import ConnectFour
from player import LLMPlayer

board = ConnectFour()

player_x = LLMPlayer("llama3.2", "X")
player_o = LLMPlayer("llama3.2", "O")

board.print_board()

result = player_x.make_move(board)

print(result)

move = result["move"]

row, col, player, win = board.move(move)

board.print_board()


# board = ConnectFour()
# board.move(3)
# board.move(2)
# board.move(5)
# board.move(7)


# print(board.to_llm_json())


# board.print_board()

# print("Legal moves:", [ConnectFour.COL_LABELS[c] for c in board.legal_moves()])