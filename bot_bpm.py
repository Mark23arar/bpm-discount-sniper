import requests
from bs4 import BeautifulSoup
import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

client = discord.Client()

def get_discounted_products():
    url = "https://www.bpmpower.com/it/prodotti/offerte"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for item in soup.select(".product-item"):
        try:
            title = item.select_one(".product-title").text.strip()

            old_price_tag = item.select_one(".old-price")
            new_price_tag = item.select_one(".special-price")

            if not old_price_tag or not new_price_tag:
                continue # salta se manca uno dei prezzi

            old_price = float(old_price_tag.text.replace("€", "").replace(",", ".").strip())
            new_price = float(new_price_tag.text.replace("€", "").replace(",", ".").strip())

            discount = round((old_price - new_price) / old_price * 100)

            if discount >= 20:
                relative_link = item.select_one("a")["href"]
                full_link = f"https://www.bpmpower.com{relative_link}"
                products.append({
                    "title": title,
                    "old_price": old_price,
                    "new_price": new_price,
                    "discount": discount,
                    "link": full_link
                })
        except Exception as e:
            print(f"Errore parsing prodotto: {e}")
            continue

    return products

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    products = get_discounted_products()

    if not products:
        await channel.send("🚫 Nessun prodotto scontato del 20% o più al momento.")
    else:
        for p in products[:5]: # Limita a 5 prodotti per messaggio
            msg = (
                f"🔎 **{p['title']}**\n"
                f"💰 Prezzo originale: €{p['old_price']:.2f}\n"
                f"🔥 Prezzo scontato: €{p['new_price']:.2f} (-{p['discount']}%)\n"
                f"🔗 [Vai al prodotto]({p['link']})"
            )
            await channel.send(msg)

    await client.close()

client.run(TOKEN)

