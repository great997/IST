import tkinter as tk
import random
import tkinter.messagebox as messagebox
import time

BOARD_SIZE = 8
SQUARE_SIZE = 60
window = tk.Tk()
window.withdraw()
menu = tk.Menu(window)

board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
selected_piece = None
ai_difficulty = "Easy"
game_over = False
PLAYER_COLOR = "white"
AI_COLOR = "black"
PLAYER_KING_COLOR = "pink"
AI_KING_COLOR = "red"


NORMAL_VALUE = 10  # 普通棋子的价值
KING_VALUE = 20  # 升王棋子的价值
EDGE_VALUE = 5  # 边缘棋子的价值
CENTER_VALUE = 3  # 中心棋子的价值



# 画出棋盘
def draw_board():
    # 清空画布
    canvas.delete("all")

    # 画出棋盘的方格
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 根据行列号计算方格的坐标
            x1 = col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE

            # 如果方格是黑色，就用灰色填充
            if (row + col) % 2 == 0:
                canvas.create_rectangle(x1, y1, x2, y2, fill="gray")

            # 如果方格有棋子，就画出棋子的颜色和形状
            if board[row][col] is not None:
                # 根据棋子的颜色，画出一个圆形
                if board[row][col] == PLAYER_COLOR:
                    canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
                elif board[row][col] == AI_COLOR:
                    canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                elif board[row][col] == PLAYER_KING_COLOR:
                    canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="pink")
                elif board[row][col] == AI_KING_COLOR:
                    canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="red")

                # 如果棋子是升王的，就在圆形上画一个差不多的星形
                if board[row][col] in (PLAYER_KING_COLOR, AI_KING_COLOR):
                    canvas.create_polygon(x1 + 30, y1 + 10, x1 + 20, y1 + 20, x1 + 10, y1 + 10,
                                          x1 + 15, y1 + 30, x1 + 5, y1 + 40, x1 + 30, y1 + 35,
                                          x1 + 55, y1 + 40, x1 + 45, y1 + 30, x1 + 50, y1 + 10,
                                          x1 + 30, y1 + 15, fill="yellow")

            # 如果方格是选中的棋子或者合法的走法，就用红色的边框标记出来
            if selected_piece is not None and (row, col) in get_valid_moves(board, selected_piece[0],
                                                                            selected_piece[1]):
                canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="red", width=4)

    # 更新画布
    canvas.update()

def is_valid_move(board, row1, col1, row2, col2):
    color = board[row1][col1]

    # 定义一个列表，用来存储对方的所有可能的棋子颜色
    opponent_colors = []
    if color == PLAYER_COLOR or color == PLAYER_KING_COLOR:
        opponent_colors = [AI_COLOR, AI_KING_COLOR]
    elif color == AI_COLOR or color == AI_KING_COLOR:
        opponent_colors = [PLAYER_COLOR, PLAYER_KING_COLOR]
    # 如果目标位置不在棋盘范围内，或者不为空，就返回False
    if not (0 <= row2 < BOARD_SIZE and 0 <= col2 < BOARD_SIZE) or board[row2][col2] != None:
        return False
    # 如果目标位置和起始位置的行差的绝对值为1，表示是普通移动
    if abs(row2 - row1) == 1:
        # 如果棋子是国王，就可以在任意方向移动一格
        if color == PLAYER_KING_COLOR or color == AI_KING_COLOR:
            # 如果目标位置是对方的棋子，就返回False
            if board[row2][col2] in opponent_colors:
                return False
            else:
                return True
        # 如果棋子是玩家的普通棋子，就只能向上移动一格
        elif color == PLAYER_COLOR and row2 < row1:
            # 如果目标位置是对方的棋子，就返回False
            if board[row2][col2] in opponent_colors:
                return False
            else:
                return True
        # 如果棋子是AI的普通棋子，就只能向下移动一格
        elif color == AI_COLOR and row2 > row1:
            # 如果目标位置是对方的棋子，就返回False
            if board[row2][col2] in opponent_colors:
                return False
            else:
                return True

    # 如果目标位置和起始位置的行差的绝对值为2，表示是跳跃移动
    elif abs(row2 - row1) == 2:
        # 计算跳跃的中间位置的行列号
        row3 = (row1 + row2) // 2
        col3 = (col1 + col2) // 2

        # 如果中间位置有对方的棋子，就可以跳过它
        if board[row3][col3] != None and board[row3][col3] in opponent_colors:
            return True

        # 如果中间位置有自己的棋子，就不能跳过它
        # 定义一个列表，用来存储自己的所有可能的棋子颜色
        own_colors = [color, color.upper()]
        if color == PLAYER_COLOR or color == PLAYER_KING_COLOR:
            own_colors.append(PLAYER_KING_COLOR)
        elif color == AI_COLOR or color == AI_KING_COLOR:
            own_colors.append(AI_KING_COLOR)

        if board[row3][col3] != None and board[row3][col3] in own_colors:
            return False

    # 其他情况都返回False
    return False


# 返回一个棋子的所有合法走法，参数是棋盘，行号和列号
def get_valid_moves(board, row, col):
    color = board[row][col]
    # 初始化一个空列表，用来存储有效移动
    moves = []

    # 如果棋子是国王，就可以在任意方向移动或跳跃
    if color == PLAYER_KING_COLOR or color == AI_KING_COLOR:
        for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            # 普通移动
            if is_valid_move(board, row, col, row + direction[0], col + direction[1]):
                moves.append((row + direction[0], col + direction[1]))
            # 跳跃移动
            if is_valid_move(board, row, col, row + 2 * direction[0], col + 2 * direction[1]):
                moves.append((row + 2 * direction[0], col + 2 * direction[1]))

    # 如果棋子是玩家的普通棋子，就只能向上移动或跳跃
    elif color == PLAYER_COLOR:
        for direction in [(-1, -1), (-1, 1)]:
            # 普通移动
            if is_valid_move(board, row, col, row + direction[0], col + direction[1]):
                moves.append((row + direction[0], col + direction[1]))
            # 跳跃移动
            if is_valid_move(board, row, col, row + 2 * direction[0], col + 2 * direction[1]):
                moves.append((row + 2 * direction[0], col + 2 * direction[1]))

    # 如果棋子是AI的普通棋子，就只能向下移动或跳跃
    elif color == AI_COLOR:
        for direction in [(1, -1), (1, 1)]:
            # 普通移动
            if is_valid_move(board, row, col, row + direction[0], col + direction[1]):
                moves.append((row + direction[0], col + direction[1]))
            # 跳跃移动
            if is_valid_move(board, row, col, row + 2 * direction[0], col + 2 * direction[1]):
                moves.append((row + 2 * direction[0], col + 2 * direction[1]))

    # 返回有效移动的列表
    return moves

def can_jump(row, col):
    # 判断一个棋子是否有跳过的机会
    piece = board[row][col]

    if piece is None:
        return False

    for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        move_row = row + direction[0]
        move_col = col + direction[1]
        jump_row = row + 2 * direction[0]
        jump_col = col + 2 * direction[1]

        if is_on_board(jump_row, jump_col) and board[jump_row][jump_col] is None:
            # 如果跳过后的格子是空的
            if piece == PLAYER_COLOR or piece == "white king":
                # 如果是玩家的棋子，只能向前跳过
                if move_row < row and board[move_row][move_col] in [AI_COLOR, "black king"]:
                    return True

            elif piece == AI_COLOR or piece == "black king":
                # 如果是电脑的棋子，只能向后跳过
                if move_row > row and board[move_row][move_col] in [PLAYER_COLOR, "white king"]:
                    return True

    return False


def is_on_board(row, col):
    # 判断一个坐标是否在棋盘上
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def make_king(row, col):
    # 判断一个棋子是否可以升王，并更新它的状态
    piece = board[row][col]

    if piece is None:
        return False

    if piece == PLAYER_COLOR and row == 0:
        board[row][col] = "white king"
        return True

    elif piece == AI_COLOR and row == BOARD_SIZE - 1:
        board[row][col] = "black king"
        return True

    else:
        return False


# 移动棋子，参数是起始位置和目标位置
def make_move(board, row1, col1, row2, col2, is_crowning=False):
    # 获取棋子的颜色
    color = board[row1][col1] # 这里用row1和col1作为索引
    # 如果目标位置和起始位置的行差的绝对值大于1，表示是跳跃移动，就要吃掉对方的棋子
    if abs(row2 - row1) > 1:
        # 计算被吃掉的棋子的位置
        row3 = (row1 + row2) // 2
        col3 = (col1 + col2) // 2

        # 如果被吃棋子是否为王时，将当前棋子变为王
        if board[row3][col3] == PLAYER_KING_COLOR or board[row3][col3] == AI_KING_COLOR:
            # 如果被吃棋子是王，则将当前棋子也变为王
            board[row2][col2] = PLAYER_KING_COLOR if color == PLAYER_COLOR else AI_KING_COLOR
        else:
            # 如果被吃棋子不是王，则按照原来的逻辑判断是否升为国王
            # 把起始位置的棋子移动到目标位置
            board[row2][col2] = board[row1][col1]

        # 把被吃掉的棋子从棋盘上移除
        board[row3][col3] = None

    else:
        # 如果不是跳跃移动，就直接把起始位置的棋子移动到目标位置
        board[row2][col2] = board[row1][col1]

    # 如果棋子移动到了对方的底线，就升为国王
    if color == PLAYER_COLOR and row2 == 0:
        board[row2][col2] = PLAYER_KING_COLOR
    elif color == AI_COLOR and row2 == BOARD_SIZE - 1:
        board[row2][col2] = AI_KING_COLOR

    # 把起始位置置为空
    board[row1][col1] = None

    if is_crowning:
        return board

    return board

# 返回所有可能的走法，参数是棋盘和颜色
def get_all_moves(board, color):
    # 初始化一个空列表，用来存储走法
    moves = []

    # 遍历棋盘，找到指定颜色的棋子
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == color or board[row][col] == color.upper():
                # 调用get_valid_moves函数，获取该棋子的所有合法走法
                valid_moves = get_valid_moves(board, row, col)

                # 把走法添加到列表中，每个走法包含起始位置和目标位置
                moves.extend([(row, col, move[0], move[1]) for move in valid_moves])

    # 返回所有走法的列表
    return moves


def evaluate(board, color):
    # 初始化一个变量，用来存储评估值
    value = 0

    # 遍历棋盘上的每个格子
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 如果格子有棋子
            if board[row][col] is not None:
                # 获取棋子的颜色
                piece_color = board[row][col]

                # 如果棋子是玩家的国王，就给评估值加上7
                if piece_color == PLAYER_KING_COLOR:
                    value += 7
                # 如果棋子是AI的国王，就给评估值减去7
                elif piece_color == AI_KING_COLOR:
                    value -= 7
                # 如果棋子是玩家的普通棋子，就给评估值加上1
                elif piece_color == PLAYER_COLOR:
                    value += 1
                # 如果棋子是AI的普通棋子，就给评估值减去1
                elif piece_color == AI_COLOR:
                    value -= 1

    # 返回评估值
    return value

# 复制一个棋盘，返回一个新的棋盘
def deep_copy(obj):
    # 如果对象是一个列表
    if isinstance(obj, list):
        # 初始化一个空列表，用来存储新的列表
        new_list = []
        # 遍历原来的列表，递归地复制每个元素，并添加到新的列表中
        for item in obj:
            new_list.append(deep_copy(item))
        # 返回新的列表
        return new_list
    # 如果对象是其他类型，就直接返回对象本身
    else:
        return obj

# Alpha-Beta剪枝算法，搜索最优走法，并返回最优评分和走法
# 使用Alpha-Beta剪枝算法搜索最佳走法，参数是棋盘，搜索深度，alpha值，beta值，和是否是最大化玩家
def alpha_beta_search(board, depth, alpha, beta, is_ai_turn):
    # 如果游戏结束或者搜索深度为0，就返回评估值和空走法
    if is_game_over() or depth == 0:
        return evaluate(board, AI_COLOR), None
    # 如果是AI的回合，就尝试最大化评估值
    # 如果AI没有有效的走法，就返回一个很小的评估值，表示AI输了
    if is_ai_turn and not get_all_moves(board, AI_COLOR):
        return -float('inf'), None

    # 如果玩家没有有效的走法，就返回一个很大的评估值，表示AI赢了
    if not is_ai_turn and not get_all_moves(board, PLAYER_COLOR):
        return float('inf'), None

    # 如果是AI的回合，就尝试最大化评估值
    if is_ai_turn:
        # 初始化最大评估值为负无穷
        max_value = -float('inf')
        # 初始化最佳走法为None
        best_move = None

        # 遍历棋盘上的每个格子
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] in (AI_COLOR, AI_KING_COLOR):
                    # 获取棋子的有效移动
                    moves = get_valid_moves(board, row, col)

                    # 检查AI是否有必须跳过对方棋子的情况
                    must_jump = False
                    for r in range(BOARD_SIZE):
                        for c in range(BOARD_SIZE):
                            if board[r][c] in (AI_COLOR, AI_KING_COLOR):
                                moves2 = get_valid_moves(board, r, c)
                                for move2 in moves2:
                                    if abs(move2[0] - r) > 1:
                                        must_jump = True
                                        break

                    # 如果有，就只考虑可以跳过对方棋子的走法
                    if must_jump:
                        moves = [move for move in moves if abs(move[0] - row) > 1]

                    # 遍历每个有效移动
                    for move in moves:
                        # 复制一个新的棋盘，并模拟走法
                        new_board = deep_copy(board)
                        make_move(new_board, row, col, move[0], move[1])

                        # 递归调用alpha_beta_search函数，获取下一层的评估值和走法
                        value, _ = alpha_beta_search(new_board, depth - 1, alpha, beta, False)

                        # 如果评估值大于最大评估值，就更新最大评估值和最佳走法
                        if value > max_value:
                            max_value = value
                            best_move = (row, col, move[0], move[1])

                        # 如果评估值大于等于beta值，就剪枝并返回最大评估值和最佳走法
                        if value >= beta:
                            return max_value, best_move

                        # 如果评估值大于alpha值，就更新alpha值
                        if value > alpha:
                            alpha = value

        # 返回最大评估值和最佳走法
        return max_value, best_move

    # 如果是玩家的回合，就尝试最小化评估值
    else:
        # 初始化最小评估值为正无穷
        min_value = float('inf')
        # 初始化最佳走法为None
        best_move = None

        # 遍历棋盘上的每个格子
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # 如果格子有玩家的棋子
                if board[row][col] in (PLAYER_COLOR, PLAYER_KING_COLOR):
                    # 获取棋子的有效移动
                    moves = get_valid_moves(board, row, col)

                    # 检查玩家是否有必须跳过对方棋子的情况
                    must_jump = False
                    for r in range(BOARD_SIZE):
                        for c in range(BOARD_SIZE):
                            if board[r][c] in (PLAYER_COLOR, PLAYER_KING_COLOR):
                                moves2 = get_valid_moves(board, r, c)
                                for move2 in moves2:
                                    if abs(move2[0] - r) > 1:
                                        must_jump = True
                                        break

                    # 如果有，就只考虑可以跳过对方棋子的走法
                    if must_jump:
                        moves = [move for move in moves if abs(move[0] - row) > 1]

                    # 遍历每个有效移动
                    for move in moves:
                        # 复制一个新的棋盘，并模拟走法
                        new_board = deep_copy(board)
                        make_move(new_board, row, col, move[0], move[1])

                        # 递归调用alpha_beta_search函数，获取下一层的评估值和走法
                        value, _ = alpha_beta_search(new_board, depth - 1, alpha, beta, True)

                        # 如果评估值小于最小评估值，就更新最小评估值和最佳走法
                        if value < min_value:
                            min_value = value
                            best_move = (row, col, move[0], move[1])

                        # 如果评估值小于等于alpha值，就剪枝并返回最小评估值和最佳走法
                        if value <= alpha:
                            return min_value, best_move

                        # 如果评估值小于beta值，就更新beta值
                        if value < beta:
                            beta = value

        # 返回最小评估值和最佳走法
        return min_value, best_move


# AI移动，根据ai_difficulty的值来调用不同的搜索算法
def ai_move():
    time.sleep(0.1)
    best_move = None

    # 获取AI移动后的行列号和是否升王
    row = None
    col = None
    is_king = False

    # 如果ai_difficulty是简单，就随机选择一个走法
    if ai_difficulty == "Easy":
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == AI_COLOR:
                    valid_moves = get_valid_moves(board, row, col)
                    moves.extend([(row, col, move[0], move[1]) for move in valid_moves])
        if moves:
            # 检查所有可能的移动，以确定是否有必吃的情况
            must_jump = any(abs(move[0] - move[2]) > 1 for move in moves)
            if must_jump:
                moves = [move for move in moves if abs(move[0] - move[2]) > 1]
            random_move = random.choice(moves)
            make_move(board, random_move[0], random_move[1], random_move[2], random_move[3])
            draw_board()

    elif ai_difficulty == "Medium":
        _, best_move = alpha_beta_search(board, 2, -float('inf'), float('inf'), True)
        if best_move:
            make_move(board, best_move[0], best_move[1], best_move[2], best_move[3])
            draw_board()

    elif ai_difficulty == "Hard":
        _, best_move = alpha_beta_search(board, 4, -float('inf'), float('inf'), True)
        if best_move:
            make_move(board, best_move[0], best_move[1], best_move[2], best_move[3])
            draw_board()

    if best_move:
        row = best_move[2]
        col = best_move[3]
        is_king = make_king(row, col)

    while not is_king and can_jump(row, col):
        _, best_move = alpha_beta_search(board, 4, -float('inf'), float('inf'), True)
        if best_move:
            make_move(board, best_move[0], best_move[1], best_move[2], best_move[3], is_king)
            draw_board()
            row = best_move[2]
            col = best_move[3]
            is_king = make_king(row, col)

    if is_game_over():
        show_game_over_message()
        return True

    return False



def set_difficulty(difficulty):
    # 设置AI难度
    global ai_difficulty
    ai_difficulty = difficulty


# 定义一个变量，用来存储当前选中的棋子的有效移动
valid_moves = []


# 处理鼠标点击事件
def handle_click(event):
    # 获取鼠标点击的位置
    x = event.x
    y = event.y

    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE

    # 使用global关键字，声明要使用全局变量
    global selected_piece
    global valid_moves

    # 检查game_over是否为True，如果是，就直接返回
    if game_over:
        return
    # 如果鼠标点击的位置不在棋盘上，就直接返回
    if not is_on_board(row, col):
        return

    # 如果没有选中棋子，就尝试选中一个玩家的棋子
    if selected_piece is None:
        # 如果方格有玩家的棋子，就选中它，并获取它的有效移动
        if board[row][col] in (PLAYER_COLOR, PLAYER_KING_COLOR):
            selected_piece = (row, col)
            valid_moves = get_valid_moves(board, row, col)  # 获取有效移动

            # 检查玩家是否有必须跳过对方棋子的情况
            must_jump = False
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board[r][c] in (PLAYER_COLOR, PLAYER_KING_COLOR):
                        moves = get_valid_moves(board, r, c)
                        for move in moves:
                            if abs(move[0] - r) > 1:
                                must_jump = True
                                break

            # 如果有，就只允许玩家选择可以跳过对方棋子的走法，并弹出提示信息
            if must_jump:
                valid_moves = [move for move in valid_moves if abs(move[0] - row) > 1]


    # 如果已经选中棋子，就尝试移动它
    else:
        # 如果方格是有效的移动目标，就移动棋子，并取消选中
        if (row, col) in valid_moves:
            is_king = make_move(board, selected_piece[0], selected_piece[1], row, col)
            draw_board()

            # 检查玩家是否可以继续跳跃，如果可以，就不要让AI移动，而是让玩家继续选择目标位置
            # 只有当移动的距离大于1时，才表示吃掉了对方的棋子，才需要判断是否能继续跳跃
            if not is_king and abs(row - selected_piece[0]) > 1 and can_jump(row, col):
                selected_piece = (row, col)
                valid_moves = get_valid_moves(board, row, col)
                valid_moves = [move for move in valid_moves if abs(move[0] - row) > 1]
                tk.messagebox.showinfo("提示", "你可以继续跳跃。")
            else:
                selected_piece = None
                # 让AI移动
                ai_move()


        # 如果方格是另一个玩家的棋子，就取消之前的选中，并选中这个棋子
        elif board[row][col] in (PLAYER_COLOR, PLAYER_KING_COLOR):
            selected_piece = (row, col)
            valid_moves = get_valid_moves(board, row, col)  # 获取有效移动

            # 检查玩家是否有必须跳过对方棋子的情况
            must_jump = False
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board[r][c] in (PLAYER_COLOR, PLAYER_KING_COLOR):
                        moves = get_valid_moves(board, r, c)
                        for move in moves:
                            if abs(move[0] - r) > 1:
                                must_jump = True
                                break

            # 如果有，就只允许玩家选择可以跳过对方棋子的走法，并弹出提示信息
            if must_jump:
                valid_moves = [move for move in valid_moves if abs(move[0] - row) > 1]
                tk.messagebox.showinfo("提示", "有必吃，请移动该棋子。")

        # 如果方格是其他情况，就取消选中
        else:
            selected_piece = None

    # 重新画出棋盘
    draw_board()


# 判断游戏是否结束，返回True或False
def is_game_over():
    # 初始化两个变量，用来存储玩家和AI的棋子数量
    player_pieces = 0
    ai_pieces = 0

    # 遍历棋盘，统计棋子数量
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 如果是玩家的棋子，就增加玩家的棋子数量
            if board[row][col] in (PLAYER_COLOR, PLAYER_KING_COLOR):
                player_pieces += 1

            # 如果是AI的棋子，就增加AI的棋子数量
            elif board[row][col] in (AI_COLOR, AI_KING_COLOR):
                ai_pieces += 1

    # 如果玩家或者AI的棋子数量为0，就返回True，表示游戏结束
    if player_pieces == 0 or ai_pieces == 0:
        return True

    # 如果玩家或者AI没有有效的走法，就返回True，表示游戏结束
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 如果是玩家的棋子，并且有有效的走法，就返回False，表示游戏未结束
            if board[row][col] in (PLAYER_COLOR, PLAYER_KING_COLOR) and get_valid_moves(board, row, col):
                return False

            # 如果是AI的棋子，并且有有效的走法，就返回False，表示游戏未结束
            elif board[row][col] in (AI_COLOR, AI_KING_COLOR) and get_valid_moves(board, row, col):
                return False

    # 如果一方棋子设法抓住了对方的国王，它会立即加冕为国王，随后游戏结束
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 如果是玩家的普通棋子，并且可以跳过对方的国王，就返回True，表示游戏结束
            if board[row][col] == PLAYER_COLOR and is_valid_move(board, row, col, row - 2, col - 2) and board[row - 1][
                col - 1] == AI_KING_COLOR:
                return True
            if board[row][col] == PLAYER_COLOR and is_valid_move(board, row, col, row - 2, col + 2) and board[row - 1][
                col + 1] == AI_KING_COLOR:
                return True

            # 如果是AI的普通棋子，并且可以跳过对方的国王，就返回True，表示游戏结束
            if board[row][col] == AI_COLOR and is_valid_move(board, row, col, row + 2, col - 2) and board[row + 1][
                col - 1] == PLAYER_KING_COLOR:
                return True
            if board[row][col] == AI_COLOR and is_valid_move(board, row, col, row + 2, col + 2) and board[row + 1][
                col + 1] == PLAYER_KING_COLOR:
                return True

    # 如果以上都不满足，就返回True，表示游戏结束
    return True


def show_rules():
    # 显示规则说明
    tk.messagebox.showinfo("规则说明", "这是一个国际64格跳棋游戏。\n"
                                   "游戏规则如下：\n"
                                   "1. 每人用一种颜色棋子占一个角。\n"
                                   "2. 棋子可以在有直线连接的相邻六个方向移动或跳过其他棋子。\n"
                                   "3. 谁先把正对面的阵地全部占领，谁就取得胜利。\n"
                                   "4. 如果一方棋子设法抓住了对方的国王，它会立即加冕为国王，随后游戏结束。\n"
                                   "5. 国王是在自己的棋子到达对面的最后一行时才产生的。\n"
                                   "6. 国王可以在任意方向移动或跳过其他棋子。\n"
                                   "祝你玩得开心！")


def restart_game():
    # 使用global关键字，声明要使用全局变量
    global board
    global game_over
    # 重置棋盘状态
    board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    for row in range(3):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = AI_COLOR

    for row in range(5, BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = PLAYER_COLOR

    # 设置game_over为False
    game_over = False

    # 重新绘制棋盘
    draw_board()

    # 清除游戏结束信息
    canvas.delete("all")


def show_game_over_message():
    # 显示游戏结束信息
    player_pieces = 0
    ai_pieces = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER_COLOR or board[row][col] == 'white king':
                player_pieces += 1
            elif board[row][col] == AI_COLOR or board[row][col] == 'black king':
                ai_pieces += 1

    if player_pieces == 0:
        message = 'AI赢了!'
    else:
        message = '你赢了!'

    canvas.create_text(BOARD_SIZE * SQUARE_SIZE / 2, BOARD_SIZE * SQUARE_SIZE / 2, text=message, fill='red',
                       font=('Arial', 24))
    window.quit()  # 终止主循环
    window.deiconify()
    window.mainloop()

    # 设置game_over为True
    global game_over
    game_over = True

    canvas.create_text(BOARD_SIZE * SQUARE_SIZE / 2, BOARD_SIZE * SQUARE_SIZE / 2, text=message, fill='red',
                       font=('Arial', 24))
    window.quit()  # 终止主循环
    window.deiconify()
    window.mainloop()


window = tk.Tk()
window.title("Checkers")

canvas = tk.Canvas(window, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
canvas.pack()

# 初始化棋盘状态
for row in range(3):
    for col in range(BOARD_SIZE):
        if (row + col) % 2 == 1:
            board[row][col] = AI_COLOR

for row in range(5, BOARD_SIZE):
    for col in range(BOARD_SIZE):
        if (row + col) % 2 == 1:
            board[row][col] = PLAYER_COLOR

# 绑定事件
canvas.bind("<Button-1>", handle_click)

# 显示菜单
menu = tk.Menu(window)
window.config(menu=menu)

difficulty_menu = tk.Menu(menu)
# 添加菜单项
rules_menu = tk.Menu(menu)

menu.add_cascade(label="规则说明", menu=rules_menu)
rules_menu.add_command(label="查看规则", command=show_rules)

menu.add_cascade(label="难度选择", menu=difficulty_menu)
difficulty_menu.add_command(label="简单", command=lambda: set_difficulty("Easy"))
difficulty_menu.add_command(label="中等", command=lambda: set_difficulty("Medium"))
difficulty_menu.add_command(label="困难", command=lambda: set_difficulty("Hard"))
menu.add_command(label="重开游戏", command=restart_game)

# 绘制棋盘
draw_board()

window.mainloop()