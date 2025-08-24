from app.services.backups import backup_now

if __name__ == "__main__":
    path = backup_now()
    print(path)
