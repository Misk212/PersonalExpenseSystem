# Importazione libreria per gestione DB PostgresSql-pgAdmin4
import psycopg2

####################################################################################################
# CONNESSIONE AL DATABASE
####################################################################################################

def connetti_db():

    #Guardia/Controllo sulla corretta connessione del DB con riscontro se non corretta
    try:
        conn = psycopg2.connect(
            host='localhost',
            database="postgres",
            user="postgres",
            password="admin12345",
            port="5432"
        )
        print("Connesso al DB")
        return conn

    #Except necessario per chiudere la guardia sulla connessione
    except Exception as e:
        print(f"Non posso connettermi: {e}")
        return None


####################################################################################################
# MODULO CATEGORIE
####################################################################################################

def gestione_categorie(conn):

    #Definizione puntatore e connessione
    cur = conn.cursor()

    #Esecuzione della query
    cur.execute("SELECT ID_Categoria, Nome_Categoria, Famiglia_Categoria FROM CATEGORIE")

    righe = cur.fetchall()

    categorie = [
        {"id": r[0], "nome": r[1], "famiglia": r[2]}
        for r in righe
    ]

    #Ciclo di verifica prima di entrare nell'iterazione If
    while True:
        scelta = input("Vuoi inserire una categoria? (Y/N): ").strip().upper()

        if scelta == "N":
            print("Uscita dal modulo categorie")
            break

        if scelta != "Y":
            print("Scelta non valida")
            continue

        nome_categoria = input("Inserisci nuova categoria: ").strip().upper()

        if nome_categoria == "":
            print("Nome categoria non può essere vuoto")
            continue

        if nome_categoria in categorie:
            print("Categoria già presente in archivio")
            continue

        cur.execute(
            "INSERT INTO CATEGORIE (Nome_Categoria) VALUES (%s)",
            (nome_categoria,)
        )
        conn.commit() #Salva per evitare situazioni di rollback e perdita di dati
        categorie.append({
            "id": cur.lastrowid, #punta all'ultimo ID creato 
            "nome": nome_categoria,
            "famiglia": None
        })

        print("Categoria inserita correttamente")

    cur.close()


####################################################################################################
# MODULO INSERIMENTO SPESA
####################################################################################################

def inserisci_spesa(conn):
    cur = conn.cursor()

    #Importazione librerire per gestione data
    from datetime import datetime

    try:
        data = input("Inserisci la data (YYYY-MM-DD): ").strip()
        data_spesa = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        print("Formato data non valido.")
        cur.close()
        return

    try:
        importo = float(input("Inserisci importo spesa: ").strip())
        if importo <= 0:
            print("Importo non valido.")
            cur.close()
            return
    except ValueError:
        print("Inserisci un numero valido.")
        cur.close()
        return

    categoria = input("Inserisci la categoria: ").strip().upper()

    cur.execute("SELECT ID_Categoria FROM CATEGORIE WHERE Nome_Categoria = %s", (categoria,))
    riga = cur.fetchone()

    if riga is None:
        print("Categoria inesistente.")
        cur.close()
        return

    ID_Categoria = riga[0]

    cur.execute(
        "INSERT INTO SPESE (Data_Spese, Importo, ID_Categoria) VALUES (%s, %s, %s)",
        (data_spesa, importo, ID_Categoria)
    )

    conn.commit()
    print("Spesa inserita correttamente.")
    cur.close()


####################################################################################################
# MODULO DEFINIZIONE BUDGET
####################################################################################################

def definisci_budget(conn):
    cur = conn.cursor()

    mese_budget = input("Inserisci periodo disponibilità budget (YYYY-MM): ").strip()

    if len(mese_budget) != 7 or mese_budget[4] != "-":
        print("Formato mese non valido.")
        cur.close()
        return
                   
    try:
        importo_budget = float(input("Inserisci importo budget: ").strip())
        if importo_budget <= 0:
            print("Importo non valido.")
            cur.close()
            return
    except ValueError:
        print("Inserisci un numero valido.")
        cur.close()
        return

    cur.execute(
        "SELECT ID_Mese FROM BUDGET WHERE Mese_Riferimento = %s",
        (mese_budget,)

        
    )

    riga = cur.fetchone()

    if riga is None:
        cur.execute(
            "INSERT INTO BUDGET (Mese_Riferimento, Importo_Mese) VALUES (%s, %s)",
            (mese_budget, importo_budget)
        )
        conn.commit()
        print("Budget inserito correttamente.")
    else:
        cur.execute(
            "UPDATE BUDGET SET Importo_Mese = %s WHERE Mese_Riferimento = %s",
            (importo_budget, mese_budget)
        )
        conn.commit()
        print("Budget aggiornato correttamente.")

    cur.close()


####################################################################################################
# MODULO REPORT
####################################################################################################

def visualizza_report(conn):
    cur = conn.cursor()

    print("\n--- REPORT SPESE ---")

    cur.execute("""
        SELECT S.Data_Spese, S.Importo, C.Nome_Categoria
        FROM SPESE S
        JOIN CATEGORIE C ON S.ID_Categoria = C.ID_Categoria
        ORDER BY S.Data_Spese
    """)

    righe = cur.fetchall()

    if not righe:
        print("Nessuna spesa registrata.")
        cur.close()
        return

    totale = 0

    for r in righe:
        data, importo, categoria = r
        print(f"Data: {data} | Importo: {importo} € | Categoria: {categoria}")
        totale += importo
    print("\nTotale spese:", totale, "€")

    cur.execute("SELECT SUM(Importo_mese) FROM BUDGET")
    riga = cur.fetchone()
    if riga and riga[0] is not None:
        budget_totale = riga[0]
        budget_residuo = budget_totale - totale

        print(f"Budget totale: {budget_totale}€")
        print(f"Budget residuo: {budget_residuo}€")

        if budget_residuo <= 0:
            print(f"Attenzione, budget superato")
        else:
            print("Budget disponibile")
    else:
        print("Nessun budget definito")

    cur.close()


####################################################################################################
# MENU PRINCIPALE
####################################################################################################

def main():
    conn = connetti_db()
    if not conn:
        return

    while True:
        print("\n--- SISTEMA SPESE PERSONALI ---")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")

        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            gestione_categorie(conn)
        elif scelta == "2":
            inserisci_spesa(conn)
        elif scelta == "3":
            definisci_budget(conn)
        elif scelta == "4":
            visualizza_report(conn)
        elif scelta == "5":
            print("Uscita...")
            break
        else:
            print("Scelta non valida.")

    conn.close()


if __name__ == "__main__":
    main()
