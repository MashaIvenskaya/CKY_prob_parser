import sys
import nltk
from collections import defaultdict

class Cell(object):
	def __init__(self):
		self.cell_contents = defaultdict(list)

	def fill_cell(self, lhs, pointers):
		self.cell_contents[lhs].append(pointers)

	def cell_lhss(self):
		return self.cell_contents.keys()

	def pointers(self, lhs):
		return self.cell_contents[lhs]

class Pointer(object):
	def __init__(self, pair, candidate_pair):
		self.pair = pair
		self.candidate_pair = candidate_pair

	def cell_address(self):
		return self.pair

	def rule(self):
		return self.candidate_pair

	def left_coords(self):
		address = self.cell_address()
		left = address[0]
		return left[0], left[1]

	def right_coords(self):
		address = self.cell_address()
		right = address[1]
		return right[0], right[1]

	def left_const(self):
		return self.rule().split('&')[0]

	def right_const(self):
		return self.rule().split('&')[1]

class CKY_Parser(object):

	def __init__(self, grammar_file):
		self.rhs_dict = defaultdict(list)
		self.lhs_dict = defaultdict(list)
		self.grammar = grammar_file

	def load_grammar(self):
		with open(self.grammar, 'rU') as f:
			for line in f:
				if line:
					lhs, rhs = line.strip().split('->')
					rhs = rhs.strip().split(' ')
					self.lhs_dict[lhs.strip()].append(rhs)
					rhs_string = '&'.join(rhs)
					self.rhs_dict[rhs_string].append(lhs.strip())

	def cells_to_check(self, x, y):
		list_of_pairs = []
		lower = y
		upper = x+1
		for i in range(lower+1, upper):
			left = (i-1, lower)
			right = (upper-1, i)
			pair = (left, right)
			list_of_pairs.append(pair)
		return list_of_pairs

	def check_candidates(self, left_candidate, right_candidate):
		lhs_list = []
		for left_pos in left_candidate.keys():
			for right_pos in right_candidate.keys():
				candidate_pair = '&'.join([left_pos, right_pos])
				if candidate_pair in rhs_dict:
					lhs = rhs_dict[candidate_pair]
					lhs_list.extend(lhs)
		return lhs_list

	def fill_matrix(self, sentence):
		sent = nltk.word_tokenize(sentence)
		sent_len = len(sent)
		matrix = [None] * sent_len
		for i in range(sent_len):
			l = [None] * (i+1)
			matrix[i] = l
		for i in range(sent_len):
			pos = self.rhs_dict['\''+sent[i] + '\'']
			matrix[i][i] = Cell()
			for each in pos:
				matrix[i][i].fill_cell(each, 'leaf')
			for j in reversed(range(i)):
				cell_value = Cell()
				pairs = self.cells_to_check(i, j)
				for pair in pairs:
					left, right = pair
					left_candidates = matrix[left[0]][left[1]]
					right_candidates = matrix[right[0]][right[1]]
					if left_candidates.cell_contents and right_candidates.cell_contents:
						for left_candidate in left_candidates.cell_lhss():
							for right_candidate in right_candidates.cell_lhss():
								candidate_pair = '&'.join([left_candidate, right_candidate])
								if candidate_pair in self.rhs_dict:
									lhss = self.rhs_dict[candidate_pair]
									for lhs in lhss:
										new_pointer = Pointer(pair, candidate_pair)
										cell_value.fill_cell(lhs, new_pointer)
				 
				matrix[i][j] = cell_value
		return matrix


	def traverse_matrix(self, x, y, label, matrix, parses, sent):
		cell = matrix[x][y]
		ptrs = cell.pointers(label)
		if ptrs == ['leaf']:
			word = sent[x]
			return [nltk.Tree(label, [word])]

		subtrees = []
		for ptr in ptrs:
			left_y, left_x = ptr.left_coords()
			right_y, right_x = ptr.right_coords()
			left_cell = matrix[left_y][left_x]
			right_cell = matrix[right_y][right_x]
			left_const = ptr.left_const()
			right_const = ptr.right_const()
			left_daughter = left_cell.pointers(left_const)
			right_daughter = right_cell.pointers(right_const)
			address = ptr.cell_address()
			left = address[0]
			right = address[1]
			left_trees = self.traverse_matrix(left[0], left[1], left_const, matrix, parses, sent)
			right_trees = self.traverse_matrix(right[0], right[1], right_const, matrix, parses, sent)
			for ltree in left_trees:
				for rtree in right_trees:
					final_tree = nltk.Tree(label, [ltree, rtree])
					subtrees.append(final_tree)
					if final_tree.label() == 'TOP':
						parses.append(final_tree)		
		return subtrees


def main():
	grammar_file = sys.argv[1]
	sentence_file =sys.argv[2]
	output_file = sys.argv[3]
	parser = CKY_Parser(grammar_file)
	parser.load_grammar()

	with open(sentence_file, 'rU') as f:
		with open(output_file, 'w') as w:
			for line in f:
				w.write(line)
				w.write('\n')
				sent = line.strip()
				tokenized = nltk.word_tokenize(sent)
				matrix = parser.fill_matrix(sent)
				parses = []
				root_cell = matrix[-1][0]
				if 'TOP' in root_cell.cell_lhss():
					parser.traverse_matrix(-1, 0, 'TOP', matrix, parses, tokenized)
				for parse in parses:
					w.write(str(parse))
					w.write('\n')
					w.write('\n')
				w.write('Number of parses: ' + str(len(parses)))
				w.write('\n')
				w.write('\n')

					


if __name__ == "__main__":
    main()