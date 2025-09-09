import re
from bs4 import BeautifulSoup

def format_currency(value):
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value}"

with open("piratehq/quiverquant.html", "r") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "lxml")
script_tag = soup.find("script", string=re.compile("let tradeData"))

if script_tag:
    script_content = script_tag.string
    net_worth_match = re.search(r'let netWorthEstimate = "(\d+\.?\d*)";', script_content)
    trade_volume_match = re.search(r"let tradeVolTotal = (\d+\.?\d*);", script_content)
    trade_data_match = re.search(r"let tradeData = (\[.*\]);", script_content, re.DOTALL)

    net_worth = float(net_worth_match.group(1)) if net_worth_match else 0
    trade_volume = float(trade_volume_match.group(1)) if trade_volume_match else 0

    if trade_data_match:
        trade_data_str = trade_data_match.group(1)
        # Correctly count the trades by counting the opening brackets of the trade objects
        total_trades = trade_data_str.count('[') -1
    else:
        total_trades = 0

    with open("piratehq/index.html", "r") as f:
        pirate_html = f.read()

    pirate_soup = BeautifulSoup(pirate_html, "lxml")

    pirate_soup.find(id="net-worth").string = format_currency(net_worth)
    pirate_soup.find(id="trade-volume").string = format_currency(trade_volume)
    pirate_soup.find(id="total-trades").string = str(total_trades)

    with open("piratehq/index.html", "w") as f:
        f.write(str(pirate_soup))

    print("Metrics updated successfully!")
else:
    print("Could not find the script tag with trade data.")
