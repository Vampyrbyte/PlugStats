#!/usr/bin/env python3
from pyHS100 import SmartPlug
from influxdb import InfluxDBClient
from time import sleep, localtime, strftime
import datetime
import traceback
import sdnotify
import sys

plug = SmartPlug("192.168.1.26") #Bedroom Lights
influx = InfluxDBClient(database="SmartPlug")
now = datetime.datetime.now()

n = sdnotify.SystemdNotifier()
n.notify("READY=1")
def main():
	while True:
		try:
	#Get Stats from SmartPlug
			realtime = plug.get_emeter_realtime()
			daily_power = plug.get_emeter_daily()
			daily_power = daily_power.get(now.day)
			monthly_power = plug.get_emeter_monthly()
			monthly_power = monthly_power.get(now.month)
#	print(type(daily_power))
#	print(type(monthly_power))
			voltage = realtime["voltage_mv"]
			current = realtime["current_ma"]
			power = realtime ["power_mw"]
			alias = plug.alias
			state = plug.state
			rssi = plug.rssi

	#Post Stats to InfluxDB
			influx.write_points([{
				"measurement": "SmartPlug",
				"fields": {
					"daily_power": daily_power,
					"monthly_power": monthly_power,
					"voltage": voltage,
					"current": current,
					"power": power,
					"alias": alias,
					"state": state,
					"rssi": rssi
				}
			}])
			timestamp = strftime("%y-%m-%d %H:%M:%S %z", localtime())
			n.notify("STATUS=Report to InfluxDB at {}".format(timestamp))
			sleep(10)
		except Exception as e:
			msg = "Failed to report to InfluxDB:"
			n.notify("STATUS={} {}".format(msg, str(e)))
			sys.exit(1)
#	LoopStop = False
if __name__ == "__main__":
	main()
