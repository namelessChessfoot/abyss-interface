#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pygame
from pygame.locals import *
from GameMap import *


class Button():
    def __init__(self, screen, text, x, y, color, enable):
        self.screen = screen
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.button_color = color
        self.text_color = (255, 255, 255)
        self.enable = enable
        self.font = pygame.font.SysFont(None, BUTTON_HEIGHT * 2 // 3)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.topleft = (x, y)
        self.text = text
        self.init_msg()

    def init_msg(self):
        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class StartButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)  # 颜色前浓后淡

    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class GiveupButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(230, 67, 64), (236, 139, 137)], False)

    def click(self, game):
        if self.enable:
            game.is_play = False
            if game.winner is None:
                game.winner = game.map.reverseTurn(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class CommitBotton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(30, 144, 255), (135, 206, 250)], False)

    def click(self, game):
        if self.enable:
            game.player = game.map.reverseTurn(game.player)
            game.playerMoves = 0
            game.map.steps.append(None)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class WithdrawBotton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(255, 165, 0), (255, 228, 181)], False)

    def click(self, game):
        if len(game.map.steps) > 0:
            tmp = game.buttons[2]
            if game.playerMoves == 1:
                game.playerMoves = 0
                tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[1])
                tmp.enable = False
            elif game.playerMoves == 0:
                if len(game.map.steps)!=1:
                    game.playerMoves = 1
                    tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[0])
                    tmp.enable = True
                else:
                    game.firstMove=0
                game.player = game.map.reverseTurn(game.player)
            if game.map.steps[-1] is not None:
                x, y, value = game.map.steps.pop()
                game.map.map[y][x] = 0
            else:
                game.map.steps.pop()
            if len(game.map.steps) > 0:
                self.enable = True
            else:
                self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
                self.enable = False
            return True
        return False


class Game():
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.buttons.append(StartButton(self.screen, 'Start', MAP_WIDTH + 30, 15))
        self.buttons.append(GiveupButton(self.screen, 'Giveup', MAP_WIDTH + 30, BUTTON_HEIGHT + 45))
        self.buttons.append(CommitBotton(self.screen, 'Commit', MAP_WIDTH + 30, 2 * BUTTON_HEIGHT + 75))
        self.buttons.append(WithdrawBotton(self.screen, 'Withdraw', MAP_WIDTH + 30, 3 * BUTTON_HEIGHT + 105))
        self.is_play = False

        self.map = Map(CHESS_LEN, CHESS_LEN)
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.action = None
        self.winner = None
        self.playerMoves = None
        self.firstMove = None

    def start(self):  # 开始游戏
        self.is_play = True
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.playerMoves = 0
        self.map.reset()
        self.firstMove = 0

    def play(self):  # 进行游戏
        self.clock.tick(60)

        light_yellow = (247, 238, 214)
        pygame.draw.rect(self.screen, light_yellow, pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(MAP_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))

        for button in self.buttons:  # 把所有button画出来
            button.draw()

        if self.is_play and not self.isOver():  # 如果正在进行且没有结束
            if self.action is not None:  # action 放的是鼠标点击位置的像素坐标，非空表示鼠标刚刚在棋盘内点击了
                self.checkClick(self.action[0], self.action[1])  # 调用checkClick以调用map类中的click函数实现落子
                self.action = None

            if not self.isOver():  # 没结束就执行鼠标设置函数
                self.changeMouseShow()

        if self.isOver():  # 结束了就显示赢家
            self.showWinner()

        self.map.drawBackground(self.screen)
        self.map.drawChess(self.screen)

    def changeMouseShow(self):  # 设置棋盘内可落子位置处鼠标不可见并显示大圆点；其他位置设置鼠标可见
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            light_black, light_white = (67, 67, 67), (255, 131, 250)
            pos, radius = (map_x, map_y), CHESS_RADIUS
            if self.player == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                pygame.draw.circle(self.screen, light_black, pos, radius)
            elif self.player == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:
                pygame.draw.circle(self.screen, light_white, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    def checkClick(self, x, y, isAI=False):
        self.map.click(x, y, self.player)  # 实现落子
        self.playerMoves += 1
        if len(self.map.steps) > 0:
            tmp = self.buttons[3]
            tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[0])
            tmp.enable = True
        else:
            tmp = self.buttons[3]
            tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[1])
            tmp.enable = False

        if self.firstMove is not None:
            self.firstMove = None
            self.player = self.map.reverseTurn(self.player)
            self.playerMoves = 0
            tmp = self.buttons[2]
            tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[1])
            tmp.enable = False

        if self.find_winner(x, y):
            self.player = self.map.reverseTurn(self.player)
            self.click_button(self.buttons[1])
            return

        if self.playerMoves == 1:
            self.buttons[2].unclick()
        elif self.playerMoves == 2:
            self.player = self.map.reverseTurn(self.player)
            self.playerMoves = 0
            tmp = self.buttons[2]
            tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[1])
            tmp.enable = False

    def mouseClick(self, map_x, map_y):  # 将鼠标点击位置转换为棋盘坐标，再赋给 action
        if self.is_play and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)

    def isOver(self):  # 返回游戏是否结束，等价于是否产生赢家
        return self.winner is not None

    def showWinner(self):  # 展示赢家是哪一方
        def showFont(screen, text, location_x, locaiton_y, height):
            font = pygame.font.SysFont(None, height)
            font_image = font.render(text, True, (0, 0, 255), (255, 255, 255))
            font_image_rect = font_image.get_rect()
            font_image_rect.x = location_x
            font_image_rect.y = locaiton_y
            screen.blit(font_image, font_image_rect)

        if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            str = 'Winner is Black'
        else:
            str = 'Winner is White'
        showFont(self.screen, str, MAP_WIDTH + 25, SCREEN_HEIGHT - 60, 30)
        pygame.mouse.set_visible(True)

    def click_button(self, button):  # click 该 button 并设置 START 和 GIVEUP 只有一个可以点击
        button.click(self)
        if button == self.buttons[0]:
            self.buttons[1].unclick()
        elif button == self.buttons[1]:
            self.buttons[0].unclick()
            for tmp in self.buttons[2:4]:
                tmp.msg_image = tmp.font.render(tmp.text, True, tmp.text_color, tmp.button_color[1])
                tmp.enable = False

    def check_buttons(self, mouse_x, mouse_y):  #
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break

    def find_winner(self, x, y):
        dircount = [0 for i in range(0, 8)]
        x0, y0, x1, y1 = max(x - 5, 0), max(y - 5, 0), min(x + 5, CHESS_LEN - 1), min(y + 5, CHESS_LEN - 1)
        xx, yy = x - 1, y
        while xx >= x0:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[0] += 1
                xx -= 1
            else:
                break
        xx, yy = x - 1, y + 1
        while xx >= x0 and yy <= y1:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[1] += 1
                xx -= 1
                yy += 1
            else:
                break
        xx, yy = x, y + 1
        while yy <= y1:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[2] += 1
                yy += 1
            else:
                break
        xx, yy = x + 1, y + 1
        while xx <= x1 and yy <= y1:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[3] += 1
                xx += 1
                yy += 1
            else:
                break
        xx, yy = x + 1, y
        while xx <= x1:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[4] += 1
                xx += 1
            else:
                break
        xx, yy = x + 1, y - 1
        while xx <= x1 and yy >= y0:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[5] += 1
                xx += 1
                yy -= 1
            else:
                break
        xx, yy = x, y - 1
        while yy >= y0:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[6] += 1
                yy -= 1
            else:
                break
        xx, yy = x - 1, y - 1
        while xx >= x0 and yy >= y0:
            if game.map.map[yy][xx] == game.map.map[y][x]:
                dircount[7] += 1
                xx -= 1
                yy -= 1
            else:
                break
        for i in range(0, 4):
            if dircount[i] + dircount[i + 4] >= 5:
                return True
        return False


game = Game("Abyss " + GAME_VERSION)
while True:
    game.play()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            game.mouseClick(mouse_x, mouse_y)
            game.check_buttons(mouse_x, mouse_y)
