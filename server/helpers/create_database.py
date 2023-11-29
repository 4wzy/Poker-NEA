from server.helpers.database_interaction import DatabaseInteraction


def main():
    db_interaction = DatabaseInteraction()
    db_interaction.create_database_and_tables()


if __name__ == "__main__":
    main()
