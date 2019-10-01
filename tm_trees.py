"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all sub-directories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional

class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this asignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: Optional[str]
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = True

        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        self.data_size = data_size
        self._sum_size()

        for tree in self._subtrees:
            tree._parent_tree = self

    def _sum_size(self) -> int:
        """Return the total data_size of this tree
        """
        if self.is_empty():
            self.data_size = 0

        elif self._subtrees == []:
            pass

        else:
            total = 0
            for tree in self._subtrees:
                total += tree._sum_size()
            self.data_size = total

        return self.data_size

    def _get_root(self) -> TMTree:
        """Return the root Tree of this TMTree
        """
        if self._parent_tree is None:
            return self

        else:
            return self._parent_tree._get_root()

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def _divide_rects(self, rect: Tuple[int, int, int, int]) -> None:
        """Divide the subtrees contained in this tree using the formula stated
        in the assignment description.

        Prerequisite: self is not a leaf.
        """
        x, y, width, height = rect
        pairings = []

        if width > height:
            nx = x
            for tree in self._subtrees:
                nw = math.floor((abs(x - width) *
                                 (tree.data_size / self.data_size)))
                if tree == self._subtrees[-1] and (nx + nw - x) != width:
                    nw = (width + x) - nx
                pairings.append((nx, nw))
                nx += nw

            for tree, coords in zip(self._subtrees, pairings):
                tree.update_rectangles((coords[0], y, coords[1], height))

        else:
            ny = y
            for tree in self._subtrees:
                nh = math.floor((abs(y - height) *
                                 (tree.data_size / self.data_size)))
                if tree == self._subtrees[-1] and (ny + nh - y) != height:
                    nh = (height + y) - ny
                pairings.append((ny, nh))
                ny += nh

            for tree, coords in zip(self._subtrees, pairings):
                tree.update_rectangles((x, coords[0], width, coords[1]))

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        if self.is_empty() or self.data_size == 0:
            pass

        elif self._subtrees == [] or not self._expanded:
            self.rect = rect

        else:
            self.rect = rect
            self._divide_rects(rect)

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        if self._expanded:
            if self.is_empty():
                return []

            elif self._subtrees == []:
                return [(self.rect, self._colour)]

            else:
                rects = []
                for tree in self._subtrees:
                    rects.extend(tree.get_rectangles())
                return rects
        else:
            return [(self.rect, self._colour)]

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        x, y = pos
        lx, ly, ux, uy = self.rect

        if self.is_empty():
            return None

        elif self._subtrees == [] or not self._expanded:
            if lx <= x <= lx + ux and ly <= y <= ly + uy:
                return self

            else:
                return None

        else:
            matches = []
            for tree in self._subtrees:
                match = tree.get_tree_at_position(pos)
                if match is not None:
                    matches.append(match)

            #TIE BREAKER
            return _break_ties(matches)


    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        return self._sum_size()

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if self._subtrees != [] or destination._subtrees == []:
            pass
        else:
            self._parent_tree._subtrees.remove(self)
            self._parent_tree.update_data_sizes()
            destination._subtrees.append(self)
            destination.update_data_sizes()

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if self._subtrees != [] or self.is_empty():
            pass

        else:
            change = math.ceil(self.data_size * (abs(factor)))
            #Set polarity of change
            change *= int(factor / abs(factor))

            self.data_size += change

    def expand(self) -> None:
        """Expand this tree, so that it's subtrees are shown.
        If this tree is expanded, or a leaf, do nothing.
        """
        if self._expanded or self._subtrees == []:
            pass

        else:
            self._expanded = True
            self.update_rectangles(self.rect)

    def expand_all(self) -> None:
        """Expand this tree, and all trees within it.
        If this tree is exanded, or a leaf, do nothing.
        """
        if self._expanded or self._subtrees == []:
            pass

        else:
            self._expanded = True
            self.update_rectangles(self.rect)
            for tree in self._subtrees:
                tree.expand_all()

    def collapse(self) -> None:
        """Collapse the selected group of trees.
        If the selected tree is the root of the tree, do nothing.
        """
        if self._parent_tree is None:
            pass

        else:
            self._parent_tree._collapse_sub()

    def _collapse_sub(self) -> None:
        """Collapse all subtrees of this tree.
        """
        self._expanded = False

        if self._subtrees == []:
            pass

        else:
            for tree in self._subtrees:
                tree._collapse_sub()

    def collapse_all(self) -> None:
        """Collapse every tree contained in the root of this tree.
        """
        root = self._get_root()
        root._collapse_sub()


    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str

        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

# HELPER FUNCTIONS
def _break_ties(matches: List[TMTree]) -> TMTree:
    """Return the TMTree in matches that is clostest to (0,0)
    """
    if len(matches) > 1:
        closest = matches[0]
        for match in matches:
            if match.rect[0] < closest.rect[0]:
                closest = match
            elif  match.rect[1] < closest.rect[1]:
                closest = match
        return closest

    elif len(matches) == 1:
        return matches[0]

    else:
        return None


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!

        # COULD BE MORE EFFICIENT
        # self.rect = (0, 0, 0, 0)
        # self._name = os.path.basename(path)
        # self._colour = (randint(0,255),randint(0,255),randint(0,255))
        # self._subtrees = []
        # self._parent_tree = None
        #
        # i = 0
        # for file in os.listdir(path):
        #     self._subtrees.append(FileSystemTree(os.path.join(path, file))
        #     self._subtrees[i]._parent_tree = self
        #     i += 1
        #
        # self.data_size = self._sum_size()
        temp_subtrees = []
        if os.path.isdir(path):
            for x in os.listdir(path):
                temp_subtrees.append(FileSystemTree(os.path.join(path, x)))
        super().__init__(os.path.basename(path), temp_subtrees,
                         os.path.getsize(path))

    def _sum_os_size(self, path: str) -> int:
        """Return the data_size of self

        Precondition: <path> is a valid path for this computer
        """
        if self.is_empty():
            return 0

        elif not os.path.isdir(path):
            return os.path.getsize(path)

        elif self._subtrees == []:
            return 0

        else:
            total = 0
            for file in self._subtrees:
                total += file._sum_size(path)
            return total

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    # x = FileSystemTree(test_path)
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
