from users_profiles import UsersProfiles

bot = UsersProfiles(port=58356)
bot.group_id = "4e784292-6a65-471e-9f80-e91202e3358c"

# give the file path or None to init it.
bot.update(users_profiles_file=None)
