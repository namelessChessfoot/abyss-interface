from enum import IntEnum
import pygame
from pygame.locals import *

GAME_VERSION = 'V1.0'

REC_SIZE = 40
CHESS_RADIUS = REC_SIZE // 2
CHESS_LEN = 9
MAP_WIDTH = CHESS_LEN * REC_SIZE
MAP_HEIGHT = CHESS_LEN * REC_SIZE

INFO_WIDTH = 200
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 50

SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT


class MAP_ENTRY_TYPE(IntEnum):
    MAP_EMPTY = 0,
    MAP_PLAYER_ONE = 1,  # 黑色，先手
    MAP_PLAYER_TWO = 2,  # 白色，后手
    MAP_NONE = 3,  # out of map range


class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]  # 记录[y][x]位置是黑(2)下还是白(1)下，或是其他
        self.steps = []  # 记录双方落子情况

    def reset(self):  # 清空棋盘和落子列表
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []
        self.dirCount = [ 0 for i in range(0,8)]

    def reverseTurn(self, turn):  # 换对方落子
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            return MAP_ENTRY_TYPE.MAP_PLAYER_ONE

    def getMapUnitRect(self, x, y):  # 将坐标(x,y)转换为像素位置(map_x,map_y)
        map_x = x * REC_SIZE
        map_y = y * REC_SIZE

        return (map_x, map_y, REC_SIZE, REC_SIZE)

    def MapPosToIndex(self, map_x, map_y):  # 将像素位置(map_x,map_y)转换为坐标(x,y)
        x = map_x // REC_SIZE
        y = map_y // REC_SIZE
        return (x, y)

    def isInMap(self, map_x, map_y):  # 判断像素位置(map_x,map_y)是否超出边界
        if (map_x <= 0 or map_x >= MAP_WIDTH or
                map_y <= 0 or map_y >= MAP_HEIGHT):
            return False
        return True

    def isEmpty(self, x, y):  # 判断[y][x]位置是否为空
        return self.map[y][x] == 0

    def click(self, x, y, type):  # type为落子方，此函数为棋盘落子函数
        if type is None:
            self.steps.append(None)
            return
        self.map[y][x] = type.value
        self.steps.append((x, y, type.value))

    def drawChess(self, screen):  # 在棋盘上画棋子
        player_one = (88, 87, 86)
        player_two = (255, 251, 240)
        player_color = [player_one, player_two]

        font = pygame.font.SysFont(None, REC_SIZE * 2 // 3)
        for i in range(len(self.steps)):
            if self.steps[i] is not None:
                x, y = self.steps[i][0], self.steps[i][1]
                map_x, map_y, width, height = self.getMapUnitRect(x, y)
                pos, radius = (map_x + width // 2, map_y + height // 2), CHESS_RADIUS
                turn = self.map[y][x]
                if turn == 1:
                    op_turn = 2
                else:
                    op_turn = 1
                pygame.draw.circle(screen, player_color[turn - 1], pos, radius)

                msg_image = font.render(str(i), True, player_color[op_turn - 1], player_color[turn - 1])
                msg_image_rect = msg_image.get_rect()
                msg_image_rect.center = pos
                screen.blit(msg_image, msg_image_rect)

        if len(self.steps) > 0 and self.steps[-1] is not None:         # 为最后的落子画方框
            last_pos = self.steps[-1][0:2]
            map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
            red_color = (204, 0, 0)
            point_list = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, red_color, True, point_list, 1)
            if len(self.steps) > 1 and (self.steps[-2] is not None) and self.steps[-1][2]==self.steps[-2][2]:
                last_sec_pos=self.steps[-2][0:2]
                map_x, map_y, width, height = self.getMapUnitRect(last_sec_pos[0], last_sec_pos[1])
                light_red_color = (255, 153, 153)
                point_list = [(map_x, map_y), (map_x + width, map_y),
                              (map_x + width, map_y + height), (map_x, map_y + height)]
                pygame.draw.lines(screen, light_red_color, True, point_list, 1)
        elif len(self.steps) > 1 and self.steps[-1] is None and self.steps[-2] is not None:
            last_pos = self.steps[-2][0:2]
            map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
            red_color = (204, 0, 0)
            point_list = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, red_color, True, point_list, 1)

    def drawBackground(self, screen):    # 画背景
        color = (0, 0, 0)
        for y in range(self.height):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y), (
                MAP_WIDTH - REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y)
            if y == (self.height) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)

        for x in range(self.width):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2 + REC_SIZE * x, REC_SIZE // 2), (
                REC_SIZE // 2 + REC_SIZE * x, MAP_HEIGHT - REC_SIZE // 2)
            if x == (self.width) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)

        rec_size = 8
        temp1 = CHESS_LEN // 2
        temp2 = (CHESS_LEN // 2) // 2
        pos = [(temp2, temp2), (2 * temp1 - temp2, temp2), (temp2, 2 * temp1 - temp2),
               (2 * temp1 - temp2, 2 * temp1 - temp2), (temp1, temp1)]
        for (x, y) in pos:
            pygame.draw.rect(screen, color, (
                REC_SIZE // 2 + x * REC_SIZE - rec_size // 2, REC_SIZE // 2 + y * REC_SIZE - rec_size // 2, rec_size,
                rec_size))
