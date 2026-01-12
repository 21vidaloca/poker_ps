# Poker Monte Carlo Simulator ♠️♥️

Acest proiect este o aplicație a simulărilor de tip Monte Carlo. Ne folosim de simulare pentru a prezice cât de bună este o anumită mână de poker la un moment dat, comparându-ne cu baseline-ul teoretic.

## 1. Despre "Magia Neagră" a Simulării

Teoretic proiectul nu are vreo aplicație practică în lumea reală, dar demonstrează perfect cum funcționează simulările de tip Monte Carlo. Personal încă ni se pare magie neagră cum este de multe ori irelevantă dificultatea/complexitatea a ce simulezi în formula care îți spune de câte simulări ai nevoie pentru a obține o marjă de eroare de maxim x%.

Simulatorul se bazează pe **LEGEA NUMERELOR MARI**: pe măsură ce numărul de simulări crește, media scade, convergând la probabilitatea reală în timp (adică la cea teoretică).

## 2. De ce Monte Carlo și nu altceva?

De ce Monte Carlo? Pentru că numărul total de permutări posibil dintr-un pachet de 52 de cărți este $52!$, un număr absolut inimaginabil de mare. Deci, calculul brute-force este inaccesibil.

Dar dacă folosim o simulare de genul acesta, putem după 100.000 de mâini să spunem cu practic certitudine (99.9% precizie) un răspuns *corect*. Teoretic nu e corect corect, dar se înțelege ideea. Nu va exista niciodată un outlier atât de puternic pe care să îl omitem, întrucât fiecare simulare aduce o cantitate fixă de date în aplicație.

## 3. Matematica din Spate (Inegalitatea Hoeffding)

Am aplicat **Inegalitatea Hoeffding** direct în cod, trântind-o fără nici un fel de gând. Glumesc, am folosit-o pentru a afla o aproximare foarte bună la marja de eroare.

Astfel, legat și de ce am zis mai sus, pentru a reduce eroarea de 10 ori, trebuie să mărești numărul de simulări de 100 de ori (relație pătratică), indiferent dacă simulezi aruncarea unei monede sau o mână complexă de poker cu 7 cărți.

## 4. Tehnologii (Stack-ul Nostru)

Am folosit **Python** pentru simplitatea și rapiditatea implementării, cât și pentru că are o librării foarte utile precum `matplotlib`. (și pentru că l-am folosit la laborator :PP).