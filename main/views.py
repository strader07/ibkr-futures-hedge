from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect  # get_object_or_404
from django.template import loader
from django.http import HttpResponse  # JsonResponse
from django import template
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt

from .models import *
from .tick import Tick
from .config import *

from datetime import datetime, timedelta, date
from sortedcontainers import SortedDict
from threading import Thread
import threading
import requests
import time
import json
import re
import logging

from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from ib.ext.Order import Order

global tickers
tickers = SortedDict()
global TickPrices
TickPrices = SortedDict()
global tickId
tickId = 0

log = logging.getLogger(__name__)


class TickPrice():
    def __init__(self, symbol):
        self.symbol = symbol
        self.bid = None
        self.ask = None

    def get_BidAsk(self, msg):
        if msg.field == 1:
            self.bid = msg.price
        if msg.field == 2:
            self.ask = msg.price


class OrderHandler():
    def __init__(self,conn):
        self.nextValidOrderId = None
        self.orderStatus = {}
        # conn.registerAll(self.debugHandler)
        conn.register(self.nextValidIdHandler,'NextValidId')
        conn.register(self.getOrderStatus, message.orderStatus)

    def nextValidIdHandler(self, msg):
        self.nextValidOrderId = msg.orderId

    def debugHandler(self, msg):
        print (msg)

    def getOrderStatus(self, msg):
        self.orderStatus[str(msg.orderId)] = msg.status


con = ibConnection("127.0.0.1", 7497, 23)
con.connect()
time.sleep(1)
orderHandler = OrderHandler(con)


def getContract(symbol):
    symbol = symbol.upper()
    if "-" in symbol:
        _symbol = symbol.split("-")[0].strip()
        m = symbol.split("-")[1].strip()
        _month = str(int(m[1]) + 2020) + MONTH_DICT[m[0]]
    else:
        if "K200" in symbol or "N225M" in symbol:
            _symbol = "K200" if "K200" in symbol else "N225M"
            m = symbol.replace(_symbol, "").strip("-., ")
            _month = str(int(m[1]) + 2020) + MONTH_DICT[m[0]]
        else:
            m = re.findall(r"\d+\s*$", symbol)
            _month = str(int(m[0]) + 2020) + MONTH_DICT[symbol.replace(m[0], "")[-1]]
            _symbol = symbol.replace(m[0], "")[:-1]

    currency = "JPY" if _symbol=="N225M" else "KRW" if _symbol=="K200" else "USD"

    if _symbol in EXCHANGES:
        exchange = EXCHANGES[_symbol]
    else:
        exchange = "GLOBEX"
        exit()

    contractTuple = (_symbol, "FUT", exchange, currency, _month)

    contract = Contract()
    contract.m_symbol = contractTuple[0]
    contract.m_secType = contractTuple[1]
    contract.m_exchange = contractTuple[2]
    contract.m_currency = contractTuple[3]
    contract.m_expiry = contractTuple[4]

    return contract


def get_tick_price(key):
    global tickId
    tickId = tickId + 1
    tickPrice = TickPrice(key)
    con.register(tickPrice.get_BidAsk, message.tickPrice)
    contract = getContract(key)
    # con.reqMarketDataType(4)
    con.reqMktData(tickId, contract, "", True)
    time.sleep(1)
    bid = tickPrice.bid if tickPrice.bid else 9999999
    ask = tickPrice.ask if tickPrice.ask else 0
    del tickPrice
    return {"symbol":key, "bid":bid, "ask":ask}


@login_required(login_url="/login/")
def index(request):
    context = {}
    positions = Position.objects.all()
    context["positions"] = positions
    return render(request, "index.html", context)


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        print(request.path)
        load_template = request.path.split("/")[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template("error-404.html")
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template("error-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def new_position(request):
    if request.method == "POST":
        name = request.POST.get("name")
        symbol = request.POST.get("symbol")
        num_contract = int(request.POST.get("num_contract"))
        tick = float(request.POST.get("tick"))
        long_dpp = float(request.POST.get("long_dpp"))
        long_dpp_up = int(request.POST.get("long_dpp_up"))
        long_dpp_dn = int(request.POST.get("long_dpp_dn"))
        short_dpp = float(request.POST.get("short_dpp"))
        short_dpp_up = int(request.POST.get("short_dpp_up"))
        short_dpp_dn = int(request.POST.get("short_dpp_dn"))
        is_active = request.POST.get("is_active")
        if is_active == "on":
            is_active = True
        else:
            is_active = False

        position = Position(
            name=name,
            symbol=symbol,
            num_contract=num_contract,
            tick=tick,
            long_dpp=long_dpp,
            long_dpp_up=long_dpp_up,
            long_dpp_dn=long_dpp_dn,
            short_dpp=short_dpp,
            short_dpp_up=short_dpp_up,
            short_dpp_dn=short_dpp_dn,
            is_active=is_active
        )
        position.save()
        messages.info(request, "New position successfully created!")

        return redirect("/")
    else:
        return render(request, "new-position.html")


@login_required(login_url="/login/")
def edit_position(request, pk=0):
    try:
        position = Position.objects.get(id=pk)
        if request.method == "GET":
            return render(request, "edit-position.html", {"position": position, "pk":pk})
        else:
            name = request.POST.get("name")
            symbol = request.POST.get("symbol")
            num_contract = int(request.POST.get("num_contract"))
            tick = float(request.POST.get("tick"))
            long_dpp = float(request.POST.get("long_dpp"))
            long_dpp_up = int(request.POST.get("long_dpp_up"))
            long_dpp_dn = int(request.POST.get("long_dpp_dn"))
            short_dpp = float(request.POST.get("short_dpp"))
            short_dpp_up = int(request.POST.get("short_dpp_up"))
            short_dpp_dn = int(request.POST.get("short_dpp_dn"))
            is_active = request.POST.get("is_active")
            if is_active == "on":
                is_active = True
            else:
                is_active = False

            position.name = name
            position.symbol = symbol
            position.num_contract = num_contract
            position.tick = tick
            position.long_dpp = long_dpp
            position.long_dpp_up = long_dpp_up
            position.long_dpp_dn = long_dpp_dn
            position.short_dpp = short_dpp
            position.short_dpp_up = short_dpp_up
            position.short_dpp_dn = short_dpp_dn
            position.is_active = is_active
            position.save()

            messages.info(request, "The position successfully updated!")
            return redirect("/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/login/")
def active_position(request, pk=0):
    try:
        position = Position.objects.get(id=pk)
        print(request.body, pk)

        messages.info(request, "The position status successfully updated!")
        return redirect("/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/login/")
def del_position(request, pk=0):
    try:
        position = Position.objects.get(id=pk)
        position.delete()

        messages.info(request, "The position successfully deleted!")
        return redirect("/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/login/")
def delete_positions(request):
    positions = Position.objects.all()
    for position in positions:
        position.delete()
    return redirect("/")


def place_stop_limit_order(position, side, hedge):
    if hedge == "LONG":
        if side == "BUY":
            stop_price = position.long_dpp
            limit_price = position.long_dpp + position.tick*position.long_dpp_up
        else:
            stop_price = position.long_dpp
            limit_price = position.long_dpp - position.tick*position.long_dpp_dn
    else:
        if side == "SELL":
            stop_price = position.short_dpp
            limit_price = position.short_dpp - position.tick*position.short_dpp_dn
        else:
            stop_price = position.short_dpp
            limit_price = position.short_dpp + position.tick*position.short_dpp_up

    symbol = position.symbol
    contract = getContract(symbol)
    order = Order()
    # order.m_orderType = 'MKT'
    order.m_orderType = 'STP LMT'
    order.m_totalQuantity = position.num_contract
    order.m_action = side
    order.m_lmtPrice = limit_price
    order.m_auxPrice = stop_price
    order.m_outsideRth = True

    con.reqIds(-1)
    time.sleep(1)
    orderId = orderHandler.nextValidOrderId

    con.placeOrder(orderId, contract, order)
    time.sleep(2)

    return {"order": order, "order_id": orderId}


def process_hedge(ticker):
    symbol = ticker.symbol
    position = ticker.position
    quote = get_tick_price(symbol)
    log.info(f"quote: {quote}")

    if ticker.long_hedge_side=="BUY" and not ticker.long_hedge_order:
        if quote["ask"] > position.long_dpp:
            ticker.long_hedge_order = place_stop_limit_order(position, "BUY", "LONG")
            ticker.long_hedge_side = "SELL"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.long_hedge_order}")
            if orderHandler.orderStatus[str(ticker.long_hedge_order["order_id"])].upper() == "FILLED":
                ticker.long_hedge_filled = True
    if ticker.long_hedge_order and not ticker.long_hedge_filled:
        con.reqAllOpenOrders()
        time.sleep(1)
        log.info(f"{orderHandler.orderStatus}, {ticker.long_hedge_order}")
        if orderHandler.orderStatus[str(ticker.long_hedge_order["order_id"])].upper() == "FILLED":
            ticker.long_hedge_filled = True
    if ticker.long_hedge_side == "BUY" and ticker.long_hedge_filled:
        if quote["ask"] > position.long_dpp:
            ticker.long_hedge_order = place_stop_limit_order(position, "BUY", "LONG")
            ticker.long_hedge_side = "SELL"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.long_hedge_order}")
            if orderHandler.orderStatus[str(ticker.long_hedge_order["order_id"])].upper() == "FILLED":
                ticker.long_hedge_filled = True
    if ticker.long_hedge_side == "SELL" and ticker.long_hedge_filled:
        if quote["bid"] < position.long_dpp:
            ticker.long_hedge_order = place_stop_limit_order(position, "SELL", "LONG")
            ticker.long_hedge_side = "BUY"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.long_hedge_order}")
            if orderHandler.orderStatus[str(ticker.long_hedge_order["order_id"])].upper() == "FILLED":
                ticker.long_hedge_filled = True

    if ticker.short_hedge_side=="SELL" and not ticker.short_hedge_order:
        if quote["bid"] < position.short_dpp:
            ticker.short_hedge_order = place_stop_limit_order(position, "SELL", "SHORT")
            ticker.short_hedge_side = "BUY"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.short_hedge_order}")
            if orderHandler.orderStatus[str(ticker.short_hedge_order["order_id"])].upper() == "FILLED":
                ticker.short_hedge_filled = True
    if ticker.short_hedge_order and not ticker.short_hedge_filled:
        con.reqAllOpenOrders()
        time.sleep(1)
        log.info(f"{orderHandler.orderStatus}, {ticker.short_hedge_order}")
        if orderHandler.orderStatus[str(ticker.short_hedge_order["order_id"])].upper() == "FILLED":
            ticker.short_hedge_filled = True
    if ticker.short_hedge_side == "SELL" and ticker.short_hedge_filled:
        if quote["bid"] < position.short_dpp:
            ticker.short_hedge_order = place_stop_limit_order(position, "SELL", "SHORT")
            ticker.short_hedge_side = "BUY"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.short_hedge_order}")
            if orderHandler.orderStatus[str(ticker.short_hedge_order["order_id"])].upper() == "FILLED":
                ticker.short_hedge_filled = True
    if ticker.short_hedge_side == "BUY" and ticker.short_hedge_filled:
        if quote["ask"] > position.short_dpp:
            ticker.short_hedge_order = place_stop_limit_order(position, "BUY", "SHORT")
            ticker.short_hedge_side = "SELL"
            con.reqAllOpenOrders()
            time.sleep(1)
            log.info(f"{orderHandler.orderStatus}, {ticker.short_hedge_order}")
            if orderHandler.orderStatus[str(ticker.short_hedge_order["order_id"])].upper() == "FILLED":
                ticker.short_hedge_filled = True

    return ticker


def run_hedge():
    while True:
        positions = Position.objects.filter(is_active=True)
        pos_symbols = [pos.symbol for pos in positions]
        del_keys = []
        for key in tickers:
            if key not in pos_symbols:
                del_keys.append(key)
        for key in del_keys:
            del tickers[key]

        for position in positions:
            if position.symbol not in tickers:
                key = position.symbol
                ticker = Tick(position.symbol, position)
                tickers[key] = ticker
            else:
                ticker = tickers[position.symbol]
                ticker.position = position

        log.info(f"Active products: {str(list(tickers.keys()))}\n")

        for key in tickers:
            ticker = tickers[key]
            tickers[key] = process_hedge(ticker)

        time.sleep(5)
        # break


th_hedge = Thread(target=run_hedge, name="ThreadHedge")
th_hedge.start()