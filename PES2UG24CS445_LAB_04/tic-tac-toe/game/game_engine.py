from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # Scoreboard
        self.x_score = 0
        self.o_score = 0
        self.draws = 0

        # Default starter
        self.starter = HUMAN_SYMBOL

        # Start the first round
        self.reset_round()

    def reset_round(self):
        """Restart the current round without resetting the scoreboard."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.starter
        self.round_over = False
        self.winner = None

        # If O starts, the computer moves automatically
        if self.current_player == COMPUTER_SYMBOL:
            self._maybe_take_computer_turn()

    def reset_match(self):
        """Reset the complete match including the scoreboard."""
        self.x_score = 0
        self.o_score = 0
        self.draws = 0

        self.reset_round()

    def choose_starter(self, starter):
        """Choose who starts the next round."""
        if starter not in (HUMAN_SYMBOL, COMPUTER_SYMBOL):
            return

        self.starter = starter
        self.reset_round()

    def handle_click(self, pos):
        # Do nothing after the round ends
        if self.round_over:
            return

        # Only X is controlled by the player
        if self.current_player != HUMAN_SYMBOL:
            return

        cell = board_pos_to_cell(pos)

        if cell is None:
            return

        row, col = cell

        # Reject an occupied cell
        if self.board[row][col] is not None:
            return

        # Place X
        self.board[row][col] = HUMAN_SYMBOL

        # Check the result
        self.check_round_end()

        if self.round_over:
            return

        # Computer's turn
        self.current_player = COMPUTER_SYMBOL
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over:
            return

        if self.current_player != COMPUTER_SYMBOL:
            return

        move = choose_move(self.board)

        if move is None:
            return

        row, col = move

        # Never overwrite an occupied cell
        if self.board[row][col] is not None:
            return

        # Place O
        self.board[row][col] = COMPUTER_SYMBOL

        # Check the result
        self.check_round_end()

        if self.round_over:
            return

        # Back to player's turn
        self.current_player = HUMAN_SYMBOL

    def handle_keydown(self, key):
        import pygame

        # X starts the next round
        if key == pygame.K_x:
            self.choose_starter(HUMAN_SYMBOL)

        # O starts the next round
        elif key == pygame.K_o:
            self.choose_starter(COMPUTER_SYMBOL)

        # Restart current round
        elif key == pygame.K_r:
            self.reset_round()

        # Reset complete match
        elif key == pygame.K_m:
            self.reset_match()

    def check_round_end(self):
        # Check winner FIRST.
        # This handles a winning move that fills the last cell.

        winner = check_winner(self.board)

        if winner:
            self.round_over = True
            self.winner = winner

            if winner == HUMAN_SYMBOL:
                self.x_score += 1
            elif winner == COMPUTER_SYMBOL:
                self.o_score += 1

            return

        # If there is no winner and board is full, it is a draw
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.draws += 1

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_board(surface, self.board)

        renderer.draw_scoreboard(
            surface,
            font,
            self.x_score,
            self.o_score,
            self.draws
        )
        
        renderer.draw_controls(surface, font)

        turn_label = (
            "Your turn (X)"
            if self.current_player == HUMAN_SYMBOL
            else "Computer's turn (O)"
        )

        renderer.draw_text(
            surface,
            font,
            turn_label,
            (10, 20)
        )

        if self.round_over:
            text = (
                f"{self.winner} wins!"
                if self.winner
                else "Draw!"
            )

            renderer.draw_banner(
                surface,
                font,
                f"{text} Press R for a new round."
            )