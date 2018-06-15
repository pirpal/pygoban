#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SgfParser:
    """
    takes a sgf file and return a data dictionnary containing sgf properties
    set for the game and moves list

    """
    def __init__(self, file):
        self.file = file
        self.data = {
            "moves": {},
        }
        self.parse()

    def cleanString(self, old_str, chrs):
        new_str = old_str
        for c in chrs:
            new_str = new_str.replace(c, "")
        return new_str

    def parse(self):
        data_str = ""
        with open(self.file) as f:
            for line in f.readlines():
                if line != "":
                    data_str += self.cleanString(line, ["(", ")", "\n"])
        data_list = data_str.split(";")
        move_nb = 0
        for elt in data_list:
            if elt != "":
                if elt[:2] in ["B[", "W["]:
                    move_nb += 1
                    self.data["moves"][move_nb] = (elt[0], elt[2:4])
                else:
                    properties_list = elt.split("]")
                    for p in properties_list:
                        if p != "":
                            property_set = p.split("[")
                            self.data[property_set[0]] = property_set[1]


# parser = SgfParser("./games/1.sgf")
# print(parser.data)
