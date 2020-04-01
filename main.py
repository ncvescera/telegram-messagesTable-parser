import sqlite3
import time
import sys


def blob_parser(data: "binary string"):
    offset_len_msg = 28
    start_msg = 29  # potrebbe essere anche 32 dipende da offset_len_msg

    # print("hex:", hexToStr(data[offset_len_msg].to_bytes(1, 'little')), "dec:", data[offset_len_msg])

    ln = data[offset_len_msg]

    result = ""

    try:
        result = data[start_msg:(start_msg+ln)].decode("utf-8")
    except Exception:
        result = data[start_msg:(start_msg+ln)]

    return result


# 532005619
def main():
    conn = sqlite3.connect('cache4.db')

    if len(sys.argv) <= 1:
        quit()

    c = conn.cursor()
    c.execute(f"select uid, date, data, out from messages where uid = {sys.argv[1]}  order by date desc")
    data = c.fetchall()
    conn.close()

    for i in range(len(data)):
        type_ = ""

        if data[i][3] == 0:
            type_ = "in "
        else:
            type_ = "out"

        print(i+1, data[i][0],  type_, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(data[i][1])), blob_parser(data[i][2]))
        # print(i+1, data[i][0],  type_, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(data[i][1])), parse_telegram_messages(data[i][2]))
        # print(i+1, data[i][2].decode("ascii", "ignore"))


if __name__ == "__main__":
    main()
