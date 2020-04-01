import sqlite3
import time
import sys


# contiene i tipi di messaggio da controllare
msgs_type = [
    {"name": "file",    "offset": 32, "len": 4, "data": ["d7", "70", "b0", "9c"]},
    {"name": "photo",  "offset": 32, "len": 4, "data": ["d7", "50", "51", "69"]},
]


def check_type(data: "byte string") -> "str.message_type":
    for type_ in msgs_type:
        res = 0
        for i in range(type_["len"]):
            # conta quanti campi sono uguali
            if data[(type_["offset"] + i)] == int(type_["data"][i], 16):
                res += 1

        # se tutti i campi sono uguali allora ritorna il tipo del messaggio
        if res == type_["len"]:
            return type_["name"]

    return None


def blob_parser(data: "str.binary_string") -> "str.parsed_message":
    # se con offset 16 4byte == 6d bc b1 9d -> messaggio tra due utenti
    # do per scontato che tutti i messaggi siano del tipo "tra due utenti"

    type_ = check_type(data)    # tipo del messaggio, se None è un normale messaggio di testo

    if type_ is not None:
        return f"-{type_}-"

    offset_len_msg = 28     # l'offset della lunghezza del messaggio
    start_msg = 29          # potrebbe essere anche 32 dipende da offset_len_msg

    ln = data[offset_len_msg]

    result = ""

    # se c'è un problema con la visualizzazione passo a considerare il messaggio come una "Risposta a messaggio"
    # le "Risposte a messaggio" rompono un po la visualizzazione
    # devo capire come gestirle, ma pare che in posizione 31 abbiano la lunghezza del messaggio ...
    try:
        result = data[start_msg:(start_msg+ln)].decode("utf-8")
    except Exception:
        offset_len_msg = 31
        start_msg = 32

        ln = data[offset_len_msg]
        result = data[start_msg:(start_msg+ln)].decode("utf-8", "ignore")

    return result


def get_messages(uid: "str.user_id", db_path: str) -> "list.messages":
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # usare questa sezione per aggiungere altre query ...
    query = f"select uid, date, data, out from messages where uid = {uid}  order by date asc"
    get_name = f"select name from users where uid = {uid}"

    c.execute(query)
    data = c.fetchall()

    c.execute(get_name)
    name = c.fetchall()

    conn.close()

    return (name[0], data)


# 532005619
def main():
    db_path = 'cache4.db'

    # devo specificare l'id che voglio cercare
    if len(sys.argv) <= 1:
        print("Missing UID ...")
        quit()

    name, data = get_messages(sys.argv[1], db_path)

    # parsing dei messaggi
    for i in range(len(data)):
        type_ = ""

        if data[i][3] == 0:
            type_ = "in "   # messaggio ricevuto
        else:
            type_ = "out"   # messaggio inviato

        print(i+1, name,  type_, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(data[i][1])), blob_parser(data[i][2]))
        # print(i+1, data[i][0],  type_, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(data[i][1])), blob_parser(data[i][2]))
        # print(i+1, data[i][0],  type_, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(data[i][1])), parse_telegram_messages(data[i][2]))
        # print(i+1, data[i][2].decode("ascii", "ignore"))

    print("")
    print("-" * 100)
    print(f"Messages from/to {name} ({data[0][0]})\n")


if __name__ == "__main__":
    main()
