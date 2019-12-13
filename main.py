# Academico: Cleiton Piccini
# Trabalho Final
# Disciplina: Compiladores

import csv
import os
import lex
import sin
import sem
import GL

from erro import *
from estado import *
from transicoes import *
from simbolo import *
from token import *
from goldpyser import *
from nodo import *
from simbSintatico import *

#__main__#

lex.openArq()
lex.determinizar()
lex.mortos()
lex.insereEstErro()
lex.gerarCSV()
lex.printErros(lex.lexic(),GL.ERRO_LEX)
lex.printTabSimb()

if(not GL.TABELA_ERROS):
	aceita = sin.analiseSintatica()
	if aceita:
		sem.analiseSemantica()
		sem.geraCodI()
		sem.otimizacao()