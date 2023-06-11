import tkinter
import customtkinter as ctk
from PIL import Image
import os
import json
import pyautogui
from binance_connector import GetHistoricalData, getAllTradingCoins, getAccountInfos, getAvgPrice
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import requests
from urllib.request import urlopen


class App(ctk.CTk):
    width = 900
    height = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        ctk.set_appearance_mode("system")
    
        #Set width, height and name
        self.title("Cryptocurrency Trading Dashboard")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(True, True)
        
        self.exchange_selected = tkinter.StringVar()
        self.apikey = tkinter.StringVar()
        self.apisecret = tkinter.StringVar()
        self.selected_pair = tkinter.StringVar().set("BTCUSDT")
        self.lastprice = tkinter.StringVar()
        self.change = tkinter.StringVar()
        self.volume = tkinter.StringVar()
        self.trades = tkinter.StringVar()
        self.experimental = tkinter.StringVar().set('off')
        self.fig, self.ax = plt.subplots()
        self.load_config()
                
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "imgs")

        self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "logo_light.png")), 
                                       dark_image=Image.open(os.path.join(image_path, "logo.png")), size=(113, 50))
        
        self.dashboard_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "dashboard.png")),
                                       dark_image=Image.open(os.path.join(image_path, "dashboard.png")), size=(20, 20))
        
        self.balances_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "balances.png")),
                                       dark_image=Image.open(os.path.join(image_path, "balances.png")), size=(20, 20))
        
        self.settings_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "settings.png")),
                                       dark_image=Image.open(os.path.join(image_path, "settings.png")), size=(20, 20))
        
        self.binance_logo = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "binance.png")),
                                       dark_image=Image.open(os.path.join(image_path, "binance.png")), size=(50, 30))
        
        self.bybit_logo = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "bybit.png")),
                                       dark_image=Image.open(os.path.join(image_path, "bybit.png")), size=(50, 30))

        # Navigation Frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # Logo
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="", image=self.logo_image,
                                                             compound="left")
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation - Buttons
        self.dashboard_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Dashboard",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.dashboard_image, anchor="w", command=self.dashboard_button_event)
        self.dashboard_button.grid(row=1, column=0, sticky="ew")

        self.balances_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Balances",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.balances_image, anchor="w", command=self.balances_button_event)
        self.balances_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.settings_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")


        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["System", "Light", "Dark"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        
        # Frames
        
        # Dashboard Frame
        self.dashboard = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.pulldata()
        self.dropdown_label = ctk.CTkLabel(self.dashboard, text="Select Trading Pair")
        self.dropdown_label.grid(row=0, column=0, padx=20, pady=10)
        self.lastprice_label = ctk.CTkLabel(self.dashboard, text="Last Price:")
        self.lastprice_label.grid(row=0, column=1, padx=20, pady=10)
        self.change_label = ctk.CTkLabel(self.dashboard, text="24H Change:")
        self.change_label.grid(row=0, column=2, padx=20, pady=10)
        self.volume_label = ctk.CTkLabel(self.dashboard, text="24H Volume:")
        self.volume_label.grid(row=0, column=3, padx=20, pady=10)
        self.trades_label = ctk.CTkLabel(self.dashboard, text="Amount of Trades (24H):")
        self.trades_label.grid(row=0, column=4, padx=20, pady=10)
        
        #EXPERIMENTALS TBD
        self.tradingpair_dropdown = ctk.CTkComboBox(self.dashboard, values=getAllTradingCoins() if self.experimental == "On" else ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'], variable=self.selected_pair, command=self.pulldata)
        self.tradingpair_dropdown.grid(row=1, column=0, padx=20, pady=10)
        self.lastprice_val = ctk.CTkLabel(self.dashboard, textvariable = self.lastprice)
        self.lastprice_val.grid(row=1, column=1, padx=20, pady=10)
        self.change_val = ctk.CTkLabel(self.dashboard, textvariable = self.change)
        self.change_val.grid(row=1, column=2, padx=20, pady=10)
        self.volume_val = ctk.CTkLabel(self.dashboard, textvariable = self.volume)
        self.volume_val.grid(row=1, column=3, padx=20, pady=10)
        self.trades_val = ctk.CTkLabel(self.dashboard, textvariable = self.trades)
        self.trades_val.grid(row=1, column=4, padx=20, pady=10)
      
        # Balances Frame
        self.balances = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        self.my_frame = ctk.CTkScrollableFrame(master=self.balances, width=700, height=600, corner_radius=0, fg_color="transparent")
        self.my_frame.grid(row=0, column=0, sticky="nsew")
        self.asset_image = ctk.CTkLabel(self.my_frame, text="Asset Image")
        self.asset_image.grid(row=0, column=0, padx=20, pady=10)
        self.asset_name_label = ctk.CTkLabel(self.my_frame, text="Asset Image")
        self.asset_name_label.grid(row=0, column=1, padx=20, pady=10)
        self.asset_balance = ctk.CTkLabel(self.my_frame, text="Asset Balance")
        self.asset_balance.grid(row=0, column=2, padx=20, pady=10)
        self.asset_price = ctk.CTkLabel(self.my_frame, text="Asset Price")
        self.asset_price.grid(row=0, column=3, padx=20, pady=10)
        self.asset_value = ctk.CTkLabel(self.my_frame, text="Total Value")
        self.asset_value.grid(row=0, column=4, padx=20, pady=10)
        self.addbalances()
        #Settings Frame
        self.settings = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.settings_status = tkinter.StringVar()
        
        self.settings_label = ctk.CTkLabel(self.settings, text="Select Exchange")
        self.settings_label.grid(row=0, column=0, padx=20, pady=10)
        self.settings_exchange_binance = ctk.CTkButton(self.settings, text="Binance", image=self.binance_logo, command=lambda: self.change_exchange("Binance"),  compound="top")
        self.settings_exchange_binance.grid(row=1, column=0, padx=50, pady=20)
        self.settings_exchange_bybit = ctk.CTkButton(self.settings, text="ByBit", image=self.bybit_logo, command=lambda: self.change_exchange("ByBit"),  compound="top")
        self.settings_exchange_bybit.grid(row=1, column=1, padx=50, pady=20)
        self.change_exchange(self.exchange_selected.get())

        
        
        self.settings_apikey_label = ctk.CTkLabel(self.settings, text="Enter your API KEY")
        self.settings_apikey_label.grid(row=2, column=0, padx=20, pady=10)
        self.settings_apikey = ctk.CTkEntry(self.settings, textvariable=self.apikey, placeholder_text="Enter your api key...")
        self.settings_apikey.grid(row=2, column=1, padx=50, pady=20)
        
        self.settings_apikey_label = ctk.CTkLabel(self.settings, text="Enter your API SECRET")
        self.settings_apikey_label.grid(row=3, column=0, padx=20, pady=10)
        self.settings_apikey = ctk.CTkEntry(self.settings, textvariable=self.apisecret, placeholder_text="Enter your api secret...")
        self.settings_apikey.grid(row=3, column=1, padx=50, pady=20)
        
        self.settings_save = ctk.CTkButton(self.settings, text="Save", command=lambda: self.create_settings(),  compound="top")
        self.settings_save.grid(row=4, column=0, padx=50, pady=20)
        self.settings_apikey_label = ctk.CTkLabel(self.settings, textvariable = self.settings_status)
        self.settings_apikey_label.grid(row=4, column=1, padx=20, pady=10)
        self.settings_save = ctk.CTkButton(self.settings, text="Save", command=lambda: self.create_settings(),  compound="top")
        self.settings_experimental_label = ctk.CTkLabel(self.settings, text = "EXPERIMENTAL FEATURES")
        self.settings_experimental_label.grid(row=5, column=0, padx=50, pady=20)
        self.allpairs_checkbox = ctk.CTkCheckBox(self.settings, text="SHOW ALL TRADING PAIRS",
                                     variable=self.experimental, onvalue="on", offvalue="off")
        self.allpairs_checkbox.grid(row=5, column=1, padx=50, pady=20)
        
        self.select_frame_by_name("dashboard")
        
    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def change_exchange(self, new):
        self.exchange_selected.set(new)
        self.settings_exchange_binance.configure(fg_color=["#3a7ebf", "#1f538d"] if self.exchange_selected.get() == "Binance" else "transparent")
        self.settings_exchange_bybit.configure(fg_color=["#3a7ebf", "#1f538d"] if self.exchange_selected.get() == "ByBit" else "transparent")
        
        
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.dashboard_button.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.balances_button.configure(fg_color=("gray75", "gray25") if name == "balances" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # show selected frame
        if name == "dashboard":
            self.dashboard.grid(row=0, column=1, sticky="nsew")
        else:
            self.dashboard.grid_forget()
        if name == "balances":
            self.balances.grid(row=0, column=1, sticky="nsew")
        else:
            self.balances.grid_forget()
        if name == "settings":
            self.settings.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings.grid_forget()    
        
    def dashboard_button_event(self):
        self.select_frame_by_name("dashboard")

    def balances_button_event(self):
        self.select_frame_by_name("balances")

    def settings_button_event(self):
        self.select_frame_by_name("settings")
        
    def load_config(self):
        with open("config.json", "r") as jsonfile:
            data = json.load(jsonfile)
            print(data)
        self.exchange_selected.set(data['exchange_selected'])
        self.apikey.set(data['apikey'])
        self.apisecret.set(data['apisecret'])
         
    def create_settings(self):
        try:
            settings = {
                "exchange_selected" : self.exchange_selected.get(),
                "apikey" : self.apikey.get(),
                "apisecret" : self.apisecret.get()
                }

            with open("config.json", "w") as jsonfile:
                json.dump(settings, jsonfile)
            
            self.settings_status.set("Successfuly saved.")
        except:
            self.settings_status.set("There was an error.")
            
    def pulldata(self, symbol="BTCUSDT"):
        try:
            plt.cla()
            print("yes")
        except:
            print("no")
        data = GetHistoricalData(symbol, self.apikey.get(), self.apisecret.get())
        self.lastprice.set(str(data['close'].iloc[-1])+"$")
        self.change.set(str(round(((data['close'].iloc[0] - data['close'].iloc[-1])/data['close'].iloc[0])*100, 3))+"%")
        self.volume.set(str(data['volume'].sum()*data['close'].iloc[-1])+"$")
        self.trades.set(str(data['numberOfTrades'].sum()))

           # open figure + axis
        # plot data
        self.ax.plot(data.index, data['close'])
        # rotate x-tick-labels by 90°
        self.ax.tick_params(axis='x',rotation=90)
        self.ax.set_xticks([data.index[0], data.index[int(len(data.index)/2)], data.index[-1]], ["-24h", "-12h", "now"])
        self.canvas = FigureCanvasTkAgg(self.fig, self.dashboard)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=5, column=0, padx=20, pady=10, columnspan=5)
        
        self.after(600,self.pulldata)
        
    def addbalances(self):
        data = getAccountInfos(self.apikey.get(), self.apisecret.get())
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "imgs")
        print(data)
        for i in range(len(data)):  # add items with images
            try:
                logo_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, data['asset'].iloc[i]+".png")), size=(20, 20))
            except:
                logo_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "btc.png")), size=(20, 20))
            
            data['asset'].iloc[i]
            img = ctk.CTkLabel(self.my_frame, text="", image=logo_image)
            img.grid(row=i+1, column=0, padx=20, pady=10)
                
            x = ctk.CTkLabel(self.my_frame, text=data['asset'].iloc[i])
            x.grid(row=i+1, column=1, padx=20, pady=10)
            y = ctk.CTkLabel(self.my_frame, text=data['free'].iloc[i])
            y.grid(row=i+1, column=2, padx=20, pady=10)
            price = getAvgPrice(data['asset'].iloc[i])
            z = ctk.CTkLabel(self.my_frame, text=str(price)+"$ / " +data['asset'].iloc[i])
            z.grid(row=i+1, column=3, padx=20, pady=10)
            xyz = ctk.CTkLabel(self.my_frame, text=str(price*data['free'].iloc[i])+"$")
            xyz.grid(row=i+1, column=4, padx=20, pady=10)
        self.after(600000,self.addbalances)
        
    def refresh(self):
        self.destroy()
        self.__init__()
            
            
        
if __name__ == "__main__":
    app = App()
    app.mainloop()