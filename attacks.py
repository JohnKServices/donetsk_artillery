import json
import re
import pandas as pd
import matplotlib.pyplot as plt


class Donetsky:

    def newGraph(self):
        self.subnum +=1
        self.fig.add_subplot(self.subnum)
    
    def __init__(self, data_file):

        self.data = json.load(open(data_file, encoding='utf-8'))
        self.hourofAttack = []
        self.dayofAttack = []
        self.methodUsed = []
        self.locations = []
        self.fig= plt.figure(figsize=[15,15])
        self.infra = [i['date'] for i in self.data['infra']]
        self.subnum = 330

        for i in self.data['messages']:
            self.dayofAttack.append(i['date'][:-9])
            for message in i['text']:
                time = re.findall(r"▶️\d{2}:\d{2}", str(message))
                artillery = re.findall(r"(\d{1}) (снаряда|снарядов|мин|мины) калибром (\d{3}) мм", str(message))
                MLRS = re.findall(r"([0-9]|[1-9][0-9]|[1-9][0-9][0-9]) (ракет|ракеты) из( РСЗО)? (БМ-21|БМ-27|HIMARS|«Himars»|\\\"HIMARS\\\")", str(message), re.IGNORECASE)

                if time and len(time) == 1:
                    self.hourofAttack.append(time[0].replace('▶️', '') + ':00')

                elif artillery and len(artillery) == 1:
                    for i in range(int(artillery[0][0])):
                        self.methodUsed.append([int(artillery[0][2]), self.dayofAttack[-1]])

                elif MLRS and len(MLRS) == 1:
                    for i in range(int(MLRS[0][0])):
                        if MLRS[0][3] == "БМ-21":
                            self.methodUsed.append([122, self.dayofAttack[-1]])
                        elif MLRS[0][3] == "БМ-27": 
                            self.methodUsed.append([203, self.dayofAttack[-1]])
                        elif MLRS[0][3] == "HIMARS" or "«Himars»":
                            self.methodUsed.append([227, self.dayofAttack[-1]])

        assert self.hourofAttack and self.dayofAttack and self.methodUsed and self.infra, "Invalid data file"
        
    def hourGraph(self):
        self.newGraph()
        # Load the data into a DataFrame and set the hour as the index
        df = pd.DataFrame(self.hourofAttack, columns=['hour'])
        df['hour'] = pd.to_timedelta(df['hour'])
        df.set_index('hour', drop=False, inplace=True)

        # Group the data by hour and plot the counts
        ax = df.groupby(pd.Grouper(freq='1H')).count()['hour'].plot(kind='bar', xlabel='', ylabel='Incidents', title='Distribution by time of day')

        # Set the x-axis tick marks and labels
        ax.set_xticks(range(0, 24))
        ax.set_xticklabels(range(0, 24), fontsize=9)

        # Set the title and labels for the axes

        # Hide every other x-axis tick label
        [l.set_visible(False) for (i, l) in enumerate(ax.xaxis.get_ticklabels()) if i % 2 != 0]

    def weekdayGraph(self):
        self.newGraph()

        # Define the categories for the x-axis (weekdays)
        cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Load the data into a DataFrame and set the weekdays as the index
        df = pd.DataFrame(self.dayofAttack, columns=['weekday'])
        df['weekday'] = pd.to_datetime(df['weekday']).dt.day_name()

        # Sort the weekdays by the defined categories
        df['weekday'] = pd.Categorical(df['weekday'], categories=cats, ordered=True).sort_values()

        # Group the data by weekdays and plot the counts
        df.groupby('weekday').size().plot(kind='bar', title='Distribution of weekdays', xlabel='')

    def strikesGraph(self):
        self.newGraph()
        df = pd.DataFrame(self.dayofAttack, columns=['date'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', drop=False, inplace=True)
        df = df.loc['2014-01-01':'2022-11-03']

        # Group the data by 5-day periods and plot the counts
        df.groupby(pd.Grouper(freq='5D')).count()['date'].plot(title='Claimed strikes (5 day sample)', xlabel='')

    def caliberGraph(self):
        self.newGraph()
        df = pd.DataFrame([i[0] for i in self.methodUsed], columns=['caliber']).sort_values('caliber').groupby('caliber').value_counts()
        df = df[df.values >= 100]
        df.plot(kind='bar', title='Calibers used in attacks')
    
    def ammoGraph(self, sample):
        self.newGraph()
        # Load the data into a DataFrame and set the date as the index
        df = pd.DataFrame(self.methodUsed, columns=['caliber', 'date'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', drop=False, inplace=True)
        df = df.loc['2014-01-01':'2022-11-03']
        df.groupby(pd.Grouper(freq=sample)).count()['date'].plot(xlabel='', title='Total shots by Ukraine')

    def infraGraph(self, sample):
        self.newGraph()
        df = pd.DataFrame(self.infra, columns=['date'])
        df['date'] = pd.to_datetime(df['date'],format="%d.%m.%Y")
        df.set_index('date', drop=False, inplace=True)
        
        # Group the data by the specified time period (sample) and plot the counts
        df.groupby(pd.Grouper(freq=sample)).count()['date'].plot(ylabel='Infrastructure strikes', xlabel='')
    
        
donetsky = Donetsky('result.json')
donetsky.ammoGraph('5D')
