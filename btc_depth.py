# coding: utf-8


import datetime as dt
import calendar

import requests
import bs4
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def timestamp_now():
    d = dt.datetime.utcnow()
    return calendar.timegm(d.utctimetuple())


def update():
    req = bs4.BeautifulSoup(
        requests.get("https://www.bitcoin.de/de/market").text
    )

    actions = [
        (
            el.get("data-trade-type"),
            float(el.get("data-amount")),
            float(el.get("data-critical-price")),
        )
        for el in req.findAll('tr')
        if el.has_attr("data-trade-type")
    ]

    orders, offers = [], []
    [
        (
            orders if trade_type == "order" else offers
        ).append([amnt, price])
        for (trade_type, amnt, price) in actions
    ]
    return timestamp_now(), np.array(orders), np.array(offers)


q = [update()]  # make sure non-empty to start otherwise plot3d fails


def update_3d():
    fig = plt.figure()
    fig.clf()
    q.append(update())
    X, Y, Z = [], [], []
    for idx, (timestamp, orders, offers) in enumerate(q):
        for x, y in zip(orders[:, 1], np.cumsum(orders[:, 0] * orders[:, 1])):
            X.append(x)
            Y.append(y/1000)
            Z.append(timestamp)
        X.append((orders[:, 1][0] + offers[:, 1][0]) / 2)
        Y.append(0)
        Z.append(timestamp)
        for x, y in zip(offers[:, 1], np.cumsum(offers[:, 0] * offers[:, 1])):
            X.append(x)
            Y.append(y/1000)
            Z.append(timestamp)
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(Z, X, Y, cmap=plt.cm.gist_earth, linewidth=0.2)
    ax.set_xlabel(u"Time (Seconds)")
    ax.set_ylabel(u"Price (€/BTC)")
    ax.set_zlabel(u"Volume (k€)")
    plt.show()
