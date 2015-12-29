import csv
import argparse
import jinja2
import json

__author__ = 'Chuck Woodraska'


class Node(object):
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.parent = None


class Tree(object):
    def __init__(self):
        self.root = None

    def create_tree(self, tree, column_names):
        else_check = 0
        node = None
        for line in tree['Contents']:
            if line.startswith('If'):
                data_str = line[line.find('(')+1:line.find(')')]
                if len(column_names):
                    data_str = column_names[data_str.split(' ')[1]]+' '+' '.join(data_str.split(' ')[2:])
                if not node:
                    node = self.root = Node(data=data_str)
                elif else_check:
                    else_check = 0
                    node.right = Node(data=data_str)
                    node.right.parent = node
                    node = node.right
                else:
                    node.left = Node(data=data_str)
                    node.left.parent = node
                    node = node.left
            elif line.startswith('Else'):
                else_check = 1
                if node.right:
                    node = node.parent
            elif line.startswith('Predict'):
                if else_check:
                    else_check = 0
                    node.right = Node(data=line)
                    node.right.parent = node
                    node = node.parent
                else:
                    node.left = Node(data=line)
                    node.left.parent = node

    def print_inorder(self, node):
        if node is not None:
            self.print_inorder(node.left)
            print(node.data)
            self.print_inorder(node.right)

    def preorder(self, node, node_list=None):
        if node_list is None:
            node_list = []
        if node is not None:
            node_list.append(node)
            self.preorder(node.left, node_list)
            self.preorder(node.right, node_list)
        return node_list

    def print_preorder(self, node):
        if node is not None:
            print(node.data)
            self.print_preorder(node.left)
            self.print_preorder(node.right)

    def print_postorder(self, node):
        if node is not None:
            self.print_postorder(node.left)
            self.print_postorder(node.right)
            print(node.data)


def separate_trees(tree_file):
    tree = ''
    tree_contents = []
    tree_list = []
    for line in tree_file:
        line = line.strip().rstrip()
        if line.find('Tree') != -1:
            if tree:
                tree_list.append({'Tree': tree, 'Contents': tree_contents})
            tree = line
            tree_contents = []
        else:
            tree_contents.append(line)
    tree_list.append({'Tree': tree, 'Contents': tree_contents})
    return tree_list


def make_tree_viz(trees):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(["."]))
    home_template = env.get_template("templates/home_template.jinja2")
    tree_list = ['trees/tree{0}.html'.format(index+1) for index, tree in enumerate(trees)]
    result = home_template.render(trees=tree_list)
    with open('home.html', 'w') as home_html:
        home_html.write(result)
    tree_template = env.get_template("templates/tree_template.jinja2")
    for index, tree in enumerate(trees):
        result = tree_template.render(tree=json.dumps(tree))
        with open('trees/tree{0}.html'.format(index+1), 'w') as tree_html:
            tree_html.write(result)


def read_columns(columns_file):
    column_name_dict = {}
    with open(columns_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            column_name_dict[row['INDEX']] = row['COLUMN_NAME']
    return column_name_dict


def read_trees(trees_file):
    with open(trees_file) as treesfile:
        return separate_trees(treesfile.readlines())


def main():
    parser = argparse.ArgumentParser(description='Parse a random forest')
    parser.add_argument('--trees', dest='trees',
                       help='Path to file holding the trees.')
    parser.add_argument('--columns', dest='columns', default=None,
                       help='Path to csv file holding column index and column name.')
    args = parser.parse_args()
    column_name_dict = {}
    if args.columns:
        column_name_dict = read_columns(args.columns)
    trees = read_trees(args.trees)
    tree_list = []
    for tree in trees:
        tree_obj = Tree()
        tree_obj.create_tree(tree, column_name_dict)
        node_list = tree_obj.preorder(tree_obj.root)
        node_dict = []
        for node in node_list:
            name = node.data
            parent = None
            if node.parent:
                parent = node.parent.data
            node_dict.append({'name': name, 'parent': parent})
        tree_list.append(node_dict)
    make_tree_viz(tree_list)

if __name__ == "__main__":
    main()
