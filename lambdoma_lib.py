import re, copy
from collections import deque
parameter = '[a-z]+\'*'			#all lowercase, with possible primes
lookup = '[0-9A-Z][0-9A-z]*\'*'	#numerals, or initial uppercase
name = '[0-9A-z]+\'*'			#any alphanumeric
L = chr(955)					#'λ'

#~~~~INPUT FUNCTIONS~~~~
def format(console_in):
	#backslash to lambda
	console_in = console_in.replace('\\',L)
	#put parentheses around names
	console_in += " "
	console_in = re.sub(f'({name})([^\'.])',r'(\1)\2',console_in)
	#remove spaces (but not tabs, line feeds, &c.)
	console_in = console_in.replace(" ","")
	#replace juxtaposition with infix operators
	console_in = console_in.replace(")(",")*(")
	return console_in

#split console_in into tokens (lexing)
def in_split(console_in):
	seq_i = deque()
	while console_in:
		try:
			match = re.match(f'{name}|[\\)\\(\\*]|{L}{parameter}\\.',console_in)
			seq_i.append(console_in[:match.span()[1]])
			console_in = console_in[match.span()[1]:]
		except:
			print(console_in+"| in_split")
			break
	return seq_i

#go from infix to prefix notation (shunting yard algorithm)
def polish(seq_i):
	seq = deque()
	stack = deque()
	while seq_i:
		symbol = seq_i.pop()
		if symbol in ')*':
			stack.append(symbol)
		elif symbol == '(' or symbol[0] == L:
			try:
				while stack and stack[-1] != ')':
					seq.appendleft(stack.pop())
				if symbol == '(':
					stack.pop()
				elif symbol[0] == L:
					seq.appendleft(symbol)
			except:
				raise SyntaxError('Mismatched parentheses')
		else:
			seq.appendleft(symbol)
	while stack:
		op = stack.pop()
		if op == ')':
			raise SyntaxError('Mismatched parentheses')
		else:
			seq.appendleft(op)
	return seq
		
	
#rewrite variables as de Bruijn indices using the obligation stack	
#indices count from one
def to_numeral(seq):
	#parse using a stack of unsatisfied obligations
	#number of obligations for: empty, Lx, Ly, ...
	obs = deque([1])
	#names of bound variables: ..., z, y, x
	vars = deque([''])
	for n in range(len(seq)):
		symbol = seq[n]
		#remove closed abstractions at start of loop
		while obs[-1] == 0:
			obs.pop()
			vars.popleft()
		#application adds a requirement to the current depth
		if symbol == '*':
			obs[-1] += 1
		#lambda adds a requirement to a new depth
		elif symbol[0] == L:
			obs[-1] -= 1
			obs.append(1)
			#add new lambda to stack
			vars.appendleft(symbol[1:-1])
		#variable removes a requirement from the current depth
		else:
			obs[-1] -= 1
			#replace bound variable name with index
			if symbol in vars:
				seq[n] = [vars.index(symbol)+1, False] #count_from
				#tuple of: variable index, special flag
				#(whether var in function is substituting,
				# or whether var in argument is free)
		#number of bound variables in scope at place of current symbol
		depth = len(obs)-1
	return seq
		
def rand_exp(seed = None):
	import random
	random.seed(seed)
	obs = deque([1])
	seq = deque()
	vars = 'abcdefghijklmnopqrstuvwxyz'
	while True:
		while obs[-1] == 0:
			obs.pop()
			if not obs:
				break
		if not obs:
			break
		depth = len(obs)-1
		n = random.randint(-1,depth)
		if n == -1:
			obs[-1] -= 1
			obs.append(1)
			prime = 0
			while depth >= len(vars):
				prime += 1
				depth -= len(vars)
			seq.append(L+vars[depth]+prime*'\''+'.')
		elif n == 0:
			obs[-1] += 1
			seq.append('*')
		else:
			obs[-1] -= 1
			seq.append([n,False])
	return seq
	

#~~~~DELTA FUNCTIONS~~~~

delta_dict = {'I':r'\x.x',
'K':r'\x.\y.x',
'S':r'\x.\y.\z.x z(y z)',
'B':r'\x.\y.\z.x(y z)',
'D':r'\x.\y.\z.\w.x y(z w)',
'M':r'\x.x x',
'OMEGA':r'M M',
'Y':r'\f.(\x.f(x x))(\x.f(x x))',

'T':r'\t.\f.t',
'F':r'\t.\f.f',
'N':r'\p.\t.\f.p f t',
'V':r'\p.\q.p p q',
'A':r'\p.\q.p q p',

'PAIR':r'\a.\b.\p.p a b',
'NIL': r'\x.\t.\f.t',
'EMPTY': r'\h.\t.F',
'HEAD': r'\l.l EMPTY NIL (l T)',
'TAIL': r'\l.l EMPTY NIL (l F)',
'ACCESS': r'\l.\n. HEAD (n TAIL l)',
'ACCINF':r'\l.\n.n (\l.l F) l T',

'ZERO' :r'\s.\z.z',
'SUCC' :r'\n.\s.\z.s(n s z)',
'1'    :r'\s.\z.s z',
'2'    :r'\s.\z.s(s z)',
'3'    :r'\s.\z.s(s(s z))',
'4'    :r'\s.\z.s(s(s(s z)))',
'5'    :r'\s.\z.s(s(s(s(s z))))',
'6'    :r'\s.\z.s(s(s(s(s(s z)))))',
'7'    :r'\s.\z.s(s(s(s(s(s(s z))))))',
'8'    :r'\s.\z.s(s(s(s(s(s(s(s z)))))))',
'9'    :r'\s.\z.s(s(s(s(s(s(s(s(s z))))))))',
'10'   :r'\s.\z.s(s(s(s(s(s(s(s(s(s z)))))))))',
'11'   :r'\s.\z.s(s(s(s(s(s(s(s(s(s(s z))))))))))',
'12'   :r'\s.\z.s(s(s(s(s(s(s(s(s(s(s(s z)))))))))))',
'13'   :r'\s.\z.s(s(s(s(s(s(s(s(s(s(s(s(s z))))))))))))',
'MULT' :r'\m.\n.\s.\z.m(n s)z',
'PRED' :r'\n.\s.\z.n (\x.\y.y(x s))(\x. z)I',
'ISZ'  :r'\n.n(\x.F)T',

'SR'   :r'\n.\s.\z.s n',
'PR'   :r'\n.n I ZERO',
'IT'   :r'Y (\r.\n.n (\n.SUCC (r n)) ZERO)',

'LEQ'  :r'\m.\n.ISZ (n PR (m SR ZERO))',
'EQ'   :r'\m.\n.A (LEQ m n) (LEQ n m)',
'QUOT' :r'Y (\r.\m.\n. LEQ (SUCC m) n ZERO (SUCC (r (n PR (m SR ZERO)) n)))',
'REM'  :r'Y (\r.\m.\n. LEQ (SUCC m) n (IT m) (r (n PR (m SR ZERO)) n))',

'INF': r'Y (\r.\n.PAIR n (r (SUCC n)))',

'SIEVE': r'Y (\r.\n.\s.\l.LEQ n (l T) (r (s SUCC n) s (LEQ (l T) n (l F) l)) (PAIR (l T) (r n s (l F))))',
'PRIMES': r'Y (\r.\l.PAIR (l T) (r (SIEVE ( (l T)) (l T) l)))'
}	


for definition in delta_dict:
	delta_dict[definition] = format(delta_dict[definition])

#~~~~BETA FUNCTIONS~~~~
#beta-reduction acts on the form * (Lx(...), ...)

def find_beta_redex(seq,first=True):
	if first:
		for n in range(len(seq)):
			if seq[n] == '*':
				if seq[n+1][0] == L:
					return n
	else:
		for n_ in reversed(range(len(seq))):
			if seq[n_][0] == L:
				if seq[n_-1] == '*':
					return n_-1
	return None
	
def beta_split(seq,start_redex):
	n = start_redex
	if seq[n] == '*':
		if seq[n+1][0] == L:
			obs = deque([1])
			i = n+1
			func = deque()
			#parse function only
			#break when obligation stack empty
			while True:
				while obs and obs[-1] == 0:
					obs.pop()
				if not obs:
					break
				if seq[i] == '*':
					obs[-1] += 1
				elif seq[i][0] == L:
					obs[-1] -= 1
					obs.append(1)
				else:
					obs[-1] -= 1
				depth = len(obs) - 1
				#handling free and substituting variables
				if type(seq[i][0]) == int:
					if seq[i][0] == depth:
						seq[i][1] = True
					elif seq[i][0] > depth:
						seq[i][1] = False
						seq[i][0] -= 1
						
				func.append(seq[i])
				del seq[i]
				
			obs = deque([1])	
			arg = deque()
			#parse argument
			while True:
				while obs and obs[-1] == 0:
					obs.pop()
				if not obs:
					break
				if seq[i] == '*':
					obs[-1] += 1
				elif seq[i][0] == L:
					obs[-1] -= 1
					obs.append(1)
				else:
					obs[-1] -= 1
				depth = len(obs) - 1
				#handling free variables
				if type(seq[i][0]) == int:
					if seq[i][0] > depth:
						seq[i][1] = True
						seq[i][0] -= 1
					else:
						seq[i][1] = False
						
				arg.append(seq[i])
				del seq[i]
			before = deque()
			for i in range(n):
				before.append(seq[0])
				seq.popleft()
			#remove outermost application symbol
			seq.popleft()
			after = seq.copy()
			return (before, func, arg, after)
	return None
				
def beta_reduce(func,arg):
	for n_ in reversed(range(len(func))):
		if type(func[n_][0]) == int:
			if func[n_][1]:
				depth = func[n_][0]
				del func[n_]
				for m_ in reversed(range(len(arg))):
					if type(arg[m_][0]) == int:
						if arg[m_][1]:
							value = [arg[m_][0]+depth,False]
						else:
							value = [arg[m_][0],False]
						func.insert(n_,value)
					else:
						func.insert(n_,arg[m_])
	#remove leading abstraction symbol
	func.popleft()
	reduct = func.copy()
	return reduct
	
#~~~~ETA FUNCTIONS~~~~		
# eta-reduction acts on the form Lx (*(...,x))

def find_eta_redex(seq,first=True):
	if first:
		for n in range(len(seq)):
			if seq[n][0] == L:
				if seq[n+1][0] == '*':
					return n
	else:
		for n_ in reversed(range(len(seq))):
			if seq[n_] == '*':
				if seq[n_-1][0] == L:
					return n_-1
	return None

def eta_reduce(seq,start_redex):
	seq_ = copy.deepcopy(seq)
	n = start_redex
	if seq_[n][0] == L:
		if seq_[n+1] == '*':
			obs = deque([1])
			i = n+2
			#parse left half of function body
			#... from template
			while True:
				while obs and obs[-1] == 0:
					obs.pop()
				if not obs:
					break
				if seq_[i] == '*':
					obs[-1] += 1
				elif seq_[i][0] == L:
					obs[-1] -= 1
					obs.append(1)
				else:
					obs[-1] -= 1
				depth = len(obs)
				#if x is free in ...
				if type(seq_[i][0]) == int:
					if seq_[i][0] == depth:
						return None
					elif seq_[i][0] > depth:
						seq_[i][0] -= 1
				i += 1

			if i == len(seq_) or seq_[i][0] != 1:
				return None
			else:
				#remove outer bound variable
				del seq_[i]
				#remove application
				del seq_[n+1]
				#remove outer abstraction
				del seq_[n]
			return seq_
	return None

#~~~~OUTPUT FUNCTIONS~~~~
#converts indices back to literals
def to_literal(seq):
	seq_l = seq.copy()
	obs = deque([1])
	vars = deque()
	for n in range(len(seq_l)):
		while obs[-1] == 0:
			obs.pop()
			vars.popleft()
		if seq_l[n] == '*':
			obs[-1] += 1
		elif seq_l[n][0] == L:
			while seq_l[n][1:-1] in vars:
				seq_l[n] = seq_l[n][:-1]+"\'." 
			vars.appendleft(seq_l[n][1:-1])
			obs[-1] -= 1 
			obs.append(1)
		else:
			obs[-1] -= 1
		depth = len(obs) - 1
		if type(seq_l[n][0]) == int:
			seq_l[n] = vars[seq_l[n][0]-1]
	return seq_l		

#literal (not indices) Polish to infix
#there are three special rules for reducing the number of parentheses:
#1) if multiple applications or abstractions occur in a row,
# only the last one gets parentheses (left associativity);
#2) if an abstraction occurs after an application,
# the former does not get parentheses (precedence);
#3) the last operation does not get parentheses
def infix(seq):
	seq_i = deque()
	while seq:
		symbol = seq.pop()
		special = False
		if len(seq) == 0:
			special = True
		elif seq[-1][0] == L:
			special = True
		elif symbol == '*' and seq[-1] == '*':
			special = True
		if special:
			if symbol == '*':
				left = seq_i.popleft()
				right = seq_i.popleft()
				seq_i.appendleft(left+' '+right)
			elif symbol[0] == L:
				body = seq_i.popleft()
				seq_i.appendleft(symbol+body)
			else:
				seq_i.appendleft(symbol)
		else:
			if symbol == '*':
				left = seq_i.popleft()
				right = seq_i.popleft()
				seq_i.appendleft('('+left+' '+right+')')
			elif symbol[0] == L:
				body = seq_i.popleft()
				seq_i.appendleft('('+symbol+body+')')
			else:
				seq_i.appendleft(symbol)
	return seq_i[0]