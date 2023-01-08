Istruzioni per l’esecuzione
Le applicazioni sono già configurate per utilizzare l’interfaccia di loopback. Per avviare il sistema seguire in ordine i seguenti step:
1) Eseguire il file gateway.py
a) Il gateway inizia a ricevere messaggi sul socket UDP, quindi è già possibile
collegare dei droni
b) Il gateway crea il socket di handshake, quindi è possibile inviare una richiesta
di connessione da parte di un client
2) Eseguire il file client.py
a) Viene inviata una richiesta di connessione al gateway
b) Accettare la richiesta sulla console del gateway inserendo da tastiera il
carattere Y.
3) Eseguire il file drone.py
a) Un drone viene avviato e si collega al gateway.
b) Al momento utilizzando l’interfaccia di loopback è possibile collegare un solo
drone in quanto il gateway lo identifica tramite il suo indirizzo IP. Tuttavia se si esegue il file da altri dispositivi con indirizzi IP diversi è possibile connettere più droni al gateway. Sarà necessario modificare la variabile gatewayIP nel file drone.py in modo da connettersi all’host su cui esegue il gateway.
4) Sulla console del client sono visualizzati tutti i comandi e le istruzioni per utilizzare l’applicazione. In caso di necessità digitando help come comando si ottiene la lista dei comandi disponibili.
