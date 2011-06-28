1. Opis bazy danych

Plik bioinfodb.sql zawiera stworzona przez nas baze danych. Zawiera ona 8 przykladowych artykulow 
(archiwum plos_articles.zip), poniewaz wieksza ilosc bardzo spowalnia przeszukiwanie bazy.
Najpierw nalezy otworzyc mysql i stworzyc pusta baze danych:
mysql> create database bioinfo;
Nastepnie zamykamy mysql i w terminalu wpisac polecenie:
> mysql --user=name_of_user --password bioinfo < bioinfodb.sql
Nastepnie wchodzimy do mysql i definiujemy baze danych, na ktorej bedziemy pracowac:
mysql> use bioinfo; 

a) Baza danych sklada sie z 3 tabel: paragrahps, words, wcount (poszczegolne tabele
zastepuja osobne bazy danych). Zeby wyswietlic tabelki nalezy uzyc polecenia mysql:
mysql> show tables; 
+-------------------+
| Tables_in_bioinfo |
+-------------------+
| paragraphs        |
| wcount            |
| words             |
+-------------------+
3 rows in set (0.00 sec)

b) Tabela words zawiera informacje na temat paragrafow (PMID_LIST), w ktorych wystepuje dane slowo(WORD)
oraz ogolna liczbe wystapien tego slowa w calej bazie danych:
mysql> show columns from words;
+-----------------+-------------+------+-----+---------+-------+
| Field           | Type        | Null | Key | Default | Extra |
+-----------------+-------------+------+-----+---------+-------+
| WORD            | varchar(50) | NO   | PRI | NULL    |       |
| PMID_LIST       | longtext    | NO   |     | NULL    |       |
| NRALLAPPEARANCE | bigint(20)  | NO   |     | NULL    |       |
+-----------------+-------------+------+-----+---------+-------+
3 rows in set (0.00 sec)

c) Tabela paragrahps zawiera informacje na temat listy slow (WORD_LIST) w danym paragrafie kazdego artykulu 
(PMID_PNR, gdzie PMID to nr artykulu, a PNR to numer paragrafu):
mysql> show columns from paragraphs;
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| PMID_PNR  | varchar(20) | NO   | PRI | NULL    |       |
| WORD_LIST | longtext    | NO   |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
2 rows in set (0.00 sec)

d) Tabela wcount zawiera informacje na temat czestosci (NRPARAGAPPEARANCE) wystepowania danego slowa (WORD)
w konkretnym paragrafie konkretnego artykulu (PMID_PNR):
mysql> show columns from wcount;
+-------------------+-------------+------+-----+---------+-------+
| Field             | Type        | Null | Key | Default | Extra |
+-------------------+-------------+------+-----+---------+-------+
| PMID_PNR          | varchar(20) | NO   | PRI | NULL    |       |
| WORD              | varchar(50) | NO   | PRI | NULL    |       |
| NRPARAGAPPEARANCE | bigint(20)  | NO   |     | NULL    |       |
+-------------------+-------------+------+-----+---------+-------+
3 rows in set (0.00 sec)
 
2. Opis programu xml_parser6c.py
Program jest parserem do publikacji w formacie xml. Opis poszczegolnych funkcji znajduje sie w programie
bezposrednio pod linia ich definicji.

Opis dzialania algorytmu:
- z pliku xml algorytm pobrany zostaje artykul (istotny jest tytul i body artykulu, a nieistotne sa np. referencje;
- interesujace czesci (wybrane w poprzednim punkcie) dzielone sa na paragrafy;
- z kazdego paragrafu usuwane sa stopwords (stopwords2.txt), znaki interpunkcyjne z konca i poczatku
stringow oraz niestandardowe znaki zaczynajace sie na &#x, ktore wystepuja osobno, na koniec pozostale slowa
zamieniane sa na ich podstawy slowotworcze
- algorytm zwraca 3-elementowa krotke ('pmid', 'nr paragrafu', 'lista slow wystepujacych w danym paragrafie'),
na przyklad: 
('16103898', 1, ['ab', 'initio', 'predict', 'transcript', 'factor', 'target', 'structur', 'knowledg'])

Parser ten wykorzystywany jest przy robieniu insertow do bazy danych, ale moze byc uzywany,
jako niezalezny program.
Nalezy wtedy odkomentowac fragment, znajdujacy sie na koncu pliku xml_parser6c.py:

if __name__ == '__main__':
    xml = XmlParser()
    xml_doc = open('nazwa_pliku_zawierajacego_artykul_w_formacie_xml.nxml','r').read()
    bs_doc = bs(xml_doc)
    xml_doc_important = xml.get_important_parts(xml.important_parts_list, bs_doc)
    paragraphs_list = xml.get_paragraphs(xml_doc_important)
    cleaned_tuples = xml.remove_junk(xml.get_text_from_paragraphs(xml_doc_important, bs_doc))
    #returns one list of touples from one .nxml file
    print cleaned_tuples[0]

i uruchomic program w terminalu:
> python xml_parser6c.py

3. Opis programu insertdb.py
W celu ulatwienia wprowadzania artykulow do bazy danych stworzylismy skrypt insertdb.py.
Opis poszczegolnych funkcji znajduje sie w programie bezposrednio pod linia ich definicji.

Opis dzialania algorytmu:
- program parsuje wszystkie pliki w formacie .nxml znajdujace sie w roboczym katalogu,
korzystajac ze skryptu xml_parser6c.py
- w ten sposob uzyskane dane zostaja wprowadzone do bazy

Przed uruchomieniem programu nalezy zdefiniowac uzytkownika bazy danych i sama baze danych
zmieniajac linijke w if __name__ == '__main__':
#DB connection
db = my.connect(host='localhost', user='root', passwd='bioinfo5', db='bioinfodb')

Nastepnie uruchamiammy program w terminalu:
> python insertdb.py

4. Opis programu statisticdb.py
Program zawiera funkcje wykonujace przykladowe zapytania do bazy danych oraz obliczajace z-score
2 slow. Opis poszczegolnych funkcji znajduje sie w programie bezposrednio pod linia ich definicji.

5. Opis programu run_statisticdb.py
Program umozliwia uzytkownikowi polaczenie sie z baza danych, pobieranie z niej 
informacji dotyczacych interesujacego go slowa oraz obliczenie z-score.
Wynik zapytan  kierowanych do bazy danych oraz obliczona wartosc z-score, zapisywane sa w pliku:
"Statistics_res.txt"

Uruchomienie programu:
> python run_statisticdb.py

Program zapyta uzytkownika o:
'Podaj slowo-query:'
np. model

'Podaj wartosc graniczna wystapien slow powyzej ktorej dane slow bedzie brane pod uwage w statystykach.
Wartosc graniczna:'
np. 10

'Podaj skorelowane slowo, do slowa z zapytania:'
np. sequence

Jako wynik uzyskamy:
'Z-score dla slow model i sequence wynosi: 4.02909833435'
















