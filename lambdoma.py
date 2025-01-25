import re, string, os
from collections import deque
from lambdoma_lib import *

#console_in - string, infix notation
#seq_i - deque, infix notation
#seq   - deque, prefix (Polish) notation

trace = True
showcount = False
strict = False
os.system('color')
color_beta = '\x1b[38;5;6m'
color_eta  = '\x1b[38;5;220m'
color_delta = '\x1b[38;5;7m'

while True:
	print('\n')
	console_in = input('>')
	if console_in.split()[0] == '/help':
		print('''List of actions:
		
<exp> 		: Evaluate an expression
ANS		: Recall the last result
<NAME> = <def> 	: Add a term to the dictionary
/dict 		: Show list of defined terms
/notrace 	: Toggle showing intermediate β-reductions
/count 		: Toggle showing number of β-reductions
/strict 	: Toggle normal/strict order evaluation
/random <seed> 	: Evaluate a random closed expression
/help 		: Show list of actions
CTRL-C		: Interrupt evaluation
''')
	elif '=' in console_in:
		term = console_in[:console_in.index('=')]
		term = term.replace(" ","")
		definition = console_in[console_in.index('=')+1:]
		delta_dict[term] = format(definition)
	elif console_in.split()[0] == '/notrace':
		trace = not trace
		print('Trace',['disabled','enabled'][trace])
	elif console_in.split()[0] == '/dict':
		for term in delta_dict:
			print(term + '\t' + delta_dict[term])
	elif console_in.split()[0] == '/count':
		showcount = not showcount
		print('Count of β-reductions',['hidden','shown'][showcount])
	elif console_in.split()[0] == '/strict':
		strict = not strict
		print('Using',['normal','strict'][strict]+'-order reduction')
	else:
		count = 0
		if console_in.split()[0] == '/random':
			if len(console_in.split()) > 1:
				seq = rand_exp(console_in.split()[1])
			else:
				seq = rand_exp()
			print('\n  | '+infix(to_literal(seq)))
		else:
			console_in = format(console_in)
			
			delta = False
			while re.findall(lookup,console_in):
				for element in re.findall(lookup,console_in):
					if element in delta_dict:
						console_in = re.sub(f'\({element}\)',f'({delta_dict[element]})',console_in)
						delta = True
					else:
						print(console_in)
						raise SyntaxError('Undefined term')
			seq_i = in_split(console_in)
			seq = polish(seq_i)
			seq = to_numeral(seq)
				
			if delta:
				print(color_delta+'\nδ | '+infix(to_literal(seq))+'\x1b[0m')
			else:
				print('\n  | '+infix(to_literal(seq)))
		
		try:
			via_beta = False
			while True:
				b = find_beta_redex(seq,not strict)
				if b == None:
					if not trace:
						if via_beta:
							print(color_beta+'β |',infix(to_literal(seq))+'\x1b[0m')
						print(color_beta,count,'\x1b[0m')
					break
				else:
					count += 1
					via_beta = True
					before, func, arg, after = beta_split(seq,b)
					reduct = beta_reduce(func,arg)
					seq = before + reduct + after
					if trace:
						print(color_beta+'β |',infix(to_literal(seq))+'\x1b[0m')
						if showcount:
							print(color_beta,count,'\x1b[0m')
					
			for term in delta_dict:
				if len(seq) == len(to_numeral(polish(in_split(delta_dict[term])))):
					match = True
					for n in range(len(seq)):
						if type(seq[n]) == str and seq[n][0] in string.ascii_lowercase:
							if seq[n] != to_numeral(polish(in_split(delta_dict[term])))[n]:
								match = False
								break
						elif seq[n][0] != to_numeral(polish(in_split(delta_dict[term])))[n][0]:
							match = False
							break
					if match:
						print(color_delta+'δ |',term+'\x1b[0m')

			while True:
				h = find_eta_redex(seq,not strict)
				if h == None:
					delta_dict['ANS'] = format(infix(to_literal(seq)))
					break
				else:
					reduct = eta_reduce(seq,h)
					if reduct != None:
						seq = reduct
						print(color_eta+'η |',infix(to_literal(seq))+'\x1b[0m')
					else:
						delta_dict['ANS'] = format(infix(to_literal(seq)))
						break

				for term in delta_dict:
					if len(seq) == len(to_numeral(polish(in_split(delta_dict[term])))):
						match = True
						for n in range(len(seq)):
							if type(seq[n]) == str and seq[n][0] in string.ascii_lowercase:
								if seq[n] != to_numeral(polish(in_split(delta_dict[term])))[n]:
									match = False
									break
							elif seq[n][0] != to_numeral(polish(in_split(delta_dict[term])))[n][0]:
								match = False
								break
						if match:
							print(color_delta+'δ |',term+'\x1b[0m')
		except KeyboardInterrupt:
			if showcount:
				print(color_beta,count,'\x1b[0m')
			else:
				print('\x1b[0m')
			continue