#!usr/bin python
#-*- coding: utf-8 -*-

__doc__ =  "Functions that enable collection of the informations from the data base, their presentation 
and z-score calculation."
__author__ = "Group of bioinformatics students @ AMU, Poznan"

import MySQLdb as my 
import Stemmer, sys
import math 

def stem(word):
    '''Function that returns the 'core' of the given word.'''
    
    stemmer = Stemmer.Stemmer('english')
    word_after = stemmer.stemWord(word)
    return word_after

# Przykladowe zapytania do bazy danych
def select_words(word, db_cursor):
    '''Function that selects the paragraphs with word-query.'''
    db_cursor.execute('SELECT PMID_LIST, NRALLAPPEARANCE FROM words WHERE WORD = %s', (word))
    return db_cursor.fetchall()
    
def select_paragraphs(nr_par, db_cursor):
    '''Function that selects the paragraphs with nr_par-query.'''
    db_cursor.execute('SELECT WORD_LIST FROM paragraphs WHERE PMID_PNR = %s', (nr_par))
    return db_cursor.fetchall()
    
def select_wcount(each_word, nr_par, db_cursor):
    '''Function that selects the paragraphs with nr_par-query.'''
    db_cursor.execute('SELECT NRPARAGAPPEARANCE FROM wcount WHERE WORD = %s AND PMID_PNR = %s', (each_word, nr_par))
    return db_cursor.fetchall()
    
def countall(db_cursor):
    db_cursor.execute('SELECT COUNT(*) FROM paragraphs')
    return db_cursor.fetchone()   

def zscore(word, correlated_word, db_cursor, file):
    '''
    Z-score pozwala obliczyc korelacje pomiedzy dwoma slowami, korzystajac ze wzoru:
    z-score = ( ( a - ( b * c / d) ) / ( pierwiastek_z ( c * ( ( d - c ) / ( d * d ) * b) ) ) )
    gdzie:
    b - liczba paragrafow, w ktorych wystapilo slowo z zapytania (word) - paragrafy te bedziemy okreslac,
    jako analizowane paragrafy 
    a - liczba paragrafow, w ktorych wystapilo skorelowane slowo (correlated_word), paragrafy te zostaly
    wybrane TYLKO z puli analizowanych paragrafow. Czyli wyszukujemy tych paragrafow, w ktorych wystapilo zarowno
    wyszukiwane, jak i skorelowane slowo.
    c - liczba paragrafow, w ktorych wystapilo skorelowane slowo (correlated_word), ale wybrana z puli WSZYSTKICH
    paragrafow znajdujacych sie w bazie danych
    d - ogolna liczba wszystkich paragrafow znajdujacych sie w bazie danych 
    '''
    
    word_occu = select_words(word, db_cursor)
    correl_word_occu = select_words(correlated_word, db_cursor)
    
    print word, word_occu
    print correl_word_occu
    if word_occu  and correl_word_occu :
	word_occu = word_occu[0][0].split(',')
	correl_word_occu = correl_word_occu[0][0].split(',')
	#common_par_num - liczba paragrafow, w ktorych wystepuje zarowno slowo szukane, jak i skorelowane.
	common_par_num = 0
    
	for pmid in correl_word_occu:
	    if pmid in word_occu:
		common_par_num +=1
	
	print common_par_num
	if common_par_num == 0:
	    return 'Brak korelacji!'
	
	a = float(common_par_num)
	b = float(len(word_occu))
	c = float(len(correl_word_occu))
	d = float(countall(db_cursor)[0])
	
	zscore = (a - ( b * c / d)) / math.sqrt( c * ( ( d - c ) / (d * d)  * b) )
	#return correlated_num
	file.write('Z-score dla dwoch slow: ' + word + ' ' + correlated_word + ' wynosi: ' + zscore + '\n')
	return zscore
    else:
	return 'z-score nie zostal policzony poniewaz szukane slowo nie wystepuje w bazie danych'
    
def show_words_from_table_words(word, db_cursor, wanted_word, file):
    # result is a list of touples - [(szukane słowo, lista paragrafów, liczba wystąpień słowa we wszystkich artykułach)]
    result1 = select_words(word, db_cursor)
    list_paragraphs = ''
    numb_all_appear = 0 
    if len(result1) == 0:
	print "Nie odnaleziono szukanego slowa w bazie danych!"
    else:
	list_paragraphs = ''
	numb_all_appear = 0 
	list_paragraphs = result1[0][0]
	numb_all_appear = result1[0][1]

	print 'Szukane słowo to: ', wanted_word,'\n\nWystępuje ono w następujących paragrafach: ', list_paragraphs, '\n\nWe wszystkich artykułach wystepuje ', numb_all_appear, ' razy/raz.\n\n'
	tekst = 'Poszukiwane słowo to: ' + wanted_word +'\n\nWystępuje w następujących paragrafach: ' + list_paragraphs + '\n\nWe wszystkich artykułach wystepuje ' + str(numb_all_appear) + ' razy/raz.\n\n'
	file.write(tekst)

	return list_paragraphs

def show_words_from_paragraphs(word, list_p, cut_v, db_cursor, wanted_word, file):
  '''Function that returns the statistics of words from paragraphs in which word-query appears.'''
  if list_p == None:
      print "Lista paragrafow jest pusta! Dalsza statystyka nie została przeprowadzona!"
  else:
      list_paragraphs_div = list_p.split(',')
      #split the pmid_list record into single pmid_pnr 
      for nr_par in list_paragraphs_div:
	  #select from db word_list for given pmid_pnr
	  result2 = select_paragraphs(nr_par, db_cursor)
	  print '\n\nW paragrafie ', nr_par, ' znajdują się następujące słowa: ', result2[0][0], '\n\n','Wartosc graniczna dla przeprowadzanych statystyk to: ',cut_v,'\nSlowa, ktorych liczba wystapien jest wieksza niz ta wartosc nie beda brane pod uwage w statystykach. \nSlowa z tego paragrafu i liczba ich wystapien:'
	  tekst2 = '\n\nW paragrafie ' + nr_par + ' znajdują się następujące słowa: ' + result2[0][0] + '\n\n' + 'Wartosc graniczna dla przeprowadzanych statystyk to: ' + str(cut_v) + '\nSlowa, ktorych liczba wystapien jest wieksza niz ta wartosc nie beda brane pod uwage w statystykach.\nSlowa z tego paragrafu i liczba ich wystapien:\n'
	  file.write(tekst2)
	  #split the word_list to make the words statistics
	  wordlist_div = result2[0][0].split(',')
        
	  for each_word in wordlist_div:
	      try:
		  #get the nr of word appearance in a given paragraph
		  result3 = select_wcount(each_word, nr_par, db_cursor)
		  #If nr of appearance is bigger then cut_v display the word and #
		  if int(result3[0][0]) > cut_v:
		      tekst3 = '\n> ' + each_word + ' -- ' + str(result3[0][0]) + ' razy.'
		      file.write(tekst3)
		      print '> ', each_word, ' -- ', result3[0][0], ' razy.'
		  else: pass
	      except: pass
