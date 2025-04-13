TODO fai che clean brush biene fatto da dry paper, non da V

DONE automix prevale su dirty brush

TODO manca krita palette

    difficile perché cambia con un delay il color selector. ho provato a leggere il colore
    con delay, ma se in quel momento ho gia iniziato lo stroke, krita crasha.

DONE c'è ancora il bug nell automix: scegli un colore nel selector, e quando
esci ti setta un altro, precedente. non succede dall'inizoi ma dopo un po'

    riscrivi tutto su questa idea: se arriva il fgcolor changed MENTRE TU SEI FUORI, allora e' un colore vero.


    DONE C non crea il nuovo layer? o solo se non sei in un group?

    DONE vedi se pulsante V crea nuovo layer
    
    

    DONE manca gestire il click nella history

        click su color history inizia a funzionare ma crea duplicati

        DONE non crea il nuovo layer
 
    

    DONE manca gestire C

    DONE gestire anche grayscale quando fai C. l'ho commentato

    DONE gestire mix shortcut


TODO fixa il bug di quando fa fill dell'intero layer. come si riproduceva?

DONE inverti dry paper e color preview

DONE vedi ultima versione di spectral

TODO quando togli dirty brush, deve fare accept current color. forse
solo metterlo nella history.

TODO on hold: col polling posso togliere autofocus windows! che crea un sacco di problemi?
ma no, non posso. non posso creare un layer senza rendere attiva la subwindow.


DONE ritesta save e restore state and pos of all windows

DONE reimplementa export layer coordinates

DONE pulsante merge temp layers

DONE disabilita sliders visualmente

DONE  con automix, se premo V, non mette il colore in cima alla history

DONE cercando altro bug: non crea piu il layer nemmeno senza automix

DONE automix: se premo V per andare al colore precedente, dopo il
primo stroke appena lascio mi rimette l'altro

DONE ritesta layer opacity

DONE ritesta full screen preview

    ok ma se era massimizzata, rimassimizzala quando ripremi

DONE mi sembra che il mixing spctral non funzioni piu bene da quando ho fatto il radius

DONE se premo D, fare clean brush se sporco

DONE mi crea un nuovo layer se esco e rientro con mouseover dal selector,
anche se non ha cambiato colore

TODO low priority - ad ogni mouse up viene rebuildata la color history.
per verificarlo, scommenta qualcosa dentro update_color_history_ui

TODO è inutile il brush cycling così, ma con shortcut può avere senso 

    per ora commentato