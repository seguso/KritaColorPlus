Questo plugin aggiunge a Krita delle funzionalita' come

- logica spectral del color mixing: in pratica giallo mixato con blu fa verde; blu con bianco
fa blu acceso; ecc. Grazie a Ronald van Wijnen per aver scritto la matematica di questo. :)

- un motore di "wet painting" che permette di mixare ogni tua pennellata (stroke) col colore
che è già presente sulla tela. Ogni pennellata che fai si sporca con una proporzione _fissa_
del colore già presente sulla tela (ma non con il bianco della tela).

    Quando  fai una pennellata, il pennello viene auto-pulito, quindi non ricorda il
    modo in cui si era sporcato nella pennellata precedente (come invece avviene nel
    dirty brush, vedi sezione apposita).

    Puoi configurare con uno slider in che proporzione ciascuna pennellata
    si sporca col colore che è sulla tela.
    
    Differenza dal Color Smudge Engine di Krita:

        il Color Smudge Engine di Krita funziona con il concetto di color rate, cioè la pennellata
        si sporca progressivamente. non puoi avere una pennellata che si sporca immediatamente col
        colore  che è già sulla tela, di una quantità fissa. Questo produce un effetto visivamente
        molto diverso, dando varietà al tuo dipinto.

        il Color Smudge Engine di Krita tende a produrre degli edge sfocati,
        perché usa un algoritmo di tipo build up e non di tipo glaze.

        


- un motore di "dirty brush". Ogni volta che fai una pennellata, il
tuo pennello si sporca un po' con il colore sulla tela. (ma non col
bianco della tela). La quantità con cui si sporca è configurabile.

    Per pulire i pennello c'è uno shortcut, che è lo stesso per la funzione Previous Color. (la
    prima volta che lo premi, pulisce il pennello, poi inizia a passare ai colori precedenti)