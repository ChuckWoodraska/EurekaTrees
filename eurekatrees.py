import csv
import argparse
import jinja2
import json
import webbrowser
import os

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
        self.max_depth = None
        self.max_breadth = None

    def create_tree(self, tree, column_names):
        else_check = 0
        node = None
        for index, line in enumerate(tree['Contents']):
            if line.startswith('If'):
                data_str = line[line.find('(')+1:line.find(')')].replace(' ', '_', 1)
                if len(column_names):
                    data_str = column_names[data_str.split(' ')[1]]+' '+' '.join(data_str.split(' ')[2:])
                if not node:
                    node = self.root = Node(data=data_str)
                elif else_check:
                    else_check = 0
                    while node.right:
                        node = node.parent
                    node.right = Node(data=data_str)
                    node.right.parent = node
                    node = node.right
                else:
                    node.left = Node(data=data_str)
                    node.left.parent = node
                    node = node.left
            elif line.startswith('Else'):
                else_check = 1
            elif line.startswith('Predict'):
                if not node:
                    node = self.root = Node(data=float(line.rsplit(' ')[1]))
                elif else_check:
                    else_check = 0
                    while node.right:
                        node = node.parent
                    node.right = Node(data=float(line.rsplit(' ')[1]))
                    node.right.parent = node
                    node = node.parent
                else:
                    node.left = Node(data=float(line.rsplit(' ')[1]))
                    node.left.parent = node
        self.max_depth = self.get_max_depth(self.root) - 1
        self.max_breadth = self.get_max_breadth(self.max_depth)

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

    def get_js_struct(self, node, node_dict=None):
        if node_dict is None:
            node_dict = {'name': node.data, 'children': []}
        if node is not None:
            if node.left:
                new_node_dict_left = {'name': node.left.data, 'type':'left', 'is_prediction':False 'children': []}
                node_dict['children'].append(self.get_js_struct(node.left, new_node_dict_left))
            if node.right:
                new_node_dict_right = {'name': node.right.data, 'type':'right', 'is_prediction':False 'children': []}
                node_dict['children'].append(self.get_js_struct(node.right, new_node_dict_right))
            else:
                node_dict['is_prediction'] = True
            if node.parent is None:
                node_dict['type'] = 'root'
        return node_dict

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

    def get_max_depth(self, node):
        if node is None:
            return 0
        else:
            left_depth = self.get_max_depth(node.left)
            right_depth = self.get_max_depth(node.right)
            if left_depth > right_depth:
                return left_depth + 1
            else:
                return right_depth + 1

    def get_max_breadth(self, max_depth=None):
        if max_depth is None:
            max_depth = self.get_max_depth(self.root)
        return 2**max_depth


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


def make_tree_viz(trees, output_path):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(["."]))
    home_template = env.get_template("templates/home_template.jinja2")
    tree_list = ['trees/tree{0}.html'.format(index+1) for index, tree in enumerate(trees)]
    result = home_template.render(trees=tree_list)
    with open(os.path.join(output_path, 'home.html'), 'w') as home_html:
        home_html.write(result)
    tree_template = env.get_template("templates/tree_template.jinja2")
    for index, tree in enumerate(trees):
        # These are kind of magic numbers for max_depth and max_breadth for how big the canvas needs to be
        result = tree_template.render(tree=json.dumps(tree['tree']),
                                      max_depth=tree['max_depth']*120 if tree['max_depth'] else 120,
                                      max_breadth=tree['max_depth']*750 if tree['max_depth'] else 750)
        with open(os.path.join(output_path, 'trees/tree{0}.html'.format(index+1)), 'w') as tree_html:
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
    parser.add_argument('--trees', dest='trees', help='Path to file holding the trees.', required=True)
    parser.add_argument('--columns', dest='columns', default=None,
                        help='Path to csv file holding column index and column name.')
    parser.add_argument('--output_path', dest='output_path', default='./sample_output',
                        help='Path to outputted files.')
    args = parser.parse_args()
    column_name_dict = {}
    if args.columns:
        column_name_dict = read_columns(args.columns)
    trees = read_trees(args.trees)
    tree_list = []
    for index, tree in enumerate(trees):
        tree_obj = Tree()
        tree_obj.create_tree(tree, column_name_dict)
        js_struct = tree_obj.get_js_struct(tree_obj.root)
        node_dict = {'tree': [js_struct], 'max_depth': tree_obj.max_depth, 'max_breadth': tree_obj.max_breadth}
        tree_list.append(node_dict)
    make_tree_viz(tree_list, args.output_path)
    webbrowser.open_new(os.path.join(args.output_path, 'home.html'))


if __name__ == "__main__":
    main()
