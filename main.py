#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk


class Stone:

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.belongs_to_group = False

    def __repr__(self):
        """ for console debug """
        return self.color[0]


class StoneGroup:

    def __init__(self, stones):
        self.stones = stones


class PyGoban(tk.Tk):

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        # self.resizable(width=False, height=False)
        self.geometry("800x580+100+100")
        self.title("PyGoban")
        self.goban = [[0 for i in range(19)] for i in range(19)]
        self.offset = 40  # goban grid offset from top-left canvas corner
        self.stone_size = 20
        self.game_turn = 0
        self.colors = ["black", "white"]
        self.white_stones = []
        self.black_stones = []
        self.white_prisoners = tk.IntVar(0)
        self.black_prisoners = tk.IntVar(0)
        self.goban_coords = tk.StringVar()
        self.stone_data_str = tk.StringVar()
        self.initWidgets()
        self.drawGoban()
        self.drawPoints()
        self.displayCoordinates()
        self.can.bind("<Button-1>", self.mouseClick)
        self.can.bind("<Button-3>", self.displayStoneData)
        self.can.bind("<Motion>", self.mouseMove)

    def initWidgets(self):
        self.can = tk.Canvas(self, width=480, height=480, bg="#dcb35c")
        # self.can.configure(cursor="none")
        self.can.grid(row=0, column=0)

        self.screens_frame = tk.Frame(self, bg="blue")
        self.screens_frame.grid(row=1, column=0)
        self.coords_screen = tk.Label(
            self.screens_frame,
            justify=tk.LEFT,
            textvariable=self.goban_coords,
            width=8,  # characters
            height=3,  # lines
            bg="#272822",
            fg="white"
        )
        self.coords_screen.grid(row=0, column=0)

        self.debug_screen = tk.Label(
            self.screens_frame,
            justify=tk.LEFT,
            textvariable=self.stone_data_str,
            width=30,
            height=4,
            bg="black",
            fg="white"
        )
        self.debug_screen.grid(row=0, column=1)

    # DISPLAY -----------------------------------------------------------------

    def drawGoban(self):
        for x in range(18):
            for y in range(18):
                self.can.create_rectangle(
                    self.offset + x * self.stone_size,
                    self.offset + y * self.stone_size,
                    self.offset + x * self.stone_size + self.stone_size,
                    self.offset + y * self.stone_size + self.stone_size
                )

    def drawStone(self, stone):
        self.can.create_oval(
            self.offset + stone.x * self.stone_size - self.stone_size / 2,
            self.offset + stone.y * self.stone_size - self.stone_size / 2,
            self.offset + stone.x * self.stone_size - self.stone_size / 2 + self.stone_size,
            self.offset + stone.y * self.stone_size - self.stone_size / 2 + self.stone_size,
            fill=stone.color
        )

    def drawStones(self):
        for x in range(19):
            for y in range(19):
                if self.goban[x][y] != 0:
                    self.drawStone(self.goban[x][y])

    def displayCoordinates(self):
        numbers = list(range(19, 0, -1))
        letters = list("ABCDEFGHJKLMNOPQRST")
        for i in range(1, 20):
            self.can.create_text(
              self.offset/2,
              self.offset/2 + i * self.stone_size,
              text=numbers[i-1]
            )
            self.can.create_text(
              self.offset + self.stone_size * 19,
              self.offset/2 + i * self.stone_size,
              text=numbers[i-1]
            )
            self.can.create_text(
              self.offset/2 + i * self.stone_size,
              self.offset/2,
              text=letters[i-1]
            )
            self.can.create_text(
                self.offset/2 + i * self.stone_size,
                self.offset + self.stone_size * 19,
                text=letters[i-1]
            )

    def drawPoint(self, x, y):
        self.can.create_oval(
            self.offset + x * self.stone_size - 2,
            self.offset + y * self.stone_size - 2,
            self.offset + x * self.stone_size + 2,
            self.offset + y * self.stone_size + 2,
            fill="black"
        )

    def drawPoints(self):
        """ display tengen and hoshi points on the goban """
        for x in [(3, 3), (9, 3), (15, 3),
                  (3, 9), (9, 9), (15, 9),
                  (3, 15), (9, 15), (15, 15)]:
            self.drawPoint(x[0], x[1])

    def drawLastMove(self, x, y):
        """ red square mark on last played stone """
        self.can.delete("last")
        self.can.create_rectangle(
            self.offset + x * self.stone_size - 4,
            self.offset + y * self.stone_size - 4,
            self.offset + x * self.stone_size + 4,
            self.offset + y * self.stone_size + 4,
            outline="red", fill="red", tag="last"
        )

    # DATA AND DEBUG ----------------------------------------------------------

    def consoleDisplay(self):
        print("move {}\n".format(self.game_turn + 1))
        for x in self.goban:
            print(*x, sep=" ")

    def displayStoneData(self, evt):
        " liberties and groups debug "
        goban_x = (evt.x - self.offset) // self.stone_size
        goban_y = (evt.y - self.offset) // self.stone_size
        if self.goban[goban_x][goban_y] == 0:
            return None
        else:
            stone = self.goban[goban_x][goban_y]
            if stone.belongs_to_group:
                group = " G"
            else:
                group = ""
            self.stone_data_str.set(
                "{} {} ({} {})".format(
                    stone.color[0],
                    self.humanCoords(stone.x, stone.y),
                    self.countLiberties(stone),
                    group
                )
            )

    def humanCoords(self, x, y):
        """ goban[0][0] (top left corner) is 'a19' """
        return "abcdefghjklmnopqrst"[x] + str(19 - y)

    # GAME LOGIC --------------------------------------------------------------

    def countLiberties(self, stone):
        liberties = 0
        neighbours = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for n in neighbours:
            try:
                if self.goban[stone.x + n[0]][stone.y + n[1]] == 0:
                    liberties += 1
                # check if the stone is connected in a group :
                elif self.goban[stone.x + n[0]][stone.y + n[1]].color == stone.color:
                    stone.belongs_to_group = True
            except IndexError:
                pass
        return liberties

    def countGroupLiberties(self, stone_group):
        liberties = 0
        for stone in stone_group:
            liberties += self.countLiberties(stone)
        return liberties

    def updateBlackStones(self):
        """ check each stone liberties after click """
        for s in self.black_stones:
            if s.belongs_to_group is False:
                if self.countLiberties(s) == 0:
                    x, y = s.x, s.y
                    self.goban[x][y] == 0
                    self.black_stones.remove(s)
                    self.black_prisoners.set(self.black_prisoners.get() + 1)

    def updateWhiteStones(self):
        """ check each stone liberties after click """
        for s in self.white_stones:
            if s.belongs_to_group is False:
                if self.countLiberties(s) == 0:
                    x, y = s.x, s.y
                    self.goban[x][y] == 0
                    self.white_stones.remove(s)
                    self.white_prisoners.set(self.white_prisoners.get() + 1)

    # EVENTS ------------------------------------------------------------------

    def mouseMove(self, evt):
        """ display preview stone on the goban """
        self.can.delete("preview")
        goban_x = (evt.x - self.offset) // self.stone_size
        goban_y = (evt.y - self.offset) // self.stone_size
        color = self.colors[self.game_turn % 2]
        if goban_x in range(19) and goban_y in range(19):
            self.goban_coords.set(self.humanCoords(goban_x, goban_y))
            if self.goban[goban_x][goban_y] == 0:
                self.can.create_rectangle(
                    self.offset + goban_x * self.stone_size - 5,
                    self.offset + goban_y * self.stone_size - 5,
                    self.offset + goban_x * self.stone_size + 5,
                    self.offset + goban_y * self.stone_size + 5,
                    fill=color, tag="preview"
                )

    def mouseClick(self, evt):
        goban_x = (evt.x - self.offset) // self.stone_size
        goban_y = (evt.y - self.offset) // self.stone_size
        self.can.update()
        color = self.colors[self.game_turn % 2]
        if goban_x in range(19) and goban_y in range(19):
            if self.goban[goban_x][goban_y] == 0:
                # TODO here check for illegal move (suicide)
                new_stone = Stone(goban_x, goban_y, color)
                self.goban[goban_x][goban_y] = new_stone
                if color == "black":
                    self.black_stones.append(new_stone)
                    self.updateWhiteStones()
                else:
                    self.white_stones.append(new_stone)
                    self.updateBlackStones()
                self.can.update()
                self.displayStoneData(new_stone)
                self.game_turn += 1
                self.drawStones()
                self.drawLastMove(goban_x, goban_y)


if __name__ == '__main__':
    app = PyGoban(None)
    app.mainloop()
