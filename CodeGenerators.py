#!/usr/bin/env python

from Unsatisfactory import *

def c_slugify( name ):
		return name.replace( " ", "_" ).replace( "-", "_" )
	

def c_gensym( entry ):
	
	if isinstance( entry, TransientEvent ):
		return "EVENT_%s" % c_slugify( entry.name )
	
	if isinstance( entry, State ):
		return "STATE_%s" % c_slugify( entry.name )
	
	if isinstance( entry, Term ):
		return "TERM_%s" % c_slugify( entry.name )


def c_expand_expression( expr ):
	if isinstance( expr, Term ):
		return c_gensym( expr )
		
	if expr.op == AND:
		left = c_expand_expression( expr.lhs )
		right = c_expand_expression( expr.rhs )
		return "(%s && %s)" % (left, right)
	
	elif expr.op == OR:
		left = c_expand_expression( expr.lhs )
		right = c_expand_expression( expr.rhs )
		return "(%s || %s)" % (left, right)
	
	elif expr.op == NOT:
		left = c_expand_expression( expr.lhs )
		return "(!%s)" % left

	elif expr.op == XOR:
		left = c_expand_expression( expr.lhs )
		right = c_expand_expression( expr.rhs )
		return "(%s ^ %s)" % (left, right)

def generate_c( clauses ):
	out = ""
	
	states = []
	for (key, value) in clauses.items():
		if isinstance( value, Expression ):
			out += "%s = %s;\n" %( key, c_expand_expression(value) ) 
		elif isinstance( value, State ):
			out += "%s_on = %s;\n" %( key, c_expand_expression(value.turn_on) ) 
			out += "%s_off = %s;\n" %( key, c_expand_expression(value.turn_off) ) 
			out += "\n"
			
			states.append( (key, value) )
	
	out += "\n\n"
	
	for (key, value) in states:
		out += "if( %s_on == TRUE) {\n" % ( key )
		out += "\t%s = TRUE;\n" % c_gensym(value)
		out += "\t}\n"
		out += "if( %s_off == TRUE) {\n" % ( key )
		out += "\t%s = FALSE;\n" % c_gensym(value)
		out += "\t}\n"
		out += "\n"
		
	
		
		
	return out
