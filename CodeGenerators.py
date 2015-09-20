#!/usr/bin/env python

from Unsatisfactory import *

def c_slugify( name ):
		return name.replace( " ", "_" ).replace( "-", "_" )
	

def c_gensym( entry ):
	
	if isinstance( entry, TransientEvent ):
		return "engine->EVENT_%s" % c_slugify( entry.name )
	
	if isinstance( entry, State ):
		return "engine->STATE_%s" % c_slugify( entry.name )
	
	if isinstance( entry, Term ):
		return "engine->TERM_%s" % c_slugify( entry.name )


def c_expand_expression( expr ):
	if isinstance( expr, Term ):
		return "(" + c_gensym( expr ) + ")"
		
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
	
	defines = []
	outputs = []
	states = []
	
	for (key, value) in clauses.items():
		if not isinstance( value, State ):
			outputs.append( key )
		else:
			states.append( value )
		defines.extend( value.depends() )
		
	
	defines = sorted( list( set( defines ) ), key = lambda x:repr(x) )
	
	out += "/* Defines */ \n"
	out += "#define TRUE\t(1)\n"
	out += "#define FALSE\t(0)\n"
	out += "\n"
	out += "\n"
	out += "typedef struct RuleEngine { \n"
	out += "\n"
	out += "\t/* Inputs */ \n"
	for entry in defines:
		if not isinstance( entry, State ):
			out += "\tuint8_t %s;\n" %  ( c_gensym(entry).replace("engine->", "") )	
	out += "\n"
	out += "\t/* Outputs */ \n"
	for entry in outputs:
		out += "\tuint8_t %s;\n" %  ( entry )
	out += "\n"
	out += "\t/* States */ \n"
	for entry in states:
		out += "\tuint8_t %s;\n" % ( c_gensym(entry).replace("engine->", "") )	
	out += "\n"	
	out += "\t} rule_engine_t; \n"
	out += "\n"
	for entry in defines:
		if (not isinstance( entry, State )) and (not isinstance( entry, TransientEvent )):
			out += "void rule_engine_update_%s( uint8_t value ){ %s = (value == TRUE); }\n" % ( c_slugify(entry.name), c_gensym(entry) )

	out += "\n"
	out += "void rule_engine_run( rule_engine_t *engine ){ \n"
	out += "\n";
	for (key, value) in clauses.items():
		if isinstance( value, State ):
			out += "\tuint8_t %s_on = 0;\n" % key 
			out += "\tuint8_t %s_off = 0;\n" % key 
	out += "\n"
	out += "\n"
	out += "\t/* Logic */\n"
	states = []
	for (key, value) in clauses.items():
		if isinstance( value, Expression ):
			out += "\tengine->%s = %s;\n" %( key, c_expand_expression(value) ) 
		elif isinstance( value, State ):
			out += "\t%s_on = %s;\n" %( key, c_expand_expression(value.turn_on) ) 
			out += "\t%s_off = %s;\n" %( key, c_expand_expression(value.turn_off) ) 
			out += "\n"
			
			states.append( (key, value) )
	
	out += "\n\n"
	out += "\t/* State transitions */\n"
	for (key, value) in states:
		out += "\tif( %s_on == TRUE) {\n" % ( key )
		out += "\t\t%s = TRUE;\n" % c_gensym(value)
		out += "\t\t}\n"
		out += "\tif( %s_off == TRUE) {\n" % ( key )
		out += "\t\t%s = FALSE;\n" % c_gensym(value)
		out += "\t\t}\n"
		out += "\n"
	
	out += "\t}\n"
	
		
		
	return out
