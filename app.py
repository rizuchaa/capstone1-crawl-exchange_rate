from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests
import seaborn as sns

#  don't change this
matplotlib.use('Agg')
app = Flask(__name__, static_url_path='/static') 

# do not change this

#  insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content, "html.parser")

table = soup.find('table', attrs={'table table-striped table-hover table-hover-solid-row table-simple history-data'})
[class_inline.extract() for class_inline in table.find_all("tr", {'class':'inline-grid-ad-row'})]
tr = table.find_all('tr')
temp = []   # initiating a tuple

for i in range(0, len(tr)):
    #   insert the scrapping process here
    row = table.find_all('tr')[i]

    #  get date
    date = row.find_all('td')[0].text

    #  get er
    er = row.find_all('td')[2].text

    temp.append((date, er))
temp = temp[::-1]

#  change into dataframe
data = pd.DataFrame(temp, columns=('Date', 'Exchange_Rate'))

#  insert data wrangling here
datefirst = data.Date.iloc[0]
datelast = data.Date.iloc[-1]
data['Date'] = pd.to_datetime(data.Date, format='%m/%d/%Y', dayfirst=True)
data.Exchange_Rate = data.Exchange_Rate.apply(lambda x: x.replace(',', '')).\
    apply(lambda x: x.replace(' IDR', '')).\
    astype('float64')
data = data.set_index('Date')
#  end of data wranggling
plt.style.use('seaborn-whitegrid')

@app.route("/")
def index():

    card_data = f'IDR {round(data["Exchange_Rate"].mean(), 2)}'

    # generate plot
    ax = data.plot(figsize=(13,7))

    # Rendering plot

    # Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]

    #addition
    date_show = f'Reported Period : {datefirst} - {datelast}'
    # render to html
    return render_template('index.html',
        card_data = card_data,
        plot_result = plot_result,
        date_show = date_show
        )


if __name__ == "__main__":
    app.run(debug=True)
