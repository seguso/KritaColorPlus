Questo plugin aggiunge a Krita le seguenti funzionalita:

# Logica spectral del color mixing

Questo significa che, quando mixi due colori (il che si può fare in vari modi, vedi oltre), il
giallo mixato con blu produce verde; blu con bianco produce un blu acceso e vibrante; ecc.


# Auto-mix

Se attivi questa modalità, ogni tua pennellata si sporca automaticamente con il colore che
è già presente sulla tela. La proporzione in cui si sporca è configurabile con uno slider.

    
Ogni pennellata si sporca indipendentemente. Cioè, ad ogni pennellata, il pennello viene prima
"auto-pulito", poi sporcato col nuovo colore sulla tela. (Se invece vuoi che il pennello resti
sporco tra le varie pennellate, puoi usare il dirty brush. Vedi sezione apposita).
    
Differenze col Color Smudge Engine di Krita:

    Il Color Smudge di Krita mixa i colori senza logica spectral, quindi produce
    colori sbiaditi: ad esempio, blu + giallo = grigio, non verde.

    Il  Color Smudge Engine di Krita funziona con il concetto di "color rate", cioè il tuo colore
    scelto (foreground color) viene introdotto gradualmente durante la pennellata. Non puoi avere
    una pennellata che sin dall'inizio ha il tuo foreground color, ma sporcato di una percentuale
    fissa col colore sulla tela. Questo produce un effetto visivamente molto diverso.

    Il Color Smudge Engine di Krita tende a produrre degli edge sfocati,
    perché usa un algoritmo di tipo build up e non di tipo glaze.

        
Nota: la pennellata non si sporca col bianco della tela, ma solo con il
colore davvero depositato sulla tela. Questo settaggio è opzionale.

Questo motore si chiama "auto-mix" perché ogni pennellata si "mixa
automaticamente" col colore di sfondo.

L'auto-mix funziona con qualunque brush, anche quelli che usano il pixel
engine.  Quindi non devi rinunciare al dual brush, che attualmente non è
supportato dal color smudge engine di Krita. E hai gli edge netti.


Nota:  questa modalità, se attivata, riempie la color history di Krita di
colori intermedi, prodotto dello "sporcamento" del pennello. Questo rende
la  color  history di Krita inutilizzabile. Per questa ragione, ColorPlus
offre una sua color history, che non mostra questi colori "intermedi".

# Dirty brush

In questa modalità, ogni volta che fai una pennellata, il tuo pennello si sporca un po'
con il colore sulla tela. La quantità con cui si sporca è configurabile con uno slider.
    
Differenza  con  l'auto-mix: nel dirty brush, la prima pennellata non si sporca, ma ha
il colore puro che tu hai scelto. Solo le pennellate successive si sporcano in base al
colore che era sulla tela nelle pennellate precedenti. Invece, nell'auto-mix, anche la
prima  pennellata si sporca. Ma le successive pennellate dimenticano il modo in cui si
è sporcata la pennellata precedente.

Nota: per pulire i pennello c'è uno shortcut, che è lo stesso per la funzione Previous Color.
(la prima volta che lo premi, pulisce il pennello, poi inizia a passare ai colori precedenti)

Nota: la pennellata non si sporca col bianco della tela, ma solo con il
colore davvero depositato sulla tela. Questo settaggio è opzionale.

Nota:  questa modalità, se attivata, riempie la color history di Krita di
colori intermedi, prodotto dello "sporcamento" del pennello. Questo rende
la  color  history di Krita inutilizzabile. Per questa ragione, ColorPlus
offre una sua color history, che non mostra questi colori "intermedi".

# Alternanza rapida tra colori

C'è uno shortcut con cui tu puoi alternare facilmente tra due colori, passando istantaneamente
al colore usato prima di quello attuale. 

La maggior parte del tempo, per il mio stile di pittura, io alterno continuamente tra
due colori, quindi questa funzione è essenziale per evitare mouse travel per cliccare
nella cronologia dei colori. 

Con lo stesso shortcut, premuto due volte di seguito, puoi passare
al penultimo colore usato, e così via.



# color picker intelligente

Hai uno shortcut per fare color picking del colore sotto al mouse,
senza tenere premuto ALT o CTRL.

# Color Mixing shortcut

Hai uno shortcut per mixare il colore attuale (il foreground color) con una porzione del colore
sulla tela. Ad esempio, se hai il colore blu, e il mouse si trova sul colore giallo, con questo
shortcut puoi aggiungere il 50% di giallo al blu, ottenendo il verde.

La quantità di colore che prelevi dalla tela è configurabile con uno slider.

Una  opzione importante è che, quando mixi un colore per farlo diventare più
simile a un altro, il plugin è in grado di cambiare automaticamente anche la
pennellata che hai appena fatto, dandole il nuovo colore. Questa funzione si
chiama "correzione del colore a posteriori". Vedi sezione apposita.

# Correzione a posteriori del colore

Il plugin, nella sua modalità di default, crea automaticamente un layer ogni volta che
cambi  colore.  In questo modo, permette la "post-correzione" dei colori sbagliati. Ad
esempio, capita spesso che, dopo aver fatto una pennellata, ti accorgi che il colore è
sbagliato, cioè che armonizza male con lo sfondo, perché è *troppo diverso* dal colore
che c'era sotto, sul quale hai dipinto. In questo caso, puoi modificare il colore "sul
posto", gradualmente, fino a che vedi che è diventato abbastanza simile allo sfondo.

Come si fa a modificare gradualmente il colore della pennellata appena fatta? Hai 2 modi:
    
    1) Premi il pulsante "color mix" (vedi sezione apposita). Oltre a mixare
    il  colore, questo shortcut modificherà la pennellata appena fatta (o le
    pennellate appena fatte) dandole il nuovo colore.
    
        
    2) Diminuisci la trasparenza della pennellata. Per questo c'è uno shortcut apposito.
    Premi  varie  volte  lo shortcut e vedi le pennellate appena fatte che diventano più
    trasparenti.  Quando vedi che sono arrivate al punto che non sono più troppo diverse
    dal colore sotto, ti fermi, e passi alla prossima pennellata. 

Questo è importante perché ti risparmia la sequenza noiosa in cui fai una pennellata,
ti  accorgi che il colore è sbagliato, premi Undo, cambi colore dal selector, provi a
pennellare, ti accorgi che non va ancora bene, fai undo, poi cambi di nuovo colore, e
così. via.

Tutto questo è reso possibile da layer che vengono creati automaticamente. Quindi vedrai
molti  layer creati automaticamente. Questo è voluto. Ogni tanto (diciamo ogni 5 minuti)
vorrai probabilmente fonderli tutti insieme, il che si fa con un apposito shortcut.

Puoi disattivare la creazione automatica di layer, ma perderai la
possibilità di fare post-correzioni dei colori.

Nota: Il fatto che ColorPlus crei automaticamente layer permette anche
l'effetto acquerello (vedi sezione apposita).


# simulazione di acquerello

L'acquerello  è caratterizzato soprattutto dal fatto che due pennellate trasparenti si
fondono tra loro. Non vedi la sovrapposizione di colori (overlap). Invece in krita, se
usi un colore trasparente e fai due pennellate, vedrai la sovrapposizione nel punto di
intersezione tra di loro. Le pennellate non si fondono tra loro.

Per  risolvere questo problema, ColorPlus fa sì che sia il layer ad essere
trasparente, non il tuo brush preset (che è opaco al 100%). In questo modo
vedrai  pennellate  che  si fondono tra loro senza overlap, ma allo stesso
tempo  sono trasparenti, cioè vedi il colore sotto. ColorPlus si occupa di
creare  automaticamente  layer quando cambi colore, in modo che pennellate
con lo stesso colore si fondano insieme, pur restando trasparenti.

Nota: Il fatto che ColorPlus crea automaticamente layer permette anche
la post-correzione del colore (vedi sezione apposita).



# Color history intelligente

Hai una color history visuale, che ti mostra i colori recenti, a cui
puoi switchare cliccandoci direttamente. È simile alla color history
di Krita, ma non ti fa vedere tutti i colori prodotti dall'automix e
dal dirty brush, ma solo quelli originali che tu hai selezionato dal
color selector di Krita.

# Preview a tutto schermo

Esiste  uno  shortcut  che mostra la tua immagine attuale a tutto schermo, nascondendo
temporaneamente  tutti  i docker floating che ci sono. Se premuto di nuovo, ripristina
il layout di lavoro, con i docker floating, i docker agganciati, e la reference window
eventuale.

# Esportazione di layers e coordinate

ColorPlus offre una voce di menu che esporta tutti i layer il cui nome termina con
-png, .png, -jpg o .jpg. Esporta anche un file .json che contiene le coordinate di
ogni layer all'interno dell'immagine.

Questo è utile se stai sviluppando un gioco o un'applicazione che deve caricare
fondale e personaggi, e sapere in che posizione piazzare i personaggi.

La funzione esporta anche gruppi di layer. Se hai un gruppo con nome che finisce ad esempio
con .png, esporterà un'immagine contenente la fusione di tutti i layer del gruppo.

Il .json e i layer vengono salvati nella tua cartella Documenti.