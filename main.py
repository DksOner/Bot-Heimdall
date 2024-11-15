import discord
import requests
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv() # Cargar variables de entorno desde .env

# Token bot Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") # Obtener el token desde el .env
# ID del canal de discord que recibira las notificaciones
CHANNEL_ID = os.getenv("CHANNEL_ID")

# URL de la pagina a monitorear
URL = "https://monoschinos2.com/"

# Lista de animes a monitorear
animes_de_interes = [
   {"nombre": "Dandadan", "ultimo_capitulo": None},
   {"nombre": "Blue Lock vs. U-20 Japan", "ultimo_capitulo": None},
   {"nombre": "Danmachi 5", "ultimo_capitulo": None},
   {"nombre": "Kami no Tou: Ouji no Kikan", "ultimo_capitulo": None},
   {"nombre": "Arcane S2 Doblaje Japonés", "ultimo_capitulo": None}
]

client = discord.Client(intents=discord.Intents.default())

# Funcion para Scraping
def check_para_nuevo_cap():
   response = requests.get(URL)
   soup = BeautifulSoup(response.text, 'html.parser')

   # Busca la lista de capitulos recientes
   nuevos_capitulos = []

   # Selecciona todos los <li> que contengan capitulos recientes
   for item in soup.find_all("li", class_="col mb-4"):
      articulo = item.find("article")
      if articulo:
         link = articulo.find("a")
         if link:
            capitulo_link = link.get("href")
            h2 = item.find("h2")
            if h2:
               anime_nombre = h2.text.strip()  # Nombre del anime

               # Buscar el numero del capitulo
               div = link.find("div")
               if div:
                  capitulo_span = div.find("span")
                  if capitulo_span:
                     capitulo = capitulo_span.text.strip() # Numero del capitulo

                     # Comprobar si el anime esta en la lista de interes
                     for anime in animes_de_interes:
                        if anime_nombre == anime["nombre"]:
                           # Verificar si el capitulo es nuevo
                           if capitulo != anime ["ultimo_capitulo"]:
                              anime["ultimo_capitulo"] = capitulo
                              nuevos_capitulos.append(f"¡Nuevo capitulo de {anime_nombre}!: {capitulo} - {capitulo_link}")
   return nuevos_capitulos



# Enviar mensaje a Discord
async def notify_discord():
   nuevos_capitulos = check_para_nuevo_cap()
   if nuevos_capitulos:
      canal = client.get_channel(CHANNEL_ID)
      for mensaje in nuevos_capitulos:
         await canal.send(mensaje)

# Programacion para revisar la pagina cada cierto tiempo
async def scheduled_task():
   while True:
      await notify_discord()
      await asyncio.sleep(1800)

@client.event
async def on_ready():
   print(f'Bot conectado como {client.user}')
   client.loop.create_task(scheduled_task())

client.run(DISCORD_TOKEN)