#!/usr/bin/env python


class Interval( object ):
	def __init__( self, left, right ):
		self.left = left
		self.right = right
		
		if self.left > self.right:
			self.left, self.right = self.right, self.left
		
		
	def is_in( self, point ):
		return (point >= self.left) and (point <= self.right)
	
	def __contains__(self, point):
		return self.is_in( point )
	
	def merge_or( self, other ):
		if (other.left in self) and (other.right in self):
			return Interval( self.left, self.right )
		
		if (self.left in other) and (self.right in other):
			return Interval( other.left, other.right )
		
		if self.left in other:
			return Interval( other.left, self.right )
		elif self.right in other:
			return Interval( self.left, other.right )
		else:
			return IntervalCollection([ Interval( self.left, self.right), Interval(other.left, other.right) ])
		
		
	
	def merge_and( self, other ):
		if (self.left in other) and (self.right in other):
			return Interval( self.left, self.right )
		
		if (other.left in self) and (other.right in self):
			return Interval( other.left, other.right )
		
		if self.right in other:
			if other.left in self:
				return Interval( other.left, self.right )
			else:
				return Interval( None, None )
		
		elif other.right in self:
			if self.left in other:
				return Interval( self.left, other.right )
			else:
				return Interval( None, None )
		
		else:
			return Interval( None, None )
	
	def __str__( self ):
		if self.left is None:
			return "[]"
		
		return "[%s, %s]" % ( str(self.left), str(self.right) )
	
	def is_empty( self ):
		return (self.left is None) or (self.right is None)

	def is_sane( self ):
		if self.left == float("inf"):
			return False
		
		elif self.right == float("-inf"):
			return False
		
		else:
			return True


	def __mul__( self, rhs ):
		return self.merge_and( rhs )
	
	def __add__( self, rhs ):
		return self.merge_or( rhs )

	def __neg__( self ):
		return IntervalCollection([Interval(float("-inf"), self.left), Interval(self.right, float("inf"))])

class IntervalCollection( object ):
	def __init__( self, intervals ):
		tmp = []
		
		if isinstance( intervals, IntervalCollection ):
			tmp = intervals.intervals
		else:			
			for entry in intervals:
				if isinstance( entry, IntervalCollection ):
					tmp.extend( entry.intervals )
				else:
					tmp.append( entry )
		
		self.intervals = [interval for interval in tmp if (not interval.is_empty()) and interval.is_sane()]
			
	def is_in( self, point ):
		for interval in self.intervals:
			if point in interval:
				return True
		return False
	
	def __contains__( self, point ):
		return self.is_in( point )
	
	def __add__( self, rhs ):
		results = []
		if isinstance( rhs, Interval ):
			results = [lhs + rhs for lhs in self.intervals]
		else:
			for A in self.intervals:
				for B in rhs.intervals:
					results.append( A + B )
			
			if len( results ) < 2:
				return IntervalCollection( results )
		
		ic = IntervalCollection( results )
		results = ic.intervals
		done = False
		while not done:		
			sresults = sorted( results, key = lambda x:x.left)
			will_simplify = []
			for i in range( len( sresults) ):
				A = sresults[i]
				B = sresults[(i+1) % len(sresults)]
				if isinstance(A+B, Interval ):
					will_simplify.append( (i, (i+1) % len(sresults)) )
			#print "will_simplify", will_simplify
			if len( will_simplify ) > 0:
				excluded = [will_simplify[0][0], will_simplify[0][1]]
				new_results = []
				for i in range( len(sresults) ):
					if i not in excluded:
						new_results.append( sresults[i] )
				new_results.append( sresults[will_simplify[0][0]] + sresults[will_simplify[0][1]] )
				results = new_results
			else:
				done = True
				
		return IntervalCollection( results )
	
	def __mul__( self, rhs ):
		if isinstance( rhs, Interval ):
			return IntervalCollection( [lhs * rhs for lhs in self.intervals] )
		else:
			results = []
			for A in self.intervals:
				for B in rhs.intervals:
					results.append( A * B )
			return IntervalCollection( results )
		
	def __str__( self ):
		if len( self.intervals ) < 1:
			return "[]"
		else:
			return ",".join([ str(interval) for interval in self.intervals])
	
	def __neg__( self ):
		if len( self.intervals ) < 2:
			return IntervalCollection( -self.intervals[0] )
		
		sintervals = sorted( self.intervals, key = lambda x:x.left )
		
		result = -sintervals[0]
		for interval in sintervals[1:]:
			result = result * (-interval)
		return result



#A = Interval( 0, 1 )
#B = Interval( 2, 3 )
#C = Interval( 2.5, 3.5 )
#D = Interval( 3.75, 4.5 )
#
#
#print (A + B) + C + D
#print (A + B) * C + D
#print ""
#print ""


class IntervalExpression( object ):
	def __init__( self, var, interval):
		self.var = var
		self.interval = interval
		
	def __add__( self, rhs ):
		return IntervalExpression( self.var, self.interval + rhs.interval )
	
	def __mul__( self, rhs ):
		result = self.interval * rhs.interval
		if isinstance( result, Interval ):
			result = IntervalCollection( [result] )
		return IntervalExpression( self.var, result )
	
	def __str__( self ):
		out = []
		for interval in self.interval.intervals:
			if interval.left == float("-inf"):
				out.append( "(%s < %s)" % (str(self.var), str(interval.right) ) )
			elif interval.right == float("inf"):
				out.append( "(%s > %s)" % ( str(self.var), str(interval.left) ) )
			else:
				if interval.left == interval.right:
					out.append( "(%s = %s)" % (str(self.var), str(interval.left) ) )
				else:
					out.append( "(%s < %s < %s)" % (str(interval.left), str(self.var), str(interval.right) ) )
		
		if len( out ) < 1:
			return "[]"
		
		return " OR ".join(out)
	
	def eval( self ):
		return self.var.value in self.interval			

	def __neg__( self ):
		return IntervalExpression( self.var, -self.interval )

class Variable( object ):
	def __init__( self, name ):
		self.name = name
		self.value = 0
	
	def set( self, value ):
		self.value = value
	
	def __str__( self ):
		return self.name
	
	def __gt__( self, rhs ):
		return IntervalExpression( self, IntervalCollection([Interval( rhs, float("inf") )]) )
	
	def __lt__( self, rhs ):
		return IntervalExpression( self, IntervalCollection([Interval( float("-inf"), rhs )]) )
	


#X = Variable("X")
#
#eq = (X < 10) * (X > 5) + (X < -5)
#
#print eq
#print eq.eval()
##X.set(-10)
#print eq.eval()
#print -eq

#t0 = Variable("T0")
#it = (t0 > 50) * (t0 < 120)
#it2 = -(t0 > 130)

#print it
#print it2
#print ""
#print it*it2

	
