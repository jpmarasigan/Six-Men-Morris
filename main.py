from time import sleep
import pygame
import sys
import random
import math
import copy

pygame.init()

# Set up display
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Six Men Morris - MP4")

# Define font
font = pygame.font.SysFont(None, 30)

# Load images
start_background = pygame.image.load("./images/start_background.jpg")
background = pygame.image.load("./images/six_men_morris_board.png")
player_piece = pygame.image.load("./images/player_circle.png")
ai_piece = pygame.image.load("./images/ai_circle.png")
outline = pygame.image.load('./images/move_circle.png')
recommend_piece = pygame.image.load('./images/recommend_circle.png')

# Resize images
start_background = pygame.transform.scale(start_background, (WIDTH, HEIGHT))
background = pygame.transform.scale(background, (WIDTH, HEIGHT-100))
player_piece = pygame.transform.scale(player_piece, (50, 50))
ai_piece = pygame.transform.scale(ai_piece, (50, 50))
outline = pygame.transform.scale(outline, (60, 60))
recommend_piece = pygame.transform.scale(recommend_piece, (22, 22))

# start button
start_button = pygame.Rect(200, 535, 200, 50)
transparent_surface = pygame.Surface((200, 50), pygame.SRCALPHA)     # Create semi transparent color
transparent_surface.fill((17, 19, 17, 160))                          # rgba

# Set Color             
BOARD = (255, 240, 192)
BLACK = (0, 0, 0)
HIGHLIGHT = (40,71,97)
TRANSPARENT = (0, 0, 0, 0)


# Initialization
piece_coordinates = [
    (34, 37),              (274, 37),              (515, 37),         # first row
               (153, 156), (274, 156), (395, 156),                    # second row
    (34, 276), (154, 276),             (395, 276), (513, 276),        # third row
               (153, 398), (274, 398), (395, 398),                    # fourth row
    (34, 516),             (274, 516),             (515, 516),        # fifth row
]
winning_positions = [
    ((34, 37), (274, 37), (515, 37)),
    ((515, 37), (513, 276), (515, 516)),
    ((34, 516), (274, 516), (515, 516)),
    ((34, 37), (34, 276), (34, 516)),
    ((153, 156), (274, 156), (395, 156)),
    ((395, 156), (395, 276), (395, 398)),
    ((153, 398), (274, 398), (395, 398)),
    ((153, 156), (154, 276), (153, 398)),
]
current_player = 1                        # player first
deployed_pieces = {1: [], 2: []}          # Dictionary to store deployed pieces for each player
num_pieces_deployed = 0
all_pieces_deployed = False
selected_piece = None
recommend_move = []
is_removed_piece = False
winner = None
prev_player = None
previous_winning_moves = {1: [], 2: []}   # stored the previous untouched mill moves
game_started = False

# status text
num_piece = 0
piece_text = font.render(f"Drop your ({num_piece+1}) piece.", True, BLACK)
text_rect = None

def draw_board():
    global selected_piece

    screen.blit(background, (0, 0))
    for player, pieces in deployed_pieces.items():
        for piece_coord in pieces:
            if player == 1:
                screen.blit(player_piece, piece_coord)
            else:
                screen.blit(ai_piece, piece_coord)

    if selected_piece is not None:
        for select in selected_piece:
            screen.blit(outline, select)

    if recommend_move:
        for recommend in recommend_move:
            screen.blit(recommend_piece, recommend)

    # display description
    text_width = piece_text.get_width()
    x = (WIDTH - text_width) // 2
    screen.blit(piece_text, (x, 600))


# Function to handle player input
def deploy_piece():
    global prev_player, current_player, deployed_pieces, num_pieces_deployed, num_piece, piece_text, is_removed_piece, winner

    if not winner:
        if pygame.mouse.get_pressed()[0]:       # Check for mouse button press event
            mouse_pos = pygame.mouse.get_pos()
            for piece_coord in piece_coordinates:
                if pygame.Rect(piece_coord, (50, 50)).collidepoint(mouse_pos):
                    if piece_coord not in [piece for pieces in deployed_pieces.values() for piece in pieces]:
                        deployed_pieces[current_player].append(piece_coord)
                        print(f"Player deploy piece at {piece_coord}")
                        num_pieces_deployed += 1
                        prev_player = current_player
                        current_player = 2
                        is_removed_piece = False
                        if len(deployed_pieces[1]) < 6:
                            num_piece = num_piece + 1
                            piece_text = font.render(f"Drop your ({num_piece+1}) piece.", True, BLACK)
                        else:
                            piece_text = font.render(f"Move your selected piece", True, BLACK)
        
    return



def test_mill(state):
    global winning_positions

    for win_pos in winning_positions:
        if all(piece in state[2] for piece in win_pos):
            return '2'
        if all(piece in state[1] for piece in win_pos):
            return '1'
    return None


def max_value(state, alpha, beta, depth, new_move):
    global all_pieces_deployed, piece_coordinates, num_pieces_deployed
    
    if test_mill(state) == '2':
        return 10
    if test_mill(state) == '1':
        return -10
    if depth == 0:
        return evaluate_board(state)
    
    max_val = -math.inf
    if num_pieces_deployed < 12 and not all_pieces_deployed:
        for move in piece_coordinates:
            if move not in state[1] and move not in state[2]:
                next_state = copy.deepcopy(state)
                next_state[2].append(move)
                val = min_value(next_state, alpha, beta, depth-1, new_move)
                if val > max_val:
                    max_val = val
                if val >= beta:
                    return val
                if val > alpha:
                    alpha = val
    else:
        for move in piece_coordinates:
            if move in state[2]:
                next_state, new_move = is_valid_move_ai(state, move, new_move)
                val = min_value(next_state, alpha, beta, depth-1, new_move)
                if val > max_val:
                    max_val = val
                if val >= beta:
                    return val
                if val > alpha:
                    alpha = val
    return max_val


def min_value(state, alpha, beta, depth, new_move):
    global all_pieces_deployed, piece_coordinates, num_pieces_deployed
    
    if test_mill(state) == '2':
        return 10
    if test_mill(state) == '1':
        return -10
    if depth == 0:
        return evaluate_board(state)

    min_val = math.inf
    if num_pieces_deployed < 12 and not all_pieces_deployed:
        for move in piece_coordinates:
            if move not in state[1] and move not in state[2]:
                next_state = copy.deepcopy(state)
                next_state[1].append(move)
                val = max_value(next_state, alpha, beta, depth-1, new_move)
                if val < min_val:
                    min_val = val
                if val <= alpha:
                    return val
                if val < beta:
                    beta = val
    else:
        for move in piece_coordinates:
            if move in state[1]:
                next_state, new_move = is_valid_move_human(state, move, new_move)
                val = max_value(next_state, alpha, beta, depth-1, new_move)
                if val < min_val:
                    min_val = val
                if val <= alpha:
                    return val
                if val < beta:
                    beta = val
    return min_val


def minimax_decision(deployed_pieces):
    global piece_coordinates, all_pieces_deployed, num_pieces_deployed
    max_val = -math.inf
    prev_move = None
    max_depth = 4
    max_new_move = None

    if num_pieces_deployed < 12 and not all_pieces_deployed:
        for move in piece_coordinates:
            if move not in deployed_pieces[1] and move not in deployed_pieces[2]:
                next_state = copy.deepcopy(deployed_pieces)
                next_state[2].append(move)
                val = min_value(next_state, -math.inf, math.inf, max_depth, max_new_move)
                if val > max_val:
                    print(f"Max deploy: {move}")
                    print("="*45)
                    max_val = val
                    prev_move = move
    else:
        new_move = None
        for move in piece_coordinates:
            if move in deployed_pieces[2]:
                next_state, new_move = is_valid_move_ai(deployed_pieces, move, new_move)
                print("Move: ", move)
                print("new move: ", new_move)
                if new_move is None:
                    continue
                val = min_value(next_state, -math.inf, math.inf, max_depth, new_move)
                if val > max_val:
                    print(f"Max move: {move}")
                    print(f"Max new move {new_move}")
                    print("="*45)
                    max_val = val
                    prev_move = move
                    max_new_move = new_move
                    
    return prev_move, max_new_move


def is_valid_move_ai(state, move, new_move):
    global piece_coordinates
    next_state = copy.deepcopy(state)
    prev_state = copy.deepcopy(state)
    new_move = None

    if len(state[2]) == 3:
        for dest_coord in piece_coordinates:
            if dest_coord not in state[1] and dest_coord not in state[2]:
                new_move = dest_coord
                index = next_state[2].index(move)
                next_state[2][index] = new_move
                break
    else:
        if move == (34, 37) and (274, 37) not in state[1] and (274, 37) not in state[2]:      # first row
            if next_state != state:
                next_state = copy.deepcopy(state)       
            new_move = (274, 37)              
            index = next_state[2].index(move)       # next_state[2][0] = (274, 37)
            next_state[2][index] = new_move         # next_state[2] = [(274, 37), (515, 37), (515, 37)]
        if move == (34, 37) and (34, 276) not in state[1] and (34, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 37) and (34, 37) not in state[1] and (34, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 37) and (274, 156) not in state[1] and (274, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 37) and (515, 37) not in state[1] and (515, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (515, 37) and (274, 37) not in state[1] and (274, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (515, 37) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (153, 156) and (274, 156) not in state[1] and (274, 156) not in state[2]:   # second row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (153, 156) and (154, 276) not in state[1] and (154, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 156) and (153, 156) not in state[1] and (153, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 156) and (274, 37) not in state[1] and (274, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 156) and (395, 156) not in state[1] and (395, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 156) and (274, 156) not in state[1] and (274, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 156) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (34, 276) and (34, 37) not in state[1] and (34, 37) not in state[2]:     # third row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (34, 276) and (34, 516) not in state[1] and (34, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (34, 276) and (154, 276) not in state[1] and (154, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (154, 276) and (34, 276) not in state[1] and (34, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (154, 276) and (153, 156) not in state[1] and (153, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (154, 276) and (153, 398) not in state[1] and (153, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 276) and (395, 156) not in state[1] and (395, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 156)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 276) and (395, 398) not in state[1] and (395, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 276) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (513, 276) and (515, 37) not in state[1] and (515, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 37)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (513, 276) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276) 
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (513, 276) and (515, 516) not in state[1] and (515, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (153, 398) and (154, 276) not in state[1] and (154, 276) not in state[2]:      # fourth row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (153, 398) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 398) and (153, 398) not in state[1] and (153, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 398) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 398) and (395, 398) not in state[1] and (395, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 398) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (395, 398) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (34, 516) and (34, 276) not in state[1] and (34, 276) not in state[2]:     #   fifth row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (34, 516) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 516) and (34, 516) not in state[1] and (34, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 516) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (274, 516) and (515, 516) not in state[1] and (515, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (515, 516) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[2].index(move)
            next_state[2][index] = new_move
        if move == (515, 516) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[2].index(move)
            next_state[2][index] = new_move

    return next_state, new_move



def is_valid_move_human(state, move, new_move):
    global piece_coordinates
    next_state = copy.deepcopy(state)
    new_move = None

    if len(state[1]) == 3:
        for dest_coord in piece_coordinates:
            if dest_coord not in state[1] and dest_coord not in state[2]:
                new_move = dest_coord
                index = next_state[1].index(move)
                next_state[1][index] = new_move
                break
    else:
        if move == (34, 37) and (274, 37) not in state[1] and (274, 37) not in state[2]:        # first row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (34, 37) and (34, 276) not in state[1] and (34, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 37) and (34, 37) not in state[1] and (34, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 37) and (274, 156) not in state[1] and (274, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 37) and (515, 37) not in state[1] and (515, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (515, 37) and (274, 37) not in state[1] and (274, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (515, 37) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (153, 156) and (274, 156) not in state[1] and (274, 156) not in state[2]:      # second row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (153, 156) and (154, 276) not in state[1] and (154, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 156) and (153, 156) not in state[1] and (153, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 156) and (274, 37) not in state[1] and (274, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 156) and (395, 156) not in state[1] and (395, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 156) and (274, 156) not in state[1] and (274, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 156) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move   
        if move == (34, 276) and (34, 37) not in state[1] and (34, 37) not in state[2]:       # third row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (34, 276) and (34, 516) not in state[1] and (34, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (34, 276) and (154, 276) not in state[1] and (154, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (154, 276) and (34, 276) not in state[1] and (34, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (154, 276) and (153, 156) not in state[1] and (153, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (154, 276) and (153, 398) not in state[1] and (153, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 276) and (395, 156) not in state[1] and (395, 156) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 156)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 276) and (395, 398) not in state[1] and (395, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 276) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (513, 276) and (515, 37) not in state[1] and (515, 37) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 37)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (513, 276) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276) 
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (513, 276) and (515, 516) not in state[1] and (515, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (153, 398) and (154, 276) not in state[1] and (154, 276) not in state[2]:   # fourth row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (154, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (153, 398) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 398) and (153, 398) not in state[1] and (153, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (153, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 398) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 398) and (395, 398) not in state[1] and (395, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 398) and (395, 276) not in state[1] and (395, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (395, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (395, 398) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (34, 516) and (34, 276) not in state[1] and (34, 276) not in state[2]:     # fifth row
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (34, 516) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 516) and (34, 516) not in state[1] and (34, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (34, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 516) and (274, 398) not in state[1] and (274, 398) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 398)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (274, 516) and (515, 516) not in state[1] and (515, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (515, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (515, 516) and (274, 516) not in state[1] and (274, 516) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (274, 516)
            index = next_state[1].index(move)
            next_state[1][index] = new_move
        if move == (515, 516) and (513, 276) not in state[1] and (513, 276) not in state[2]:
            if next_state != state:
                next_state = copy.deepcopy(state)  
            new_move = (513, 276)
            index = next_state[1].index(move)
            next_state[1][index] = new_move

    return next_state, new_move



def ai_deploy_piece():
    global prev_player, current_player, deployed_pieces, num_pieces_deployed, is_removed_piece, winner

    if not winner:
        # Get the best move for the AI using the alpha-beta pruning algorithm
        ai_piece, _ = minimax_decision(deployed_pieces)
        print(f"AI deploy piece at: {ai_piece}")
        apply_deploy(ai_piece)
        prev_player = current_player
        current_player = 1
        is_removed_piece = False

    return


def move_piece():
    global prev_player, current_player, selected_piece, piece_coordinates, deployed_pieces, recommend_move, winner, is_removed_piece, previous_winning_moves

    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()
        for piece_coord in deployed_pieces[current_player]:
            if pygame.Rect(piece_coord, (50, 50)).collidepoint(mouse_pos):
                recommend_move = []     # clear the array
                # outline coordinates
                selected_piece = [(piece_coord[0]-5, piece_coord[1]-5)]
                if len(deployed_pieces[1]) <= 3:
                    for dest_coord in piece_coordinates:
                        if dest_coord not in deployed_pieces[1] and dest_coord not in deployed_pieces[2]:
                            recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                else:
                    for dest_coord in piece_coordinates:
                        if dest_coord not in deployed_pieces[1] and dest_coord not in deployed_pieces[2]:
                            # RECOMMENDATION MOVES
                            if piece_coord == (34, 37) and (dest_coord == (34, 276) or dest_coord == (274, 37)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (274, 37) and (dest_coord == (34, 37) or dest_coord == (515, 37) or dest_coord == (274, 156)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (515, 37) and (dest_coord == (274, 37) or dest_coord == (513, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (153, 156) and (dest_coord == (154, 276) or dest_coord == (274, 156)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (274, 156) and (dest_coord == (153, 156) or dest_coord == (395, 156) or dest_coord == (274, 37)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (395, 156) and (dest_coord == (274, 156) or dest_coord == (395, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (34, 276) and (dest_coord ==(34, 37) or dest_coord == (34, 516) or dest_coord == (154, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (154, 276) and (dest_coord == (34, 276) or dest_coord == (153, 156) or dest_coord == (153, 398)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (395, 276) and (dest_coord == (395, 156) or dest_coord == (395, 398) or dest_coord == (513, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (513, 276) and (dest_coord == (515, 37) or dest_coord == (515, 516) or dest_coord == (395, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (153, 398) and (dest_coord == (154, 276) or dest_coord == (274, 398)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (274, 398) and (dest_coord == (153, 398) or dest_coord == (274, 516) or dest_coord == (395, 398)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (395, 398) and (dest_coord == (274, 398) or dest_coord == (395, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (34, 516) and (dest_coord == (34, 276) or dest_coord == (274, 516)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (274, 516) and (dest_coord == (34, 516) or dest_coord == (274, 398) or dest_coord == (515, 516)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))
                            elif piece_coord == (515, 516) and (dest_coord == (274, 516) or dest_coord == (513, 276)):
                                recommend_move.append((dest_coord[0]+13, dest_coord[1]+14))   

    # if next move clicked
    if winner:
        recommend_move = []
        return
    else:
        if pygame.mouse.get_pressed()[0]: 
            for move in recommend_move:
                adjusted_move = (move[0]-13, move[1]-14)
                adjusted_selected_piece = (selected_piece[0][0]+5, selected_piece[0][1]+5)
                if pygame.Rect(adjusted_move, (50, 50)).collidepoint(mouse_pos):
                    index = deployed_pieces[current_player].index(adjusted_selected_piece)
                    
                    # Check if the piece being moved is in previous_winning_moves
                    for win_move in previous_winning_moves[current_player]:
                        if adjusted_selected_piece in win_move:
                            previous_winning_moves[current_player].remove(win_move)     # make the winning move available again

                    deployed_pieces[current_player][index] = adjusted_move
                    selected_piece = None     # remove selected piece
                    recommend_move = []       # remove recommended piece
                    is_removed_piece = False
                    prev_player = current_player
                    current_player = 2 if current_player == 1 else 1
                    return


def ai_move():
    global prev_player, current_player, deployed_pieces, is_removed_piece, num_pieces_deployed, winner

    if not winner:
        # Get the best move for the AI using the alpha-beta pruning algorithm
        ai_prev_move, ai_new_move = minimax_decision(deployed_pieces)
        print(f"AI move piece from {ai_prev_move} to {ai_new_move}")
        apply_move(ai_prev_move, ai_new_move)

        # Check if the piece being moved is in previous_winning_moves
        for win_move in previous_winning_moves[2]:
            if ai_prev_move in win_move:
                previous_winning_moves[current_player].remove(win_move) 

        prev_player = current_player
        current_player = 1
        is_removed_piece = False
    return


def game_over():
    global current_player, deployed_pieces, winning_positions

    for player_pieces in deployed_pieces[current_player]:
        for win_pos in winning_positions:
            if all(piece in player_pieces for piece in win_pos):
                return True

    return False


def evaluate_board(deployed_pieces):
    player_score = 0
    ai_score = 0

    for win_pos in winning_positions:
        if all(pos in deployed_pieces[1] for pos in win_pos):
            player_score += 1
        if all(pos in deployed_pieces[2] for pos in win_pos):
            ai_score += 1

    return player_score - ai_score


def apply_deploy(move):
    global current_player, deployed_pieces, num_pieces_deployed
    deployed_pieces[current_player].append(move)    # current player = 2; AI
    num_pieces_deployed += 1

    
def apply_move(prev_move, new_move):
    global current_player, deployed_pieces, previous_winning_moves
    index = deployed_pieces[2].index(prev_move)

    deployed_pieces[2][index] = new_move


def exclude_mill_pieces(pieces, player):
    global winning_positions
    non_winning_pieces = []

    for piece in pieces:
        if not any(piece in win_pos and all(pos in pieces for pos in win_pos) for win_pos in winning_positions):
            if player == 2:
                non_winning_pieces.append((piece[0]-5, piece[1]-5))
            else:
                non_winning_pieces.append(piece)
    
    if len(non_winning_pieces) == 0:
        return pieces
    return non_winning_pieces 


def check_winner(player):
    global current_player, winning_positions, selected_piece, is_removed_piece, deployed_pieces, all_pieces_deployed, winner, piece_text, num_piece, previous_winning_moves

    if len(deployed_pieces[1]) < 3 and all_pieces_deployed:
        piece_text = font.render(f"AI wins", True, BLACK)
        return True
    elif len(deployed_pieces[2]) < 3 and all_pieces_deployed:
        piece_text = font.render(f"Player wins", True, BLACK)
        return True
    
    if not is_removed_piece:
        for pos in winning_positions:
            if pos not in previous_winning_moves[player]:
                if all(piece in deployed_pieces[player] for piece in pos):
                    piece_text = font.render(f"Select enemies piece to remove", True, BLACK)
                    winner = player
                    if player == 1:
                        if len(deployed_pieces[2]) > 3:
                            selected_piece = exclude_mill_pieces(deployed_pieces[2], 2)
                        else:
                            selected_piece = [(piece[0]-5, piece[1]-5) for piece in deployed_pieces[2]]
                    
                        if pygame.mouse.get_pressed()[0]:
                            mouse_pos = pygame.mouse.get_pos()
                            for piece in selected_piece:
                                adjusted_piece = (piece[0] + 5, piece[1] + 5)
                                if pygame.Rect(adjusted_piece, (50, 50)).collidepoint(mouse_pos):
                                    get_previous_winning_moves(pos, player)
                                    deployed_pieces[2].remove(adjusted_piece)
                                    print(f"Player removed AI piece at {adjusted_piece}")
                                    # Make previous winning move available
                                    for win_move in previous_winning_moves[2]:
                                        if adjusted_piece in win_move:
                                            previous_winning_moves[2].remove(win_move)
                                            
                                    # reset      
                                    winner = None
                                    selected_piece = None
                                    is_removed_piece = True
                                    break
                    else:
                        if deployed_pieces[1]:  # If there are any enemy pieces left
                            selected_enemy_piece = []
                            piece_to_remove = None

                            if len(deployed_pieces[1]) > 3:
                                # Remove that is almost to create mill from the player
                                selected_enemy_piece = exclude_mill_pieces(deployed_pieces[1], 1)
                            else:
                                selected_enemy_piece = [piece for piece in deployed_pieces[1]]
                            piece_to_remove = random.choice(selected_enemy_piece)

                            get_previous_winning_moves(pos, player)
                            deployed_pieces[1].remove(piece_to_remove)

                            # Make previous winning move available
                            for win_move in previous_winning_moves[1]:
                                if piece_to_remove in win_move:
                                    previous_winning_moves[1].remove(win_move)
                            # reset
                            winner = None
                            is_removed_piece = True
                            break 

    if num_pieces_deployed == 12 and not winner:
        piece_text = font.render(f"Move your selected piece", True, BLACK)
    elif num_pieces_deployed < 12 and not winner:
        piece_text = font.render(f"Drop your ({num_piece+1}) piece.", True, BLACK)

    return False


def get_previous_winning_moves(pos, current_player):
    global deployed_pieces, previous_winning_moves

    if all(piece in deployed_pieces[current_player] for piece in pos):
        previous_winning_moves[current_player].append(pos)
    
    return

# MAIN METHOD
if __name__ == "__main__":
    running = True
    status = False

    while running:
        screen.fill(BOARD)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_started = True
                    sleep(0.6)

        if not game_started:
            screen.blit(start_background, (0, 0))
            screen.blit(transparent_surface, (200, 535))
            text = font.render('Start', 1, (184, 166, 153))
            screen.blit(text, (270, 550))
            pygame.display.flip()

        else:
            if status is False:
                screen.fill(BOARD)
                if num_pieces_deployed < 12 and not all_pieces_deployed:
                    if current_player == 1:
                        deploy_piece()
                        sleep(0.1)
                    else:
                        ai_deploy_piece()
                        sleep(0.1)
                else:
                    all_pieces_deployed = True
                    if current_player == 1:
                        move_piece()
                        sleep(0.1)
                    else:
                        ai_move()
                        sleep(0.1)
            
                if prev_player:
                    status = check_winner(prev_player)

            draw_board()
            pygame.display.flip()

            if status:
                break
        
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()





