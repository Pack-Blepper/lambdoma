# lambdoma
Command Line Lambda Calculator

This program performs computation by normalizing λ-expressions: for small arithmetic problems it attains ~1000 β-reductions per second.

Type /help after starting the program to see the valid commands.

# Predefined constants

## Literal Combinators:

I - Identity

K - Constant (alias of True)

S - "Fusion" Combinator

B - "Bluebird"

D - "Dove"

M - "Mockingbird"

OMEGA - Quine

Y - Fixed Point Combinator

## Booleans:

T - True

F - False

N,V,A - Not, Or, And; evoking the forms of ~,∨,∧

## Pairs:

PAIR - Applies a predicate to two elements

NIL - Function of one argument evaluating to True

EMPTY - Function of two arguments evaluating to False

HEAD,TAIL - Apply a pair to a predicate or take NIL

ACCESS - Iterate HEAD and TAIL prefixes

ACCINF - Iterate True and False postfixes

## Numerals:

SUCC,ZERO,1,2,...13 - Church numerals

PRED - Predecessor

  ### Scott Numerals:
 
  SR - Recursive Successor
  
  PR - Recursive Predecessor
  
  IT - Iterate

  ## Arithmetic
  
MULT - Multiply (Alias of B)

ISZ - Equals zero

LEQ - Not greater than

EQ - Equal to

QUOT - Quotient

REM - Remainder

INF - Infinite list

SIEVE,PRIMES - The Sieve of Eratosthenes; very slow for some reason—there are λ-expressions that list prime numbers much faster than this.
