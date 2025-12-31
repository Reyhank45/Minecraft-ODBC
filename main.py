import time
import re
import mysql.connector
from nbtlib import parse_nbt
import json
from mcrcon import MCRcon, MCRconException

db = mysql.connector.connect(
    host="hostname db",
    user="user db",
    password="passwd db",
    database="db"
)
cursor = db.cursor()

class RCONMonitor:
    def get_query_args(self, mcr):
        try:
            response = mcr.command("data get storage mc:args")
            nbt_str = response.split("Storage mc:args has the following contents: ")[-1]
            return parse_nbt(nbt_str)

        except Exception as e:
            print(f"Nbt error: {e}")
            return None

    def monitor_rcon(self):
        while True:
            try:
                with MCRcon("hostname", "pass", port=25575) as mcr:
                    while True:
                        response = mcr.command("scoreboard players get ServerTrigger db_trigger")
                        responsejson = json.dumps(re.findall(r"\d+", response))
                        data = json.loads(responsejson)
                        responseparsed = data[0]
                        if "1" in responseparsed:
                            args = self.get_query_args(mcr)
                            sql_query = args['query']
                            #sql_args = args['params']
                            cursor.execute(sql_query)
                            queryresult = cursor.fetchone()
                            mcr.command(f"/say {queryresult}")
                            mcr.command("scoreboard players set ServerTrigger db_trigger 0")
                            mcr.command("data remove storage mc:args")

                        time.sleep(0.3)
            except Exception as e:
                print(f"monitor error {e}")
                return None

    def run(self):
        while True:
            self.connection_retries = 0
            print("[+]connection established")
            self.monitor_rcon()
            time.sleep(0.3)
            #print("connection error")
                

if __name__ == "__main__":
    monitor = RCONMonitor()
    monitor.run()
