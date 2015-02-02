#!/usr/bin/python
# Copyright (c) 2014 Daniel Loman

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
#    subject to the following conditions:

#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.

#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import pygame
import time
from pygame.locals import *
from random import randint
import requests

###############################################################################
SNAKE_COLOR = (0, 160, 190)
FOOD_COLOR = (240, 170, 0)
UI_COLOR = (0, 60, 120)
BG_COLOR = (255, 255, 255)
###############################################################################

###############################################################################
###############################################################################


class Snake():

    def __init__(self):
        pygame.init()
        self.mFrameRate = 10
        self.mLineThickness = 10
        self.mWindowWidth = 800
        self.mWindowHeight = 700
        self.mFont = pygame.font.Font('freesansbold.ttf', 20)
        self.mBigFont = pygame.font.Font('freesansbold.ttf', 40)
        self.mDisplay = \
            pygame.display.set_mode((self.mWindowWidth, self.mWindowHeight))
        self.mClock = pygame.time.Clock()
        pygame.display.set_caption('MIDASnake 1.0')
        self.mGameOver = True
        # MIDAS Variables
        self.apicall = 'http://localhost:8080/ecgnode/metric/median_bpm:ibi/5'
        self.last_speed_update = time.time()
        self.speed_update_interval = 2.0
    ##########################################################################

    def StartGame(self):
        MiddleX, MiddleY = self.mWindowWidth/2, self.mWindowHeight/2
        self.mSnakeLength = 3
        self.mSnake = [(MiddleX, MiddleY),
                       (MiddleX-self.mLineThickness, MiddleY),
                       (MiddleX-2*self.mLineThickness, MiddleY)]
        self.mSnakeXDirection = 1
        self.mSnakeYDirection = 0
        self.mFoodPosition = self.GetNextFoodPosition()
        self.mTimeSinceLastIncrease = time.time()
        self.mTimeSinceLastFood = time.time()
        self.mScore = 0

    ##########################################################################
    def IsInsideOfSnake(self, x, y):
        for SnakeX, SnakeY in self.mSnake:
            SnakeXRange = range(SnakeX, SnakeX + self.mLineThickness)
            SnakeYRange = range(SnakeY, SnakeY + self.mLineThickness)
            if x in SnakeXRange and y in SnakeYRange:
                return True
        return False

    ##########################################################################
    def GetNextFoodPosition(self):
        while True:
            x = randint(
                self.mLineThickness,
                (self.mWindowWidth - 2 * self.mLineThickness) /
                self.mLineThickness) * self.mLineThickness
            y = randint(
                self.mLineThickness,
                (self.mWindowHeight - 2 * self.mLineThickness) /
                self.mLineThickness) * self.mLineThickness
            self.mFoodColor = FOOD_COLOR
            if not self.IsInsideOfSnake(x, y):
                return x, y

    ##########################################################################
    def DrawMenu(self):
        NewGameSurface = \
            self.mBigFont.render("'S' = START NEW GAME", True, SNAKE_COLOR)
        NewGameRectangle = NewGameSurface.get_rect()
        NewGameRectangle.midbottom = (
            self.mWindowWidth/2,
            (self.mWindowHeight/4))

        EscapeSurface = \
            self.mBigFont.render("'ESC' = QUIT GAME", True, SNAKE_COLOR)
        EscapeRectangle = EscapeSurface.get_rect()
        EscapeRectangle.midtop = NewGameRectangle.midbottom

        self.mDisplay.blit(NewGameSurface, NewGameRectangle)
        self.mDisplay.blit(EscapeSurface, EscapeRectangle)

    ##########################################################################
    def DrawColorBorder(self):
        for xPos in range(self.mWindowWidth/10, 9*self.mWindowWidth/10,
                          self.mLineThickness):
            TopRectangle = pygame.Rect(
                xPos,
                self.mWindowHeight/10,
                self.mLineThickness,
                self.mLineThickness)
            BottomRectangle = pygame.Rect(
                xPos,
                9*self.mWindowHeight/10,
                self.mLineThickness,
                self.mLineThickness)
            pygame.draw.rect(self.mDisplay, UI_COLOR, TopRectangle)
            pygame.draw.rect(
                self.mDisplay,
                UI_COLOR,
                BottomRectangle)
        for yPos in range(self.mWindowHeight/10,
                          9*self.mWindowHeight/10+self.mLineThickness,
                          self.mLineThickness):
            LeftRectangle = pygame.Rect(
                self.mWindowWidth/10,
                yPos,
                self.mLineThickness,
                self.mLineThickness)
            RightRectangle = pygame.Rect(
                9*self.mWindowWidth/10,
                yPos,
                self.mLineThickness,
                self.mLineThickness)
            pygame.draw.rect(
                self.mDisplay,
                UI_COLOR,
                LeftRectangle)
            pygame.draw.rect(
                self.mDisplay,
                UI_COLOR,
                RightRectangle)

    ##########################################################################
    def DrawStartScreen(self):
        self.DrawBorder()
        self.DrawMenu()
        self.DrawColorBorder()
        pygame.display.update()

    ##########################################################################
    def DrawGame(self):
        self.DrawBorder()
        self.DrawFood()
        self.DrawSnake()
        self.DrawScore()
        pygame.display.update()

    ##########################################################################
    def DrawBorder(self):
        self.mDisplay.fill(BG_COLOR)
        pygame.draw.rect(
            self.mDisplay,
            UI_COLOR,
            ((0, 0), (self.mWindowWidth, self.mWindowHeight)),
            self.mLineThickness * 2)

    ##########################################################################
    def DrawSnake(self):
        for x, y in self.mSnake:
            Rect = pygame.Rect(x, y, self.mLineThickness, self.mLineThickness)
            pygame.draw.rect(self.mDisplay, SNAKE_COLOR, Rect)

    ##########################################################################
    def GetRandomColor(self):
        return randint(0, 255), randint(0, 255), randint(0, 255)
    ##########################################################################

    def DrawFood(self):
        x, y = self.mFoodPosition
        Food = pygame.Rect(x, y, self.mLineThickness, self.mLineThickness)
        pygame.draw.rect(self.mDisplay, self.mFoodColor, Food)

    ##########################################################################
    def GetNextHead(self):
        x, y = self.mSnake[0]
        x = x + self.mSnakeXDirection * self.mLineThickness
        y = y + self.mSnakeYDirection * self.mLineThickness
        return x, y
    ##########################################################################

    def MoveSnake(self):
        if time.time() - self.mTimeSinceLastIncrease > 5:
            self.mTimeSinceLastIncrease = time.time()
            self.mSnake = [self.GetNextHead()] + self.mSnake
        else:
            self.mSnake = [self.GetNextHead()] + self.mSnake[:-1]

    ##########################################################################
    def CheckForFoodCollision(self):
        if self.IsInsideOfSnake(self.mFoodPosition[0], self.mFoodPosition[1]):
            self.mScore += 100 * len(self.mSnake)
            self.mTimeSinceLastIncrease = -100
            self.mFoodPosition = self.GetNextFoodPosition()

    ##########################################################################
    def DisplayGameOver(self):
        GameOverSurface = self.mBigFont.render('GAME OVER', True, SNAKE_COLOR)
        GameOverRectangle = GameOverSurface.get_rect()
        GameOverRectangle.midbottom = (
            self.mWindowWidth/2,
            self.mWindowHeight/2)
        self.mDisplay.blit(GameOverSurface, GameOverRectangle)

        ScoreSurface = self.mBigFont.render(
            'Score = %s' %
            (self.mScore),
            True,
            FOOD_COLOR)
        ScoreRectangle = ScoreSurface.get_rect()
        ScoreRectangle.midtop = GameOverRectangle.midbottom
        self.mDisplay.blit(ScoreSurface, ScoreRectangle)

        pygame.display.update()
        time.sleep(3)

    ##########################################################################
    def Fail(self):
        self.DisplayGameOver()
        self.mGameOver = True

    ##########################################################################
    def CheckForSnakeCollision(self):
        if len(set(self.mSnake)) < len(self.mSnake):
            self.Fail()

    ##########################################################################
    def CheckForWallCollision(self):
        x, y = self.mSnake[0]
        if x <= 0 or x + self.mLineThickness >= self.mWindowWidth:
            self.Fail()
        elif y <= 0 or y + self.mLineThickness >= self.mWindowHeight:
            self.Fail()

    ##########################################################################
    def HandleKeyPress(self, Event):
        # Control snake
        if Event.key == K_DOWN:
            if self.mSnakeYDirection == 0:
                self.mSnakeXDirection = 0
                self.mSnakeYDirection = 1
        elif Event.key == K_UP:
            if self.mSnakeYDirection == 0:
                self.mSnakeXDirection = 0
                self.mSnakeYDirection = -1
        elif Event.key == K_RIGHT:
            if self.mSnakeXDirection == 0:
                self.mSnakeXDirection = 1
                self.mSnakeYDirection = 0
        elif Event.key == K_LEFT:
            if self.mSnakeXDirection == 0:
                self.mSnakeXDirection = -1
                self.mSnakeYDirection = 0

        # Set snake speed
        elif Event.key == K_1:
            self.mFrameRate = 10
        elif Event.key == K_2:
            self.mFrameRate = 20
        elif Event.key == K_3:
            self.mFrameRate = 30
        elif Event.key == K_4:
            self.mFrameRate = 40
        elif Event.key == K_5:
            self.mFrameRate = 50

        # Exit program
        elif Event.key == K_ESCAPE or Event.key == 113:
            pygame.quit()
            exit()
        elif Event.key == 115:
            self.StartGame()
            self.mGameOver = False

    ##########################################################################
    def DrawScore(self):
        score_text_surface = self.mFont.render('SCORE:', True, UI_COLOR)
        score_value_surface = self.mFont.render('%0.5d' % (self.mScore), True,
                                                FOOD_COLOR)
        score_text_rect = score_text_surface.get_rect()
        score_value_rect = score_value_surface.get_rect()

        score_text_rect.topleft = (self.mLineThickness*3, self.mLineThickness*2)
        self.mDisplay.blit(score_text_surface, score_text_rect)

        score_value_rect.topleft = (score_text_rect.right,
                                    self.mLineThickness*2)
        self.mDisplay.blit(score_value_surface, score_value_rect)

        speed_text_surface = self.mFont.render('SPEED:', True, UI_COLOR)
        speed_value_surface = self.mFont.render('%0.2d' % (self.mFrameRate),
                                                True, FOOD_COLOR)
        speed_text_rect = speed_text_surface.get_rect()
        speed_value_rect = speed_value_surface.get_rect()

        speed_text_rect.topleft = (score_value_rect.right + 10,
                                   self.mLineThickness*2)
        self.mDisplay.blit(speed_text_surface, speed_text_rect)

        speed_value_rect.topleft = (speed_text_rect.right,
                                    self.mLineThickness*2)
        self.mDisplay.blit(speed_value_surface, speed_value_rect)
    ##########################################################################

    def CheckIfStuck(self):
        if time.time() - self.mTimeSinceLastIncrease > 10:
            self.mFoodPosition = self.GetNextFoodPosition()

    ##########################################################################
    def UpdateSpeed(self):
        if time.time() - self.last_speed_update > self.speed_update_interval:
            try:
                r = requests.get(self.apicall, timeout=0.10).json()
                if r:
                    bpm = r['median_bpm_ibi']
                    if bpm < 40:
                        bpm = 40.0
                    elif bpm > 120:
                        bpm = 120.0
                    self.mFrameRate = bpm / 2 - 10
                    self.last_speed_update = time.time()
            except:
                pass

    def Run(self):
        while True:
            try:
                for Event in pygame.event.get():
                    if Event.type == QUIT:
                        pygame.quit()
                        exit()
                    elif Event.type == KEYDOWN:
                        self.HandleKeyPress(Event)

                if self.mGameOver:
                    self.DrawStartScreen()
                else:
                    self.DrawGame()
                    self.mClock.tick(self.mFrameRate)
                    self.MoveSnake()
                    self.CheckForFoodCollision()
                    self.CheckForWallCollision()
                    self.CheckForSnakeCollision()
                    self.CheckIfStuck()
                    # Add check for speed
                    self.UpdateSpeed()
            except KeyboardInterrupt:
                pygame.quit()
                exit()
        pygame.quit()
        exit()

################################################################################
################################################################################
if __name__ == '__main__':
    SnakeGame = Snake()
    SnakeGame.Run()
