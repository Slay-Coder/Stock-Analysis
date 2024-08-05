from datetime import datetime as date
from datetime import timedelta
import plotly.graph_objs as go
import plotly.express as px
import yfinance as yf
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split


#predict stock prices
def predict(stock, days_n):
    df = yf.download(stock, period='1y') 
    df.reset_index(inplace=True)
    df['Day'] = df.index

    days = [[i] for i in range(len(df.Day))]
    X = days
    Y = df[['Close']]
    
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, shuffle=False)
    y_train = y_train.values.ravel()

    param_grid = {
        'C': [0.1, 1, 100, 1000],
        'epsilon': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10],
        'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5]
    }

    splits = min(5, len(x_train))  
    gsc = GridSearchCV(estimator=SVR(kernel='rbf'), param_grid=param_grid, cv=splits, scoring='neg_mean_squared_error', verbose=0, n_jobs=-1)
    grid_result = gsc.fit(x_train, y_train)
    best_params = grid_result.best_params_

    best_svr = SVR(kernel='rbf', C=best_params['C'], epsilon=best_params['epsilon'], gamma=best_params['gamma'])
    best_svr.fit(x_train, y_train)

    output_days = [[i + x_test[-1][0] + 1] for i in range(days_n)]

    dates = [date.today() + timedelta(days=i) for i in range(1, days_n + 1)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=best_svr.predict(output_days), mode='lines+markers', name='Prediction'))
    fig.update_layout(title=f"Predicted Close Price for the Next {days_n} Days",
                      xaxis_title="Date",
                      yaxis_title="Close Price",
                      legend_title="Prediction")

    return fig
