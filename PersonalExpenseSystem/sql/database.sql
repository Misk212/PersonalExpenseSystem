
-- PULIZIA INIZIALE IN CASO CI FOSSERO DATI INSERITI O REFUSI -- 
DROP TABLE IF EXISTS BUDGET CASCADE;
DROP TABLE IF EXISTS SPESE CASCADE;
DROP TABLE IF EXISTS CATEGORIE CASCADE;


-- 1. CREAZIONE TABELLE --
CREATE TABLE CATEGORIE (
   	ID_Categoria SERIAL PRIMARY KEY,
    Nome_Categoria varchar(50) NOT NULL UNIQUE, -- UNIQUE PER EVITARE RIPETIZIONE DI CATEGORIE
    Famiglia_Categoria varchar(30) -- es. 'Beni primari', 'Hobby', 'Imprevisti' -- NON SI RICHIEDE L'OBBLIGO DI RIEMPIMENTO
);

CREATE TABLE SPESE (
    ID_Spese SERIAL PRIMARY KEY ,
    Data_Spese date NOT NULL,
    Importo DECIMAL(10, 2) NOT NULL CHECK (Importo > 0),
	Descrizione_Spesa varchar(100),
	ID_Categoria INTEGER NOT NULL,
	FOREIGN KEY (ID_Categoria) REFERENCES CATEGORIE(ID_Categoria)
);

CREATE TABLE BUDGET (
    ID_Mese SERIAL PRIMARY KEY,
	Mese_Riferimento varchar (7) NOT NULL, -- FORMATO "YYYY-MM" --
	Importo_mese decimal(10, 2) NOT NULL CHECK (Importo_mese > 0),
    ID_Categoria INTEGER,
    FOREIGN KEY (ID_Categoria) REFERENCES CATEGORIE(ID_Categoria),
    UNIQUE (Mese_Riferimento, ID_Categoria) -- UN MESE SOLO PER CATEGORIA --
);


	ALTER TABLE BUDGET
	ALTER COLUMN ID_Categoria DROP NOT NULL;
-- 2. POPOLAMENTO DATI (INSERT) --

-- CATEGORIE (ID_Categorie, Nome_Categoria, Famiglia_Categoria) --
--INSERT INTO CATEGORIE VALUES (1, 'Alimentari', 'Beni Primari');
--INSERT INTO CATEGORIE VALUES (2, 'Affitto/Mutuo', 'Beni Primari');
--INSERT INTO CATEGORIE VALUES (3, 'Manutenzione Auto', 'Trasporti');
--INSERT INTO CATEGORIE VALUES (4, 'Cene Fuori', 'Hobby/Svago');

-- SPESE (ID_Spese, Data_Spese, Importo, Descrizione_Spesa, ID_Categoria) --
--INSERT INTO SPESE VALUES (1, '2026-01-01', 150.00, 'Alimenti per tutto il mese', 1);
--INSERT INTO SPESE VALUES (2, '2026-01-15', 700.00, NULL, 1);
--INSERT INTO SPESE VALUES (3, '2026-01-20', 150.00, 'Benzina', 3);
--INSERT INTO SPESE VALUES (4, '2026-01-30', 0.00, 'Cene Fuori', 4);

-- BUDGET (ID_Mese, Mese_Riferimento, Importo_Limite, ID_Categoria) --
--INSERT INTO BUDGET VALUES (1, '2026-01', 1000.00, 1);
--INSERT INTO BUDGET VALUES (2, '2026-01', 150.00, 3);
--INSERT INTO BUDGET VALUES (3, '2026-01', 200.00, 4);

 
-- QUERY SPESE x CATEGORIA -- 
SELECT c.Nome_Categoria,
	SUM(s.Importo) AS Totale_Speso
FROM SPESE s
	JOIN CATEGORIE c ON s.ID_Categoria = c.ID_Categoria
		GROUP BY c.nome_categoria
			ORDER BY Totale_Speso DESC;

-- QUERY SPESE MENSILI x BUDGET --
SELECT 	b.Mese_Riferimento,
		c.Nome_Categoria,
		b.importo_mese AS Buget_pianificato,
	SUM(s.Importo) AS Totale_Spesa_Effettivo
FROM BUDGET AS b
	JOIN CATEGORIE c ON b.ID_Categoria = c.ID_categoria
	JOIN SPESE s ON s.ID_Categoria = c.ID_Categoria
		AND TO_CHAR(s.Data_Spese, 'YYYY-MM') = b.mese_riferimento
			GROUP BY 	b.Mese_Riferimento,
						c.Nome_Categoria,
						b.importo_mese
				ORDER BY b.Importo_mese DESC;

-- QUERY ELENCO COMPLETO SPESE ORDINATE PER DATA --
SELECT * FROM SPESE s
	ORDER BY s.Data_Spese ASC;







