#!/usr/bin/env python

import pprint
import itertools


AND = 1
OR = 2
NOT = 3
XOR = 4

class Expression( object ):
	def __init__( self, op, lhs, rhs ):
		self.op = op
		self.lhs = lhs
		self.rhs = rhs

	def __and__( self, rhs ):
		return Expression( AND, self, rhs )
	
	def __mul__( self, rhs ):
		return Expression( AND, self, rhs )
	
	def __or__( self, rhs ):
		return Expression( OR, self, rhs )
	
	def __add__( self, rhs ):
		return Expression( OR, self, rhs )
	
	def __neg__( self ):
		return Expression( NOT, self, None )
	
	def __not__( self ):
		return Expression( NOT, self, None )
		
	def __xor__( self, rhs ):
		return Expression( XOR, self, rhs )
	
	def eval( self ):
		if self.op == AND:
			return self.lhs.eval() and self.rhs.eval()
		elif self.op == OR:
			return self.lhs.eval() or self.rhs.eval()
		elif self.op == NOT:
			return not self.lhs.eval()
		elif self.op == XOR:
			return self.lhs.eval() ^ self.rhs.eval()
	
	def __nonzero__( self ):
		return self.eval()
	
	def depends(self):
		out = []
		
		if self.lhs is not None:
			out.extend( self.lhs.depends() )
		if self.rhs is not None:
			out.extend( self.rhs.depends() )
		
		# remove duplicates
		return list(set(tuple(out)))
		
	
	def __str__( self ):
		if self.op == AND:
			return "(%s AND %s)" % ( str(self.lhs), str(self.rhs) )
		elif self.op == OR:
			return "(%s OR %s)" % ( str(self.lhs), str(self.rhs) )
		elif self.op == NOT:
			return "(NOT (%s))" % str(self.lhs)
		elif self.op == XOR:
			return "(%s XOR %s)" % ( str(self.lhs), str(self.rhs) )

	def demorgan( self ):
		if self.op == NOT:
			if isinstance(self.lhs, Term):
				# nothing to do
				return
			else:
				if self.lhs.op == AND:
					lhs = Expression(NOT, self.lhs.lhs, None)
					rhs = Expression(NOT, self.lhs.rhs, None)
					self.lhs = lhs
					self.rhs = rhs
					self.op = OR
					self.lhs.demorgan()
					self.rhs.demorgan()
				
				elif self.lhs.op == OR:
					lhs = Expression(NOT, self.lhs.lhs, None)
					rhs = Expression(NOT, self.lhs.rhs, None)
					self.lhs = lhs
					self.rhs = rhs
					self.op = AND
					self.lhs.demorgan()
					self.rhs.demorgan()
				
				elif self.lhs.op == NOT:
					if isinstance( self.lhs.lhs, Term ):
						# mathematically unaesthetic
						self.op = AND
						self.rhs = self.lhs.lhs
						self.lhs = self.lhs.lhs
						# no need to continue
						return
						
					else:
						self.op = self.lhs.lhs.op
						self.rhs = self.lhs.lhs.rhs
						self.lhs = self.lhs.lhs.lhs
						self.lhs.demorgan()
						if self.rhs:
							self.rhs.demorgan()
						self.demorgan()
		else:
			self.lhs.demorgan()
			self.rhs.demorgan()
	
	def satisfy( self ):
		if self.op == NOT:
			return [(self.lhs, False)]
		
		elif self.op == OR:
			left = self.lhs.satisfy()
			right = self.rhs.satisfy()
			
			# test if we did actually generate duplicates
			if tuple(left) == tuple(right):
				return [left]
				
			return [left, right]
		
		elif self.op == AND:
			left = self.lhs.satisfy()
			
			#short-circuit evaluation, if lhs is empty
			if len(left) < 1:
				return []
			
			right = self.rhs.satisfy()
			out = []
			for l in left:
				for r in right:
					if isinstance( l, tuple ):
						raw_result = [l]
					else:
						raw_result = l
						
					if isinstance( r, tuple ):
						raw_result.append( r )
					else:
						raw_result.extend( r )
					
					is_ok = True
					result = []
					for entry in raw_result:
						if (entry[0], not entry[1]) in raw_result:
							is_ok = False
							break
						else:
							if entry not in result:
								result.append( entry )
					
					if is_ok:
						out.append( result )
					
			return out
			
			

class Term( object ):
	def __init__( self, name ):
		self.name = name
		self.value = True
	
	def set( self, value ):
		self.value = value
	
	def eval(self):
		return self.value
	
	def depends(self):
		return [self]
	
	def demorgan(self):
		pass
	
	def satisfy( self ):
		return [(self, True)]
	
	def __and__( self, rhs ):
		return Expression( AND, self, rhs )
	
	def __rand__( self, rhs ):
		return Expression( AND, self, rhs )

	
	def __mul__( self, rhs ):
		return Expression( AND, self, rhs )
	
	def __or__( self, rhs ):
		return Expression( OR, self, rhs )
	
	def __add__( self, rhs ):
		return Expression( OR, self, rhs )
	
	def __neg__( self ):
		return Expression( NOT, self, None )
	
	def __not__( self ):
		return Expression( NOT, self, None )
		
	def __xor__( self, rhs ):
		return Expression( XOR, self, rhs )
	
	def __str__(self):
		return self.name# + "[%s]" % self.value
	
	def __repr__(self):
		return "Term('%s')" % self.name
	
	def __nonzero__( self ):
		return self.eval()


class State( Term ):
	def __init__( self, name ):
		self.name = name
		self.turn_on = None
		self.turn_off = None
		self.value = False
	
	def demorgan( self ):
		self.turn_on.demorgan()
		self.turn_off.demorgan()
	
	def consistent( self ):
		left = set(self.turn_on.depends())
		right = set(self.turn_off.depends())
		
		#print ""
		#print "consistency:"
		#print "\tl:", left
		#print "\tr:", right
		
		common = left.intersection( right )
		# state turning on and off are fully independent
		# -> not guaranteed that both wouldn't be true at the same time
		
		if len(common) < 1:
			return False
		
		left = self.turn_on.satisfy()
		right = self.turn_off.satisfy()
		
		#print ""
		#print "satisfy:"
		#print "\tl:", left
		#print "\tr:", right
		
		# make sure that both on- and off-states are possible
		if len( left ) < 1:
			return False
		
		if len( right ) < 1:
			return False
		
		# be sure that on- and off-states cannot be true at the same time
		
		for lhs in left:
			for rhs in right:
				found = False
				for q in lhs:
					if q in rhs:
						found = True
					else:
						found = False
				if found:
					return False
				
				found = False
				for q in rhs:
					if q in lhs:
						found = True
					else:
						found = False
				if found:
					return False
						
		return True
	
	def eval( self ):
		left = self.turn_on.eval()
		right = self.turn_off.eval()
		if left:
			self.value = True
		
		if right:
			self.value = False
		
		return self.value
	
	def __irshift__( self, rhs ):
		self.turn_off = rhs
		return self
	
	def __ilshift__( self, rhs ):
		self.turn_on = rhs
		return self
	
	def __repr__(self):
		return "State('%s')" % self.name

class TransientEvent( Term ):
	def __init__( self, name ):
		self.name = name
		self.turn_on = None
		self.value = False

	def __ilshift__( self, rhs ):
		self.turn_on = rhs
		return self

	def demorgan( self ):
		self.turn_on.demorgan()
	
	def eval( self ):
		left = self.turn_on.eval()
		if not self.value and left:
			return True
			
		self.value = left
		return False
	
	def consistent( self ):
		sat = self.turn_on.satisfy()
		if len(sat) < 1:
			return False
		
		return True
	
	def __repr__(self):
		return "TransientEvent('%s')" % self.name
	
		

def analyze( relations ):
	var_map = {}
	for (name, relation) in relations.items():
		terms = relation.depends()
		for term in terms:
			if term not in var_map:
				var_map[term] = []
			var_map[term].append( name )
	pprint.pprint( var_map)
	print ""
	terms = var_map.keys()
	
	rels = {}
	for (name, relation) in relations.items():
		terms = tuple( sorted( relation.depends(), key = lambda t: t.name ) )
		
		if terms not in rels:
			rels[terms] = {}
		rels[terms][name] = relation
	
	for (terms, to_be_evaled) in rels.items():
		evals = {}
		for i in range( 2**len(terms) ):
			values = []
			for j in range( len( terms ) ):
				terms[j].set( (i & (1 << j)) > 0 )
				values.append((i & (1 << j)) > 0 )
			evals[tuple(values)] = {name: relation.eval() for (name, relation) in to_be_evaled.items()}
		print terms
		pprint.pprint( evals )
		print ""






### example

if __name__ == "__main__":
					
	X = Term("X")
	Y = Term("Y")
	Z = Term("Z")

	Q = X + Y
	P = X + (Y * Z)
	R = Z * (-Q )
	S = X * ((-(-(X+X))) * X)
	T = X * (-(-(-( -(-Z)))))

	print "Q :=", Q 
	print "P :=", P
	print "R :=", R
	print "S :=", S
	print "T :=", T
	print ""
	print "after De Morgan rewrite:"
	print ""

	Q.demorgan()
	P.demorgan()
	R.demorgan()
	S.demorgan()
	T.demorgan()

	print "Q :=", Q 
	print "P :=", P
	print "R :=", R
	print "S :=", S
	print "T :=", T
	print ""

	print ""
	print "Satify test"
	print "Q:", Q.satisfy()
	print "P:", P.satisfy()
	print "R:", R.satisfy()
	print "S:", S.satisfy()
	print "T:", T.satisfy()

	print ""
	print ""

	print "Q :=", Q, "->", Q.eval()
	print "P :=", P, "->", P.eval()
	print "R :=", R, "->", R.eval()
	print "S :=", S, "->", S.eval()
	print "T :=", T, "->", T.eval()

	print ""
	print "Q depends on", Q.depends()
	print "P depends on", P.depends()
	print "R depends on", R.depends()
	print "S depends on", S.depends()
	print "T depends on", T.depends()
	print ""
	analyze({
		'Q': Q,
		'R': R,
		'P': P,
		'S': S,
		'T': T,
		})

	print ""
	print ""

	A = State("A")
	B = State("B")

	A <<= -Q
	A >>= R

	B <<= Q * (-A)
	B >>= R

	print "Is A consistent?", A.consistent()
	print ""
	print "A :=", A.eval()
	print ""
	print "Is B consistent?", B.consistent()
	print ""
	print "B :=", B.eval()



