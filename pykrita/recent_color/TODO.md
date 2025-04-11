TODO vedi ultima versione di spectral

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