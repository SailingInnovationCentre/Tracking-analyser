from downloaders.sap_downloader import SapDownloader


def main():
    main_download()


def main_download():
    base_url = 'https://www.sapsailing.com/sailingserver/api/v1'
    target_path = 'c:/data/powertracks/auto_download'
    downloader = SapDownloader(base_url, target_path)
    downloader.start()


if __name__ == "__main__":
    main()
