import discord
import database
import welcome as welc


@discord.app_commands.command(name="test", description="Tests things.")
async def co_test(interaction: discord.Interaction):
    await interaction.response.send_message(
        content="Test!"
    )


@discord.app_commands.command(name="sql", description="Submits a raw SQL query and returns the results.")
@discord.app_commands.describe(query="Your raw SQL query.")
async def co_sql(interaction: discord.Interaction, query: str):
    print("Processing query...")
    await interaction.response.send_message(database.raw_query(query))


@discord.app_commands.command(name="welcome", description="Generates a welcome embed.")
async def co_welcome(interaction: discord.Interaction):
    await interaction.response.send_message(
        embeds=[welc.get_welcome_embed(interaction.user, "Test introduction!")]
    )


@discord.app_commands.command(name="modal", description="Supplies a modal to the user.")
async def co_modal(interaction: discord.Interaction):
    await interaction.response.send_message(
        content="Not ready yet!"
    )


@discord.app_commands.command(name="dbupdate", description="DB update!")
async def co_dbupdate(interaction: discord.Interaction):
    print("DB update!")
    # member_iter = interaction.guild.fetch_members()
    await interaction.response.defer(ephemeral=True, thinking=True)
    discord_members = interaction.guild.members
    print(len(discord_members))
    rows = 0
    async for user in interaction.guild.fetch_members():
        userdata = database.identify_user(user.id)
        if user.bot:
            continue
        if userdata is None:
            # The user is not in the database.
            query = f"INSERT INTO users (user_id, username) VALUES ({user.id}, \"{user.name}#{user.discriminator}\")"

        else:
            query = f"UPDATE users SET user_id = {user.id}, username = \"{user.name}#{user.discriminator}\" " \
                    f"WHERE user_id = {user.id}"
        database.raw_query(query)
        rows += 1
    await interaction.followup.send(
        content=f"Done - {rows} rows affected."
    )


@discord.app_commands.context_menu(name="Identify")
async def ca_user_identify(interaction: discord.Interaction, user: discord.Member):
    user_data = database.identify_user(user.id)
    """
        user_data now contains a 5-tuple with the following values:
        - User ID
        - User full name
        - User grad year
        - User email stub
        - Username#Discriminator
    """
    data_embed = discord.Embed()
    data_embed.set_author(name="User Information")
    data_embed.title = f"{user.name}#{user.discriminator}"

    if user_data is None or len(user_data) == 0:
        data_embed.description = "No information available on this user!\n Please let the E-Board know!"
    else:
        data_embed.add_field(name="Name", value=user_data[1])
        data_embed.add_field(name="Class", value=user_data[2])
        data_embed.add_field(name="Email", value=user_data[3] + "@g.holycross.edu", inline=False)

    data_embed.set_thumbnail(url=user.avatar.url)
    data_embed.colour = 16777215

    await interaction.response.send_message(
        ephemeral=True,
        embeds=[data_embed]
    )


@discord.app_commands.context_menu(name="Thumbs")
async def ca_message_thumbs(interaction: discord.Interaction, message: discord.Message):
    await message.add_reaction("👍")
    await interaction.response.send_message(
        ephemeral=True,
        content="Done!"
    )
