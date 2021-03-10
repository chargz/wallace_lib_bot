import json
import requests

url1 = "https://hooks.slack.com/services/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"

with open('init2.json') as rd:
    data = json.load(rd)

roomMap = {
"302":"2472",
"303":"2474",
"304":"2476",
"305":"2478",
"306":"2480",
"317":"3415",
"318":"3420",
"319":"3455",
"322":"3474",
"323":"3476",
"324":"3478",
"325":"3480",
"326":"3484",
"337":"4470",
"338":"4472",
"339":"4474",
"340":"4476",
"341":"4478",
"342":"4480",
"343":"4482",
"344":"4686",
"345":"4688"
}

tmpstr = ""
for i in range(0,len(data["Bookings"])):
    name = str(data["Bookings"][i]["GroupName"])
    try:
        name = name.split(",")[1] + " " + name.split(",")[0]
        name = name.replace(",","")
    except:
        continue

    room = str(data["Bookings"][i]["BookingInRoomId"])

    timeStart = str(data["Bookings"][i]["TimeBookingStart"])
    timeStart = timeStart.split("T")[-1][:-3]

    timeEnd = str(data["Bookings"][i]["TimeBookingEnd"])
    timeEnd = timeEnd.split("T")[-1][:-3]

    tmpstr += name+" @ "+roomMap[room]+", "+timeStart+"-"+timeEnd+"\n"

slack_data = {'text': tmpstr}
requests.post(url1, headers={'Content-Type': 'application/json'}, data = json.dumps(slack_data))