import io
import re
import chess
import chess.pgn
import numpy as np

def extract_bitboards_and_scores(pgn_text):
    dataset = []
    to_play_next = chess.BLACK
    # Create a StringIO object from the PGN text
    pgn = io.StringIO(pgn_text)

    # Iterate over all games in the PGN file
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break

        # Check if the game has embedded Stockfish evaluations
        has_evaluations = any('[%eval ' in node.comment for node in game.mainline())
        if not has_evaluations:
            continue

        # Setup initial empty chess board
        board = chess.Board()

        # Iterate through all moves of the game
        for node in game.mainline():
            move = node.move
            board.push(move)
            # Get the comment (which contains the evaluation) for this move
            comment = node.comment
            match = re.search(r"\[%eval (.*?)\]", comment)
            if match is None:
                continue
            
            score = float(match.group(1))

            # Convert the board position to bitboards and add to list
            bitboards = board_to_bitboards(board)

            dataset.append([bitboards, to_play_next, score])
            to_play_next = not to_play_next
    return dataset

def board_to_bitboards(board):
    bitboards = []
    for color in chess.COLORS:
        for piece_type in chess.PIECE_TYPES:
            bitboards.append(board.pieces_mask(piece_type, color))
    return bitboards

def bitboards_to_board(bitboards):
    # Initialize an empty board
    board = chess.Board(None)

    # Ensure we have 12 bitboards
    assert len(bitboards) == 12, "Need 12 bitboards for a complete position"

    # Iterate over each color and piece type
    for color in chess.COLORS:
        for piece_type in chess.PIECE_TYPES:
            # Get the bitboard for this piece type and color
            bitboard = bitboards.pop(0)
            # Iterate over each square in the bitboard
            for square in range(64):  # change here
                if bitboard & (1 << square):  # If this piece is on this square
                    piece = chess.Piece(piece_type, color)
                    board.set_piece_at(square, piece)
    return board

def bitboards_to_fens(bitboards_list):
    fens = []
    for bitboards in bitboards_list:
        board = bitboards_to_board(bitboards)
        fens.append(board.fen())
    return fens

def bitboard_to_fen(bitboards):
    board = bitboards_to_board(bitboards)
    fen = board.fen()
    return fen

def bitboard_to_array(bitboard):
    # Initialize an 8x8 array with zeroes
    array = [[0 for _ in range(8)] for _ in range(8)]
    
    # Iterate over each square on the board
    for square in range(64):
        # Calculate the row and column index
        row = square // 8
        col = square % 8

        # Check if the bit at this square is set
        if bitboard & (1 << square):
            # If it is, set the corresponding element in the array to 1
            array[row][col] = 1
            
    return np.array(array, dtype=np.int8)
    
def bitboards_to_3d_array(bitboards):
    arrays = [bitboard_to_array(bitboard) for bitboard in bitboards]
    return np.array(arrays, dtype=np.int8)
    
def array_to_bitboard(array):
    bitboard = 0
    square = -1
    for row in range(8):
        for col in range(8):
            # Increment the square index (from 0 to 63) based on row and column
            square += 1
            if array[row][col] == 1:
                # Set the bit at the calculated square index
                bitboard |= (1 << square)
    return bitboard