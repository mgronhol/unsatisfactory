#!/usr/bin/env python

from Unsatisfactory import *
from CodeGenerators import *



X = Term("X")
Y = Term("Y")
Z = Term("Z")

Q = X + Y
P = X + (Y * Z)
R = Z * (-Q )
S = X * ((-(-(X+X))) * X)
T = X * (-(-(-( -(-Z)))))

A = State("A")
B = State("B")

A <<= -Q
A >>= R

B <<= Q * (-A)
B >>= R


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
A.demorgan()
B.demorgan()

print "Q :=", Q 
print "P :=", P
print "R :=", R
print "S :=", S
print "T :=", T
print ""


print "Generating C code:"
print ""
print generate_c( {
	'Q': Q,
	'P': P,
	'R': R,
	'S': S,
	'T': T,
	'A': A,
	'B': B
	})


