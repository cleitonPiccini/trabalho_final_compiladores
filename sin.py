
import csv
import os
import lex
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


#Faz a analise sintatica do codigo
#retorna verdadeiro caso a analise sintatica ocorra com sucesso
#retorna falso caso contrario
def analiseSintatica():
	#global TABELA_SIMBOLOS
	cod = []
	tabela_slr = read_from_xml("grammar.xml")

	prods = get_productions_from_xml("grammar.xml")
	pilha = []
	pilha.append('0')
	indice = 0
	reconhece = True
	aceita = False
	LINHA = 0
	ERRO = ""
	while(reconhece == True and aceita == False):
		if(indice != len(GL.TABELA_SIMBOLOS)):
			LINHA = GL.TABELA_SIMBOLOS[indice].linha
			pos_fita = GL.TABELA_SIMBOLOS[indice].token
			pos_fita = pos_fita[:-1]
			token = GL.TABELA_SIMBOLOS[indice].eh_token
		else:
			token = True
			pos_fita = "EOF"

		pos_pilha = int(pilha[len(pilha)-1])
		op = " "
		pos_fita2 = " "

		if token == False:
			pos_fita2 = "var"
		else:
			pos_fita2 = pos_fita

		for i in tabela_slr:
			if i.rotulo == pos_fita2:
				op = i.transicoes[pos_pilha]

		tipo = op[:1]
		if(tipo == 'X'):
			ERRO = pos_fita
			reconhece = False

		elif(tipo == 'T'):
			t = op[1:]
			pilha.append(pos_fita)
			pilha.append(t)
			indice += 1

		elif(tipo == 'R'):
			r = int(op[1:])
			tam = 2 * int(prods[r].tam)
			nt = int(prods[r].regra)
			caracs = []

			while(tam > 0):
				if(tam % 2 == 1):
					caracs.append(pilha[len(pilha)-1])
				pilha.pop(len(pilha)-1)
				tam -= 1
			cod = sem.acaoSemantica(r,caracs,cod)
			pos = int(pilha[len(pilha)-1])
			salto = tabela_slr[nt].transicoes[pos]
			pilha.append(str(tabela_slr[nt].rotulo))
			pilha.append(str(salto))

		elif(tipo == 'A'):
			aceita = True

	if aceita == False:
		er = erro()
		er.linha = LINHA
		er.token = ERRO
		er.cod_erro = GL.ERRO_SINTATICO
		GL.TABELA_ERROS.append(er)
		printErros(False,GL.ERRO_SINTATICO)
	else:
		printTabSimbSint()
		lex.printErros(True,GL.ERRO_SINTATICO)
	return aceita

#Imprime tabela de simbolos da etapa de analise sintatica
def printTabSimbSint():
	#global TABELA_SIMBOLOS_SINTATICA
	print("------TABELA DE SÍMBOLOS------")
	print()
	for i in GL.TABELA_SIMBOLOS_SINTATICA:
		print("Rótulo = " + i.rotulo + " Valor = " + i.val, " Tipo = " + i.tipo)
	print()
