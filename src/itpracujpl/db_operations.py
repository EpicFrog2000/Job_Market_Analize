import mysql.connector
from .key_words_for_pracujpl import * 
import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="itpracujpl_db"
)

# Czasem oferta jest po angielsku więc tłumaczę wszystkie pobrane dane na język polski dla konsystencji i jakości
def tłumacz_i_filtruj(lista):
    tłumaczenie = {
        "full-time": "pełny etat",
        "part time": "część etatu",
        "dodatkowa / tymczasowa": "dodatkowa / tymczasowa",
        "expert": "ekspert",
        "assistant": "asystent",
        "director": "dyrektor",
        "manager / supervisor": "kierownik / koordynator",
        "trainee": "praktykant / stażysta",
        "full office work": "praca stacjonarna",
        "hybrid work": "praca hybrydowa",
        "home office work": "praca zdalna",
        "mobile work": "praca mobilna",
        "contract of employment": "umowa o pracę",
        "B2B contract": "kontrakt B2B",
        "contract of mandate": "umowa zlecenie",
        "internship / apprenticeship contract": "umowa o staż / praktyki",
        "temporary staffing agreement": "umowa na zastępstwo",
        "contract for specific work": "umowa o dzieło",
    }
    przetłumaczona_lista = []
    for item in lista:
        if item in tłumaczenie:
            przetłumaczona_lista.append(tłumaczenie[item])
        elif item not in przetłumaczona_lista:
            przetłumaczona_lista.append(item)
    return przetłumaczona_lista

todays_date = datetime.datetime.now()
todays_date = str(todays_date.year) + "-" + str(todays_date.month)  + "-" + str(todays_date.day)

def insert_data(data_list,start_id_offer):
    connection = mydb.cursor()
    id_offer = start_id_offer
    for data_row in data_list:
        # insert into main table
        sql = "INSERT INTO daily_data (title, company, location, salary, id, doswiadczenie, date) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (data_row[0], data_row[1], data_row[2], data_row[4], id_offer, data_row[11], todays_date)
        connection.execute(sql, values)
        mydb.commit()
        # insert into management_level table
        lista_management_level = data_row[3].split(",")
        lista_management_level = [item.strip() for item in lista_management_level]
        for item in lista_management_level:
            matches = [key for key in key_words_management_level if key in item]
            matches = tłumacz_i_filtruj(matches)
            for match in matches:
                sql = "INSERT INTO daily_management_level (id, management_level) VALUES (%s,%s)"
                values = (id_offer, match)
                connection.execute(sql, values)
                mydb.commit()
        # insert into tryb_pracy table
        lista_tryb_pracy = data_row[5].split(",")
        lista_tryb_pracy = [item.strip() for item in lista_tryb_pracy]
        for item in lista_tryb_pracy:
            matches = [key for key in key_words_work_type if key in item]
            matches = tłumacz_i_filtruj(matches)
            for match in matches:
                sql = "INSERT INTO daily_work_type (id, work_type) VALUES (%s,%s)"
                values = (id_offer, match)
                connection.execute(sql, values)
                mydb.commit()
        # insert into etat table
        lista_etat = data_row[6].split(",")
        lista_etat = [item.strip() for item in lista_etat]
        for item in lista_etat:
            matches = [key for key in key_words_etat if key in item]
            matches = tłumacz_i_filtruj(matches)
            for match in matches:
                sql = "INSERT INTO daily_etat (id, etat) VALUES (%s,%s)"
                values = (id_offer, match)
                connection.execute(sql, values)
                mydb.commit()
        # insert into kontrakt table
        lista_kontrakt = data_row[7].split(",")
        lista_kontrakt = [item.strip() for item in lista_kontrakt]
        for item in lista_kontrakt:
            matches = [key for key in key_words_kontrakt if key in item]
            matches = tłumacz_i_filtruj(matches)
            for match in matches:
                sql = "INSERT INTO daily_kontrakt (id, kontrakt) VALUES (%s,%s)"
                values = (id_offer, match)
                connection.execute(sql, values)
                mydb.commit()
        # insert into specjalizacje table
        lista_specjalizacja = data_row[8].split(",")
        lista_specjalizacja = [item.strip() for item in lista_specjalizacja]
        for item in lista_specjalizacja:
            sql = "INSERT INTO daily_specjalizacje (id, specjalizacja) VALUES (%s,%s)"
            values = (id_offer, item)
            connection.execute(sql, values)
            mydb.commit()
        # insert into technologie_wymagane table
        for item in data_row[9]:
            sql = "INSERT INTO daily_technologie_wymagane (id, technologia) VALUES (%s,%s)"
            values = (id_offer, item.strip())
            connection.execute(sql, values)
            mydb.commit()
        # insert into technologie_mile_widziane table
        for item in data_row[10]:
            sql = "INSERT INTO daily_technologie_mile_widziane (id, technologia) VALUES (%s,%s)"
            values = (id_offer, item.strip())
            connection.execute(sql, values)
            mydb.commit()
        id_offer += 1
    mydb.commit()
    #print("data succesfuly inserted")
    connection.close()
    return id_offer

# Wkłada dane do tabelek z danymi historycznymi
def insert_to_historic_data():
    connection = mydb.cursor()

    connection.execute("SELECT COUNT(id) AS count FROM daily_data;")
    count_of_all_offers = connection.fetchone()
    val = (count_of_all_offers[0], todays_date)
    sql = "INSERT INTO historic_count (count, date) VALUES (%s, %s)"
    connection.execute(sql, val)
    mydb.commit()
    
    connection.execute("SELECT (SUM(CASE WHEN salary > 0 THEN 1 ELSE 0 END) / COUNT(salary)) * 100 AS percentage FROM daily_data;")
    salary_percent = connection.fetchone()
    val = (salary_percent[0], todays_date)
    sql = "INSERT INTO historic_salary (salary, date) VALUES (%s, %s)"
    connection.execute(sql, val)
    mydb.commit()

    connection.execute("SELECT etat, COUNT(id) AS count FROM daily_etat WHERE etat IN ('pełny etat', 'część etatu', 'dodatkowa / tymczasowa') GROUP BY etat ORDER  BY count DESC;")
    etat_data = connection.fetchall()
    val = ()
    for x in etat_data:
        val += (x[1],)
    val += (todays_date, )
    sql = "INSERT INTO `historic_etat`(`pełny etat`, `część etatu`, `dodatkowa / tymczasowa`, `date`) VALUES (%s, %s, %s, %s)"
    connection.execute(sql, val)
    mydb.commit()

    connection.execute("SELECT kontrakt, COUNT(id) AS count FROM daily_kontrakt WHERE kontrakt IN ('umowa o pracę', 'kontrakt B2B', 'umowa zlecenie', 'umowa o staż / praktyki', 'umowa o dzieło', 'umowa na zastępstwo') GROUP BY kontrakt ORDER  BY count DESC;")
    kontrakt_data = connection.fetchall()
    val=()
    for x in kontrakt_data:
        val += (x[1],)
    val +=(todays_date,)
    sql = "INSERT INTO `historic_kontrakt`(`umowa o pracę`, `kontrakt B2B`, `umowa zlecenie`, `umowa o staż / praktyki`, `umowa o dzieło`, `umowa na zastępstwo`, `date`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    connection.execute(sql, val)
    mydb.commit()
        
    connection.execute("SELECT management_level, COUNT(id) AS count FROM daily_management_level WHERE management_level IN ('Mid', 'asystent', 'Junior', 'Senior', 'ekspert', 'team manager','menedżer', 'praktykant / stażysta','dyrektor') GROUP BY management_level ORDER  BY count DESC;")
    management_level_data = connection.fetchall()
    val=()
    for x in management_level_data:
        val += (x[1],)
    val +=(todays_date,)
    sql = "INSERT INTO `historic_management_level`(`Mid`, `asystent`, `Junior`, `Senior`, `ekspert`, `team manager`, `menedżer`, `praktykant / stażysta`, `dyrektor`, `date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    connection.execute(sql, val)
    mydb.commit()
        
    connection.execute("SELECT work_type, COUNT(id) AS count FROM daily_work_type WHERE work_type IN ('praca hybrydowa', 'praca zdalna', 'praca stacjonarna', 'praca mobilna') GROUP BY work_type ORDER  BY count DESC")
    management_level_data = connection.fetchall()
    val=()
    for x in management_level_data:
        val += (x[1],)
    val +=(todays_date,)
    sql = "INSERT INTO `historic_work_type`(`praca hybrydowa`, `praca zdalna`, `praca stacjonarna`, `praca mobilna`, `date`) VALUES (%s, %s, %s, %s, %s)"
    connection.execute(sql, val)
    mydb.commit()
        
    connection.execute("SELECT specjalizacja, COUNT(specjalizacja) AS count FROM daily_specjalizacje WHERE specjalizacja IS NOT NULL AND specjalizacja != '' GROUP BY specjalizacja ORDER BY count DESC;")
    specjalizacja_data = connection.fetchall()
    val=()
    for x in specjalizacja_data:
        sql = "INSERT INTO `historic_specjalizacja`(`specjalizacja`, `count`, `date`) VALUES (%s, %s, %s)"
        val = (x[0],x[1],todays_date,)
        connection.execute(sql, val)
        mydb.commit()
        
    connection.execute("SELECT technologia, COUNT(technologia) AS count FROM daily_technologie_wymagane GROUP BY technologia ORDER BY count DESC;")
    wym_tech_data = connection.fetchall()
    val=()
    for x in wym_tech_data:
        sql = "INSERT INTO `historic_technologie_wymagane`(`technologia`, `count`, `date`) VALUES (%s, %s, %s)"
        val = (x[0],x[1],todays_date,)
        connection.execute(sql, val)
        mydb.commit()
        
    connection.execute("SELECT technologia, COUNT(technologia) AS count FROM daily_technologie_mile_widziane GROUP BY technologia ORDER BY count DESC;")
    wym_tech_data = connection.fetchall()
    val=()
    for x in wym_tech_data:
        sql = "INSERT INTO `historic_technologie_mile_widziane`(`technologia`, `count`, `date`) VALUES (%s, %s, %s)"
        val = (x[0],x[1],todays_date,)
        connection.execute(sql, val)
        mydb.commit()
        
    connection.execute("INSERT INTO historic_location (location, count, date) SELECT location, COUNT(*) AS location_count, '"+str(todays_date)+"' AS date FROM `daily_data` GROUP BY location ORDER BY location_count DESC LIMIT 20;")
    mydb.commit()

    # czyści dane z tabelek z danymi dziennymi
def clear_tables():
    connection = mydb.cursor()
    tables_to_clear = [
        "daily_data",
        "daily_etat",
        "daily_kontrakt",
        "daily_management_level",
        "daily_specjalizacje",
        "daily_technologie_wymagane",
        "daily_technologie_mile_widziane",
        "daily_work_type"]
    for table in tables_to_clear:
        sql = f"DELETE FROM {table};"
        connection.execute(sql)
    mydb.commit()
