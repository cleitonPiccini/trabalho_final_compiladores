import csv
import os
import GL

from erro import *
from estado import *
from transicoes import *
from simbolo import *
from token import *
from goldpyser import *
from nodo import *
from simbSintatico import *


#funcao que recebe como parametro a reducao, os caracteres da fita e o codigo temporario da reduçao
#realiza operaçoes de açoes semanticas em produçoes
#retorna o codigo temporario da reducao
def acaoSemantica(r,caracs,cod):
	#global CONT_TEMP, TABELA_SIMBOLOS_SINTATICA

	if(r == 35 or r == 39 or r == 41 or r == 40): #adiciona à pilha
		cod.append(caracs[len(caracs)-1])

	if(r == 28 or r == 29 or r == 31 or r == 32): #cria um temporário com a operação
		temp = "temp" + str(GL.CONT_TEMP)
		GL.CODI.append(temp + " = " + 	cod[len(cod)-2] + " " + caracs[1] + " " + cod[len(cod)-1])
		cod.pop(len(cod)-1)
		cod.pop(len(cod)-1)
		cod.append(temp)
		GL.CONT_TEMP += 1

	if(r == 25): # final de produção
		simbolo = simbSintatico()
		simbolo.rotulo = caracs[len(caracs)-1]
		simbolo.val = cod[len(cod)-1]
		simbolo.tipo = "oper"
		GL.TABELA_SIMBOLOS_SINTATICA.append(simbolo)

	if(r == 38): # declaração de variável - atribui o tipo
		GL.CODI.append(cod[len(cod)-1] + " " + caracs[1])
		simbolo = simbSintatico()
		simbolo.rotulo = caracs[1]
		simbolo.val = cod[len(cod)-1]
		simbolo.tipo = "var"
		GL.TABELA_SIMBOLOS_SINTATICA.append(simbolo)
		cod.pop(len(cod)-1)

	if(r == 26): # atribuição entre duas variáveis
		GL.CODI.append(caracs[3] + " = " + caracs[1])
		simbolo = simbSintatico()
		simbolo.val = caracs[1]
		simbolo.rotulo = caracs[3]
		simbolo.tipo = "atrib"
		GL.TABELA_SIMBOLOS_SINTATICA.append(simbolo)
	return cod


#funcao que recebe como parametro uma linha do codigo intemediario e um grafo
#Gera nodos dessa linha no grafo
def geraNodos(lin,grafo):
	#global CONTNODO
	at1 = True
	at2 = True
	rot1 = 0
	rot2 = 0
	lin[4] = lin[4][:-1]

	for i in grafo:
		if(i.var == lin[2]):
			rot1 = i.pos
			at1 = False
		if(i.var == lin[4]):
			rot2 = i.pos
			at2 = False

	if at1 == True:
		nodo1 = nodo()
		nodo1.pos = GL.CONTNODO
		nodo1.var = lin[2]
		GL.CONTNODO += 1
		grafo.append(nodo1)

	if at2 == True:
		nodo2 = nodo()
		nodo2.pos = GL.CONTNODO
		nodo2.var = lin[4]
		GL.CONTNODO += 1
		grafo.append(nodo2)

	nodotemp = nodo()
	nodotemp.pos = GL.CONTNODO
	nodotemp.var = lin[0]
	nodotemp.op = lin[3]
	if at1 == True: nodotemp.filhos.append(nodo1.pos)
	else: nodotemp.filhos.append(rot1)
	if at2 == True: nodotemp.filhos.append(nodo2.pos)
	else: nodotemp.filhos.append(rot2)
	grafo[nodotemp.filhos[0]].pai.append(GL.CONTNODO)
	grafo[nodotemp.filhos[1]].pai.append(GL.CONTNODO)
	GL.CONTNODO+=1
	grafo.append(nodotemp)

#funcao que recebe como parametro um grafo e uma lista de nodos
#percorre o grafo em profundidade mais a esquerda
#fundamental para o processo de otimizaçao
def dfs(grafo, ordemInst):
	pilha = []
	pilha.append(ordemInst[len(ordemInst)-1])
	ar = False
	on  = False
	while(pilha):
		for aresta in pilha[len(pilha)-1].filhos:
			if(grafo[aresta] not in ordemInst and grafo[aresta].filhos):
				for pai in grafo[aresta].pai:
					if grafo[pai] in ordemInst:
						on = True
					else:
						on = False
						break
				if on == True:
					ordemInst.append(grafo[aresta])
					pilha.append(grafo[aresta])
					ar = True
					break
		if ar == False:
			pilha.pop(len(pilha)-1)
		on = False
		ar = False

#funçao recebe como parametro um grafo e uma pilha
#escreve o codigo otimizado no arquivo codOtimizado.txt
def codOtimizado(ordemInst,grafo):
	arquivo = open('codOtimizado.txt', 'a')
	k = len(ordemInst) - 1
	while(k >= 0):
		i = ordemInst[k]
		arquivo.write(str(i.var) + " = " + grafo[i.filhos[0]].var + " " + i.op + " " + grafo[i.filhos[1]].var + " " + "\n")
		k -= 1
	arquivo.close()


#funcao que realiza a otimizaçao do codigo intermediario
def otimizacao():
	grafo = []
	ordemInst = []

	with open("codIntermediario.txt", "r") as arquivo:
		for linha in arquivo:
			linha.strip('\n')
			lin = linha.split(" ")
			if len(lin) == 5:
				geraNodos(lin,grafo)
			else:
				arquivo = open('codOtimizado.txt', 'a')
				arquivo.write(str(linha))
				arquivo.close()

	for nodo in grafo:
		if(len(nodo.pai) == 0 and nodo not in ordemInst):
			ordemInst.append(nodo)
			dfs(grafo,ordemInst)
	codOtimizado(ordemInst,grafo)

#funcao que escrece o codigo intermediario gerado na analise sintatica no arquivo codIntermediario.txt
def geraCodI():
	arquivo = open('codIntermediario.txt', 'w')
	for i in GL.CODI:
		arquivo.write(i+'\n')
	arquivo.close()

#Faz a analise semantica recorrente da analise sintatica
#Apenas para o caso  de var = var
def analiseSemantica():
	val1 = ""
	val2 = ""
	eh_var = False
	for i in GL.TABELA_SIMBOLOS_SINTATICA:
		if i.tipo == "atrib":
			for j in GL.TABELA_SIMBOLOS_SINTATICA:
				if j.tipo == "var":
					if i.rotulo == j.rotulo:
						val1 = j.val
			for k in GL.TABELA_SIMBOLOS_SINTATICA:
				if k.tipo == "var":
					if i.val == k.rotulo:
						eh_var = True
						val2 = k.val
			if(val1 != val2 and eh_var):
				print("erro semantico na expressão: " + i.rotulo + "("+val1+")"+ " = " + ""+ i.val + "("+val2+")")
				print()
			eh_var = False

#imprime tabela LSR
def printSLR(tabela_slr):
	for i in tabela_slr:
		print(i.rotulo,end = " === ")
		for j in i.transicoes:
			print(j, end = "")
		print()

