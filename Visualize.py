#!/usr/bin/env python

from Unsatisfactory import *
import sys

class DisplayBuffer( object ):
	def __init__( self, w, h ):
		self.buffer = []
		for j in range( w ):
			self.buffer.append( [None for i in range( h ) ])
		
		self.w = w
		self.h = h
		
	
	def write( self, x, y, ch ):
		if x < 0:
			return
		if y < 0:
			return
		
		if x >= self.w:
			return
		
		if y >= self.h:
			return
		
		self.buffer[x][y] = ch
	
	def read( self, x, y ):
		if x < 0:
			return False
		if y < 0:
			return False
		
		if x >= self.w:
			return False
		
		if y >= self.h:
			return False
		
		return self.buffer[x][y]
	
	
	def render( self ):
		for y in range( self.h ):
			for x in range( self.w ):
				if self.buffer[x][y] is not None:
					sys.stdout.write( self.buffer[x][y] )
				else:
					sys.stdout.write( " " )
			sys.stdout.write("\r\n")


JUNCTION_NONE = 0
JUNCTION_LEFT = 1
JUNCTION_RIGHT = 2

class OC(object):
	def __init__( self, term ):
		self.term = term
		self.junction = JUNCTION_NONE
		
	def draw( self, x, y, dbuf, continues ):
		status = {True: "*", False: " "}[self.term.eval()]
		symbol = "---[%s]---" % status
		
		if self.junction == JUNCTION_LEFT:
			symbol = "---[%s]---" % status
		elif self.junction == JUNCTION_RIGHT:
			symbol = "---[%s]---" % status
		
		elif self.junction == JUNCTION_LEFT | JUNCTION_RIGHT:
			symbol = "---[%s]---" % status
		
		
		for i in range( len( symbol ) ):
			dbuf.write( x + i, y, symbol[i] )
		
		namelen = min( len(self.term.name), 7 )
		
		for i in range( namelen):
			dbuf.write( x + i + 4 - namelen/2, y+1, self.term.name[i] )
		
		
		if (self.junction & JUNCTION_LEFT) != 0:
			dbuf.write( x, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x, y + p, "|" )
						else:
							dbuf.write( x, y + p, "+" )
							done = True
				p -= 1
		
		if (self.junction & JUNCTION_RIGHT) != 0 and not continues:
			dbuf.write( x+8, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x + 8, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x+8, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x+8, y + p, "|" )
						else:
							
							dbuf.write( x+8, y + p, "+" )
							done = True
				p -= 1
		
		
	def __str__( self ):
		return "--[ ]--"
	
	def __call__( self, junction ):
		self.junction |= junction
		return self

class NC( object ):
	def __init__( self, term ):
		self.term = term
		self.junction = False

	def draw( self, x, y, dbuf, continues ):
		status = {True: "X", False: "\\"}[not self.term.eval()]
		symbol = "---[%s]---" % status

		if self.junction == JUNCTION_LEFT:
			symbol = "---[%s]---" % status
		elif self.junction == JUNCTION_RIGHT:
			symbol = "---[%s]---" % status
		
		elif self.junction == JUNCTION_LEFT | JUNCTION_RIGHT:
			symbol = "---[%s]---" % status
	

		for i in range( len( symbol ) ):
			dbuf.write( x + i, y, symbol[i] )
		
		namelen = min( len(self.term.name), 7 )
		
		for i in range( namelen ):
			dbuf.write( x + i + 4 - namelen/2, y+1, self.term.name[i] )
		


		if (self.junction & JUNCTION_LEFT) != 0:
			dbuf.write( x, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x, y + p, "|" )
						else:
							dbuf.write( x, y + p, "+" )
							done = True
				p -= 1
		
		
		if (self.junction & JUNCTION_RIGHT) != 0 and (not continues):
			dbuf.write( x+8, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x + 8, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x+8, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x+8, y + p, "|" )
						else:
							
							dbuf.write( x+8, y + p, "+" )
							done = True
				p -= 1
		

	def __str__( self ):
		return "--[\\]--"

	def __call__( self, junction ):
		self.junction |= junction
		return self



class Wire( object ):
	def __init__( self, junction ):
		self.junction = junction

	def draw( self, x, y, dbuf, continues ):
		symbol = "---------"
		if self.junction == JUNCTION_RIGHT:
			symbol = "--------+"
		for i in range( len( symbol ) ):
			dbuf.write( x + i, y, symbol[i] )
		
		if (self.junction & JUNCTION_LEFT) != 0 and False:
			dbuf.write( x, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x, y + p, "|" )
						else:
							dbuf.write( x, y + p, "+" )
							done = True
				p -= 1
		
		if (self.junction & JUNCTION_RIGHT) != 0:
			dbuf.write( x+8, y, "+" )
			done = False
			p = -1
			while not done:
				ch = dbuf.read(x + 8, y + p )
				if ch == False:
					done = True
				else:
					if ch is None:
						dbuf.write( x+8, y + p, "|" )
					else:
						if ch in " |":
							dbuf.write( x+8, y + p, "|" )
						else:
							dbuf.write( x+8, y + p, "+" )
							done = True
				p -= 1
		

	def __str__( self ):
		return "-------"
			
class OutputCoil( object ):
	def __init__( self, name, expr ):
		self.name = name
		self.expr = expr			

	def draw( self, x, y, dbuf, continues ):
		status = {True: "*", False: " "}[self.expr.eval()]
		symbol = "----(%s)--" % status

		for i in range( len( symbol ) ):
			dbuf.write( x + i, y, symbol[i] )
		
		namelen = min( len(self.name), 7 )
		
		for i in range( namelen ):
			dbuf.write( x + i + 5 - namelen/2, y+1, self.name[i] )


		
def generate_ladder( expr ):
	if isinstance( expr, Expression ):
		if expr.op == AND:
			out = []
			out.extend( generate_ladder(expr.lhs) )
			out.extend( generate_ladder(expr.rhs) )
			return out	
		elif expr.op == OR:
			return [[generate_ladder(expr.lhs), generate_ladder(expr.rhs)]]
		elif expr.op == NOT:
			return [NC(expr.lhs)]
	else:
		return [OC(expr)]



def get_ladder_size( ladder ):
	w = 0
	h = 0
	for entry in ladder:
		if isinstance( entry, list ):
			lw = []
			lh = []
			for rung in entry:
				(qw, qh) = get_ladder_size( rung )
				lw.append( qw )
				lh.append( qh )
			w += max(lw)
			h += max(lh)
		else:
			w += 1
	return w, h + 1


def _render_ladder(emit, x, y, ladder, junction ):
	ecnt = 0
	for entry in ladder:
		ecnt += 1
		
		if isinstance( entry, list ):
			old_y = y
			
			max_width = 0
			for entry2 in entry:
				(w,h) = get_ladder_size( entry2 )
				if w > max_width:
					max_width = w
			
			cnt = 0
			for entry2 in entry:
				(w,h) = get_ladder_size( entry2 )
				_render_ladder( emit, x, y, entry2, JUNCTION_LEFT )
				for j in range( w, max_width ):
					if j != max_width - 1: 
						emit( x + j, y, Wire(JUNCTION_NONE) )
					else:
						emit( x + j, y, Wire(JUNCTION_RIGHT) )
				cnt += 1
				y += h
			y = old_y
			x += max_width
		else:
			if junction == JUNCTION_LEFT:
				emit( x, y, entry(JUNCTION_LEFT) )
				junction = JUNCTION_NONE
			
			if ecnt == len(ladder):
				emit( x, y, entry(JUNCTION_RIGHT) )
			else:
				emit( x, y, entry(JUNCTION_NONE) )
			x += 1
		
def render_ladder( ladder, outputName, outputExpr, width ):
	(maxw,maxh) = get_ladder_size( ladder )
	
	#grid = [[None]*(maxh) for i in range(maxw+1)]
	grid = [[None]*(maxh) for i in range(width)]
	
	def emit( x,y, value ):
		grid[x][y] = value
		
	_render_ladder( emit, 0,0, ladder, JUNCTION_NONE )
	
	emit( width - 1, 0, OutputCoil( outputName, outputExpr ) )
	for j in range( width - 2, 0, -1 ):
		if grid[j][0] != None:
			break
		else:
			grid[j][0] = Wire(JUNCTION_NONE)
	
	return grid
	
def draw_grid( grid ):
	
	W = len(grid) * 9
	H = (len(grid[0])) * 3
	
	W = 79
	
	dbuf = DisplayBuffer(W, H )
	for j in range( len(grid[0]) ):
		for i in range( len( grid ) ):
			if grid[i][j] is not None:
				if i < len(grid) - 1:
					if grid[i+1][j] is not None:
						grid[i][j].draw( i*9, j*3, dbuf, True )
					else:
						grid[i][j].draw( i*9, j*3, dbuf, False )
				else:
					grid[i][j].draw( i*9, j*3, dbuf, False )
	dbuf.render()

def visualize( name, expr ):
	ladder = generate_ladder( expr )
	grid = render_ladder( ladder, name, expr, 8 )
	draw_grid( grid )
	print ""
	print ""

if __name__ == "__main__":
	X = Term("X")
	Y = Term("Y")
	Z0 = Term("Z00")
	Z1 = Term("Z01")
	
	S = State("S")
	
	
	Y.set( False )
	X.set( False )
	

	Q = (X + (Y*-Z1+X)) * Z0 * Z1 * (X + Y)
	R = X * -Y * Z0 + S

	notQ = -Q

	S <<= X
	S >>= -X + Z0
	

	Q.demorgan()
	notQ.demorgan()
	R.demorgan()
	S.demorgan()

	print ""
	visualize( "Q", Q )
	visualize( "notQ", notQ )
	visualize( "R", R )

	visualize( "S_set", S.turn_on )
	visualize( "S_rset", S.turn_off )

