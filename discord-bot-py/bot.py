import discord
import requests
from PIL import Image
import os
from io import BytesIO
import openai
import json

# Recover configurations from a config.json placed next to the script
# Check if config.json exists
if not os.path.exists("config.json"):
    # Ask user for Discord token and OpenAI API key
    print("config.json file not found.")
    discord_token = input("Enter Discord bot token: ")
    openai_key = input("Enter OpenAI API key: ")
    
    # Create config.json file with user input
    with open("config.json", "w") as f:
        json.dump({"discord_token": discord_token, "openai_key": openai_key}, f)
else:
    # Load Discord token and OpenAI API key from config.json file
    with open("config.json") as f:
        config = json.load(f)
        discord_token = config["discord_token"]
        openai_key = config["openai_key"]

# Set OpenAI API key
openai.api_key = openai_key

# Function to generate image using OpenAI API
async def generate_image(prompt):
    # Set parameters for image generation
    image_size = 512

    # Generate image using OpenAI API
    response = openai.Image.create(
        prompt=prompt,
    )

    # Get image URL from response
    image_url = response.data[0].url.strip()

    # Download image
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))

    # Resize image
    image = image.resize((image_size, image_size))

    # Create folder if it doesn't exist
    if not os.path.exists("gen_imgs"):
        os.mkdir("gen_imgs")

    # Save image to disk with prompt as filename
    filename = os.path.join("gen_imgs", f"{prompt}.png")
    image.save(filename)

    # Convert image to bytes
    buffer = BytesIO()
    image.save(buffer, "png")
    buffer.seek(0)
    return buffer


# Create new discord bot client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Function to handle message events
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Generate image based on message content
    prompt = message.content
    image = await generate_image(prompt)

    # Post image to Discord channel
    await message.channel.send(file=discord.File(image, "image.png"))

# Run the bot
client.run(discord_token)
