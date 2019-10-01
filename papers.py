"""Assignment 2: Modelling CS Education research paper data

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains a new class, PaperTree, which is used to model data on
publications in a particular area of Computer Science Education research.
This data is adapted from a dataset presented at SIGCSE 2019.
You can find the full dataset here: https://www.brettbecker.com/sigcse2019/

Although this data is very different from filesystem data, it is still
hierarchical. This means we are able to model it using a TMTree subclass,
and we can then run it through our treemap visualisation tool to get a nice
interactive graphical representation of this data.
"""
import csv
from typing import List, Dict
from tm_trees import TMTree

# Filename for the dataset
DATA_FILE = 'cs1_papers.csv'


class PaperTree(TMTree):
    """A tree representation of Computer Science Education research paper data.

    === Private Attributes ===
    _authors:
        The authors of this PaperTree.
    _doi:
        The url of this PaperTree.

    === Inherited Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.
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
    - All TMTree RIs are inherited.
    """
    _authors: str
    _doi: str


    def __init__(self, name: str, subtrees: List[TMTree], authors: str = '',
                 doi: str = '', citations: int = 0, by_year: bool = True,
                 all_papers: bool = False) -> None:
        """Initialize a new PaperTree with the given <name> and <subtrees>,
        <authors> and <doi>, and with <citations> as the size of the data.

        If <all_papers> is True, then this tree is to be the root of the paper
        tree. In that case, load data about papers from DATA_FILE to build the
        tree.

        If <all_papers> is False, Do NOT load new data.

        <by_year> indicates whether or not the first level of subtrees should be
        the years, followed by each category, subcategory, and so on. If
        <by_year> is False, then the year in the dataset is simply ignored.
        """
        if all_papers:
            temp_dict = _load_papers_to_dict(by_year)
            temp_subtrees = _build_tree_from_dict(temp_dict)
        else:
            temp_subtrees = subtrees

        super().__init__(name, temp_subtrees, citations)
        self._authors = authors
        self._doi = doi


    def get_separator(self) -> str:
        """Return the file separator for this Tree.
        """
        return ':'

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (category)'


def _load_papers_to_dict(by_year: bool = True) -> Dict:
    """Return a nested dictionary of the data read from the papers dataset file.

    If <by_year>, then use years as the roots of the subtrees of the root of
    the whole tree. Otherwise, ignore years and use categories only.
    """
    result = {}

    with open(DATA_FILE, 'r') as data:
        data.readline()
        file = csv.reader(data)

        for row in file:
            authors, name, year, temp_categories, doi, citations = row
            categories = temp_categories.split(':')

            if by_year:
                categories.insert(0, year)

            working_dict = result
            for category in categories:
                if category in working_dict.keys():
                    working_dict = working_dict[category]
                else:
                    working_dict[category] = {}
                    working_dict = working_dict[category]

            working_dict[name] = {}
            working_dict = working_dict[name]

            working_dict['authors'] = authors
            working_dict['name'] = name
            working_dict['doi'] = doi
            working_dict['citations'] = int(citations)

    return result




def _build_tree_from_dict(nested_dict: Dict) -> List[PaperTree]:
    """Return a list of trees from the nested dictionary <nested_dict>.
    """
    ans = []
    if nested_dict == {}:
        return ans

    elif 'authors' in nested_dict.keys():
        ans.append(PaperTree(nested_dict['name'], [], nested_dict['authors'],
                             nested_dict['doi'], nested_dict['citations']))

    else:
        for name, yep in nested_dict.items():
            ans.append(PaperTree(name, _build_tree_from_dict(yep)))

    return ans


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['python_ta', 'typing', 'csv', 'tm_trees'],
        'allowed-io': ['_load_papers_to_dict'],
        'max-args': 8
    })
