ColorPlus è un plugin per Krita che aggiunge a Krita le seguenti funzionalità:

# Funzionalità

## Logica spectral del color mixing

Questo significa che i colori si mixano in modo realistico. Ad esempio, quando mixi due colori,
il giallo mixato con blu produce verde; blu con bianco produce un blu acceso e vibrante; ecc.

Questo mixaggio realistico avviene in tutte le feature di ColorPlus:
mixing manuale, auto-mix, dirty brush.

Grazie a Ronald van Wijnen per la libreria utilizzata per il mixaggio
dei colori secondo la teoria Kubelka-Munk!

## Auto-mix

Se attivi questa modalità, ogni tua pennellata si sporca automaticamente con il colore che
è già presente sulla tela. La proporzione in cui si sporca è configurabile con uno slider.

    
Ogni pennellata si sporca indipendentemente. Cioè, ad ogni pennellata, il pennello viene prima
"auto-pulito", poi sporcato col nuovo colore sulla tela. (Se invece vuoi che il pennello resti
sporco tra le varie pennellate, puoi usare il dirty brush. Vedi sezione apposita).

Quindi, ad ogni pennellata introdurrete un po' di colore. Continuando a pennellare,
alla  fine arriverà al colore target. (A patto che il mixing radius sia abbastanza
basso, altrimenti non ci arriverete mai).
    
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

Per attivare l'auto mix, cliccare nel docker di ColorPlus: https://i.imgur.com/COOOjwa.png

Lì c'è anche lo slider che controlla quanto prende dalla tela ad ogni pennellata.

## Dirty brush

In questa modalità, ogni volta che fai una pennellata, il tuo pennello si sporca un po'
con il colore sulla tela. La quantità con cui si sporca è configurabile con uno slider.
    
Differenza  con  l'auto-mix: nel dirty brush, la prima pennellata non si sporca, ma ha
il colore puro che tu hai scelto. Solo le pennellate successive si sporcano in base al
colore che era sulla tela nelle pennellate precedenti. Invece, nell'auto-mix, anche la
prima  pennellata si sporca. Ma le successive pennellate dimenticano il modo in cui si
è sporcata la pennellata precedente.

Un'altra differenza è che, con l'auto-mix, ogni pennellata vi avvicina
sempre di più al colore target (cioè il foreground color). Invece, con
il dirty brush, ogni pennellata vi allontana sempre più dal foreground
color.

Nota: per pulire il pennello c'è uno shortcut, che è lo stesso per la funzione Previous Color.
(la prima volta che lo premi, pulisce il pennello, poi inizia a passare ai colori precedenti)

Nota: la pennellata non si sporca col bianco della tela, ma solo con il
colore davvero depositato sulla tela. Questo settaggio è opzionale.

Nota:  questa modalità, se attivata, riempie la color history di Krita di
colori intermedi, prodotto dello "sporcamento" del pennello. Questo rende
la  color  history di Krita inutilizzabile. Per questa ragione, ColorPlus
offre una sua color history, che non mostra questi colori "intermedi".

Per attivare il dirty Brush, usa il docker di ColorPlus: https://i.imgur.com/RDHdyWS.png

## Alternanza rapida tra colori

C'è uno shortcut con cui tu puoi alternare facilmente tra due colori,
passando istantaneamente al colore usato prima di quello attuale.

La maggior parte del tempo, per il mio stile di pittura, io alterno continuamente tra
due colori, quindi questa funzione è essenziale per evitare mouse travel per cliccare
nella cronologia dei colori. 

Con lo stesso shortcut, premuto due volte di seguito, puoi passare
al penultimo colore usato, e così via.

Consiglio di assegnare questo shortcut al tasto V: https://i.imgur.com/vpKxHaf.png


## Color picker intelligente

Hai uno shortcut per fare color picking del colore sotto al mouse,
senza tenere premuto ALT o CTRL.

C'è  una versione dello shortcut che, oltre a fare color picking, crea anche un nuovo
layer. Consiglio di usare quella. È opportuno creare un nuovo layer ogni volta che si
cambia colore, per simulare l'effetto acquerello (vedi sezione apposita).

Consiglio di associare questo shortcut al pulsante C: https://i.imgur.com/zC2rmom.png

## Color Mixing shortcut

Hai uno shortcut per mixare il colore attuale (il foreground color) con una porzione
del colore sulla tela. In altre parole, con questo shortcut, cambi il colore attuale
portandolo ad essere più vicino al colore su cui si trova il mouse.

Ad esempio, se hai il colore blu, e il mouse si trova sul colore giallo, con
questo shortcut puoi aggiungere il 50% di giallo al blu, ottenendo il verde.

La quantità di colore che prelevi dalla tela è configurabile con lo
slider "mix level" nel docker di ColorPlus:

Una  opzione importante è che, quando mixi un colore per farlo diventare più
simile a un altro, il plugin è in grado di cambiare automaticamente anche la
pennellata che hai appena fatto, dandole il nuovo colore. Questa funzione si
chiama "post-correzione del colore". Vedi sezione apposita.

Consiglio di associare questa funzione al tasto F: https://i.imgur.com/AiehdQv.png

# Post-correzione del colore

Il plugin, nella sua modalità di default, crea automaticamente un layer ogni volta che
cambi  colore.  In questo modo, permette la "post-correzione" dei colori sbagliati. Ad
esempio, capita spesso che, dopo aver fatto una pennellata, ti accorgi che il colore è
sbagliato, cioè che armonizza male con lo sfondo, perché è *troppo diverso* dal colore
che c'era sotto, sul quale hai dipinto. In questo caso, puoi modificare il colore "sul
posto", gradualmente, fino a che vedi che è diventato abbastanza simile allo sfondo.

Come si fa a modificare gradualmente il colore della pennellata appena
fatta? ColorPlus offre 2 modi di farlo:
    
    1)  Premi il pulsante "color mix" (vedi sezione apposita). Questo, come abbiamo detto, cambierà
    il  colore  del  brush portandolo più vicino al colore su cui si trova il mouse. Ma modificherà
    anche la pennellata appena fatta (o le pennellate appena fatte) portandole più vicine al colore
    sotto al mouse!
    
        
    2) Diminuisci la trasparenza della pennellata appena fatta. Per questo c'è uno shortcut
    apposito. Premi varie volte lo shortcut e vedi le pennellate appena fatte che diventano
    più trasparenti. Quando vedi che sono arrivate al punto che non sono più troppo diverse
    dal colore sotto, ti fermi, e continui a dipingere con quel livello di trasparenza.

Questo sistema (sia 1 che 2) è importante perché ti risparmia la sequenza noiosa in cui
fai  una pennellata, ti accorgi che il colore è sbagliato, premi Undo, cambi colore dal
selector, provi a pennellare, ti accorgi che non va ancora bene, fai undo, poi cambi di
nuovo colore, e così. via.

Tutto questo è reso possibile da layer che vengono creati automaticamente. Quindi vedrai
molti  layer creati automaticamente. Questo è voluto. Ogni tanto (diciamo ogni 5 minuti)
vorrai probabilmente fonderli tutti insieme, il che si fa con il pulsante cleanup layers
nel docker di ColorPlus: https://i.imgur.com/MTQC8l5.png.

Puoi disattivare la creazione automatica di layer, ma perderai la
possibilità di fare post-correzioni dei colori.

Nota: Il fatto che ColorPlus crei automaticamente layer permette anche
l'effetto acquerello (vedi sezione apposita).


### Modificare la trasparenza della pennellata

Abbiamo  detto che c'è uno shortcut per aumentare la trasparenza dell'ultima
pennellata (post-correzione del colore). Consiglio di associarlo al tasto X:
https://i.imgur.com/K8VM3Mx.png

Di solito, quando aumentate la trasparenza della pennellata perché volete fare
una modifica molto leggera, tipicamente la trasparenza finale sarà molto alta.
Quando  poi  volete passare a un altro colore, volete anche che la trasparenza
della pennellata sia automaticamente resettata a un valore normale, altrimenti
non  vedrete la nuova pennellata. Quindi ColorPlus ha una funzione "auto-reset
opacity": https://i.imgur.com/72jOEa5.png

    Impostate tramite lo slider il livello a cui volete resettare la trasparenza della pennellata,
    ogni volta che cambiate colore (consiglio di scegliere un valore tra 70% e 85%).


Se vi accorgete che la pennellata cappena fatta ontrasta troppo poco col colore sottostante,
c'è anche uno shortcut per diminuire la trasparenza della pennellata. Consiglio di assegnare
questa funzione al tasto S: https://i.imgur.com/PHRi71L.png



## Simulazione di acquerello

L'acquerello è caratterizzato (tra le altre cose!) dal fatto che due pennellate trasparenti si
fondono  tra loro. Non vedi la sovrapposizione di colori (overlap). Invece in krita, se usi un
colore  trasparente  e fai due pennellate, vedrai la sovrapposizione nel punto di intersezione
tra di loro. Le pennellate non si fondono tra loro.

Per risolvere questo problema, ColorPlus fa sì che sia il layer ad essere trasparente, non
il tuo pennello (che è opaco al 100%). In questo modo il pennello sembrerà trasparente, ma
allo  stesso  tempo  vedrai pennellate che si fondono tra loro senza overlap. ColorPlus si
occupa di creare automaticamente dei layer quando cambi colore, in modo che pennellate con
lo stesso colore si fondano insieme, pur restando trasparenti.

Nota: Il fatto che ColorPlus crea automaticamente layer permette anche
la post-correzione del colore (vedi sezione apposita).

Nel momento in cui voleste creare manualmente un layer, basta premere lo shortcut "dry
paper", che consiglio di associare al pulsante D: https://i.imgur.com/A2hIoeT.png



## Color history intelligente

Hai una color history visuale, che ti mostra i colori recenti, a cui
puoi switchare cliccandoci direttamente. È simile alla color history
di Krita, ma non ti fa vedere tutti i colori prodotti dall'automix e
dal dirty brush, ma solo quelli originali che tu hai selezionato dal
color selector di Krita.

## Preview a tutto schermo

Esiste  uno  shortcut  che  mostra il tuo dipinto attuale a tutto schermo, nascondendo
temporaneamente  tutti  i docker floating che ci sono. Se premuto di nuovo, ripristina
il layout di lavoro, con i docker floating, i docker agganciati, e la reference window
eventuale.


Suggerisco di assegnare a questa funzione il pulsante immediatamente sopra al pulsante
TAB, cioè il primo pulsante della tastiera: https://i.imgur.com/BY7BF2O.png

## Salvataggio e ripristino delle finestre e della loro posizione

ColorPlus fornisce un semplice metodo per salvare e ripristinare sessioni di lavoro: salva e
ripristina  il layout di lavoro, cioè quali file sono aperti, e in che posizione si trovano.
Trovate due voci di menu per questo: https://i.imgur.com/4ttc0XP.png

# Esportazione di layer e coordinate

ColorPlus offre una voce di menu che esporta tutti i layer il cui nome termina con
-png, .png, -jpg o .jpg. Esporta anche un file .json che contiene le coordinate di
ogni layer all'interno dell'immagine.

Questo è utile se stai sviluppando un gioco o un'applicazione che deve caricare
fondale e personaggi, e sapere in che posizione piazzare i personaggi.

La funzione esporta anche gruppi di layer. Se hai un gruppo con nome che finisce ad esempio
con .png, esporterà un'immagine contenente la fusione di tutti i layer del gruppo.

Il .json e i layer vengono salvati nella tua cartella Documenti.

## Autofocus delle finestre

Autofocus vuol dire che la finestra su cui sposti il mouse viene automaticamente attivata.

Alcune funzioni di ColorPlus hanno bisogno che l'opzione autofocus resti attiva.
Ad esempio, senza di essa non funzionerà la creazione automatica di layer.

# INSTALLAZIONE

In Windows:

Chiudi Krita. Entra nella cartella

C:\Users\yourname\AppData\Roaming\krita\pykrita

e copia qui il file recent_color.desktop e la cartella recent_color:
https://i.imgur.com/5SoFMpu.png

Poi entra nella cartella

C:\Users\yourname\AppData\Roaming\krita\actions

e copia qui i file .action: https://i.imgur.com/PR2xWr0.png

Poi avvia Krita. Da menu: Settings -> configure Krita. Python plugin manager. 

Attiva il plugin spuntandolo qui: https://i.imgur.com/EDr7vdd.png

Poi riassegna le scorciatoie qui: https://i.imgur.com/7J5ZFXe.png

(Nella schermata sopra puoi vedere anche quali tasti consiglio di
assegnare alle varie funzioni)

