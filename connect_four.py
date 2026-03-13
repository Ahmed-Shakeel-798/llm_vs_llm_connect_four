class ConnectFour:
    ROWS = 6
    COLS = 7
    COL_LABELS = "ABCDEFG"


    def __init__(self):
        self.board = [["." for _ in range(self.COLS)] for _ in range(self.ROWS)] 
        self.current_player = "X"


    def legal_moves(self):
        """Return list of column indices where a move is possible."""
        return [c for c in range(self.COLS) if self.board[0][c] == "."] # A column is full if the top row is filled.
    

    def move(self, col):
        """Drop a piece in the specified column index (0–6)."""
        if col not in range(self.COLS):
            raise ValueError("Column out of range")

        if col not in self.legal_moves():
            raise ValueError("Column is full")

        for row in reversed(range(self.ROWS)):
            if self.board[row][col] == ".":
                player = self.current_player
                self.board[row][col] = player

                win = self.check_win(row, col, player)

                self.current_player = "O" if player == "X" else "X"

                return row, col, player, win

            
    def count_direction(self, row, col, dr, dc, player):
        count = 0
        r = row + dr
        c = col + dc

        while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc

        return count
    
    
    def check_win(self, row, col, player):
        directions = [
            ((0,1), (0,-1)),   # horizontal
            ((1,0), (-1,0)),   # vertical
            ((1,1), (-1,-1)),  # diagonal \
            ((1,-1), (-1,1))   # diagonal /
        ]

        for d1, d2 in directions:
            count = 1
            count += self.count_direction(row, col, d1[0], d1[1], player)
            count += self.count_direction(row, col, d2[0], d2[1], player)

            if count >= 4:
                return True

        return False


    def print_board(self):
        """Print the board to terminal."""
        print(" " + " ".join(self.COL_LABELS))
        for row in self.board:
            print("|" + " ".join(row) + "|")
        print("+" + "--" * self.COLS + "+")


    def to_llm_json(self):
        return {
            "current_player": self.current_player,
            "legal_moves": self.legal_moves(),
            "board_rows": ["".join(row) for row in self.board]
        }