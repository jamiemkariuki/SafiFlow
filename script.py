import datetime as dt
import DeviceID
device_id = DeviceID.generate_device_id()
while True:
    ct = dt.datetime.now()
    answer = input("Enter your choice: ")
    if answer == 'Device ID':
        print(device_id)
    elif answer == "Measure energy usage":
        energy_usage =  input("Enter energy usage in kWh: ")
        print(f"Energy usage recorded on {ct}:\n{energy_usage} kWh")
    elif answer == "Measure energy collected":
        energy_collected =  input("Enter energy usage in kWh: ")
        print(f"Energy collected recorded on {ct}:\n{energy_collected} kWh")
    elif answer == "Measure water purified":
        water_purified =  input("Enter energy usage in kWh: ")
        print(f"Water purified recorded on {ct}:\n{water_purified} litres")
    elif answer == 'Exit':
        break
    else:
        print("Unknown command. Please try again.")