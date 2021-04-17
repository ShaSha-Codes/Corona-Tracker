from flask import Flask, render_template,request
import requests
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plt
import os


app = Flask(__name__)

@app.route('/')
def home():
    url = 'https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = []
    data_iterator = iter(soup.find_all('td'))
    spans = soup.findAll('span')
    spans=spans[4].text
    spans=spans.split(" ")

    url2="https://www.worldometers.info/coronavirus/#countries"
    page2=requests.get(url2)
    soup2=BeautifulSoup(page2.text,'html.parser')
    closedCases=soup2.findAll(class_="number-table-main")
    closedCases=closedCases[1].text
    closedCases=int(closedCases.replace(',',''))


    while True:
        try:
            country = next(data_iterator).text
            confirmed = next(data_iterator).text
            deaths = next(data_iterator).text
            continent = next(data_iterator).text
            data.append((
                country,
                int(confirmed.replace(',', '')),
                int(deaths.replace(',', '')),
                continent
            ))
        except StopIteration:
            break

    #Sorted the Data in highest first
    data.sort(key=lambda row: row[1], reverse=True)

    #Creating the tablele
    table="<tbody>"
    continents={"Australia/Oceania": [0,0], "Europe": [0,0], "Asia":[0,0], "North America": [0,0], "South America": [0,0], "Africa": [0,0]}
    for i in range(len(data)):
        table+="<tr>"
        table+="<td>"+data[i][0]+"</td>"
        table+= "<td>"+str(data[i][1])+"</td>"
        table+= "<td>"+str(data[i][2])+"</td>"
        table+= "<td>"+data[i][3]+"</td>"
        table+="</tr>"
        #For getting the total number of cases and deaths in Continents
        try:
            continents[data[i][3]][0]+=data[i][1]
            continents[data[i][3]][1]+=data[i][2]
        except:
            pass
    table+="</tbody>"

    #Continent Table
    con="<tr>"
    num=0
    deaths=0
    for i in continents.keys():
        con+="<th><h5>"+i+"</h5><br><h6> Cases: "+str(continents[i][0])+"<br> Deaths: "+str(continents[i][1])+"<h6></th>"
        deaths+=continents[i][1]
        num+=1
        if num==2 or num==4:
            con+="</tr><tr>"
    con+="<tr>"
    death=""
    rec=closedCases-deaths
    recovered=""
    count=0
    for j in str(deaths):
        count+=1
        death+=j
        if(count%3==0):
            death+=","
    count1=0
    for k in str(rec):
        count+=1
        recovered+=k
        if (count % 3 == 0):
            recovered += ","

    return render_template('index.html',main_table=table,continent_table=con,total_cases=spans[0],total_deaths=death,total_recovered=recovered)

@app.route('/India')
def states():
    try:
        os.remove("static\plot.png")
    except:
        pass
    response = requests.get("https://api.rootnet.in/covid19-in/stats/latest")
    json_data = json.loads(response.text)
    data=""
    for i in range(36):
        data+="<tr>"
        for j in json_data["data"]["regional"][i].values():
            data+="<td>"+str(j)+"</td>"
        data+="<tr>"
    response = requests.get("https://api.rootnet.in/covid19-in/stats/history")
    json_data = json.loads(response.text)
    print(json_data.keys())
    print(json_data["data"][0]["summary"]["total"])
    cases = []
    discharged = []
    deaths = []
    days = []
    for i in range(len(json_data["data"])):
        cases.append(json_data["data"][i]["summary"]["total"])
        days.append(i)
        discharged.append(json_data["data"][i]["summary"]["discharged"])
        deaths.append(json_data["data"][i]["summary"]["deaths"])
        maxRec=json_data["data"][i]["summary"]["discharged"]
        maxDea=json_data["data"][i]["summary"]["deaths"]

    plt.plot(days, cases, label="Total Cases")
    plt.plot(days, discharged, label="Recovered")
    plt.plot(days, deaths, label="Deaths")
    plt.xlabel('Days')
    plt.ylabel('Number of People')
    plt.title('Total vs Recovery vs Death')
    plt.legend()
    plt.savefig('static\plot.png')
    plt.clf()

    labels = 'Recovered','Deaths'
    sizes = [maxRec,maxDea]
    colors = ['lightskyblue','lightcoral']
    explode = (0.1, 0)  # explode 1st slice

    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.title('Recovery vs Death')
    plt.savefig('static\plot2.png')
    plt.clf()
    return render_template('India.html',table=data,url="static\plot.png",url2='static\plot2.png')

@app.route('/IndiaCondition', methods=['POST','GET'])
def statesCondition():
    try:
        os.remove("static\plot.png")
    except:
        pass
    x = request.form.get("states")
    data=""
    response = requests.get("https://api.rootnet.in/covid19-in/stats/latest")
    json_data = json.loads(response.text)
    for i in range(36):
        if(json_data["data"]["regional"][i]["loc"]==x):
            data += "<tr>"
            for j in json_data["data"]["regional"][i].values():
                data += "<td>" + str(j) + "</td>"
            data += "<tr>"
            break




    response = requests.get("https://api.rootnet.in/covid19-in/stats/history")
    json_data = json.loads(response.text)
    print(json_data.keys())
    print(json_data["data"][0]["summary"]["total"])
    cases = []
    discharged = []
    deaths = []
    days = []
    for i in range(len(json_data["data"])):
        for j in range(len(json_data["data"][i]["regional"])):
            if(json_data["data"][i]["regional"][j]["loc"]==x):
                cases.append(json_data["data"][i]["regional"][j]["totalConfirmed"])
                days.append(i)
                discharged.append(json_data["data"][i]["regional"][j]["discharged"])
                deaths.append(json_data["data"][i]["regional"][j]["deaths"])
                maxRec = json_data["data"][i]["regional"][j]["discharged"]
                maxDea = json_data["data"][i]["regional"][j]["deaths"]

    plt.plot(days, cases, label="Total Cases")
    plt.plot(days, discharged, label="Recovered")
    plt.plot(days, deaths, label="Deaths")
    plt.xlabel('Days')
    plt.ylabel('Number of People')
    plt.title('Total vs Recovery vs Death')
    plt.legend()
    plt.savefig('static\plot.png')
    plt.clf()

    labels = 'Recovered', 'Deaths'
    sizes = [maxRec, maxDea]
    colors = ['lightskyblue', 'lightcoral']
    explode = (0.1, 0)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.title('Recovery vs Death')
    plt.savefig('static\plot2.png')
    plt.clf()
    return render_template('India.html', table=data, url="static\plot.png", url2='static\plot2.png')

@app.route('/AboutUs')
def aboutUs():
    return render_template('AboutUs.html')

@app.route('/Coping')
def Coping():
    return render_template('Coping.html')

if __name__ == '__main__':
   app.run(debug=True)