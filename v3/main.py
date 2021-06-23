from downloaders.sap_downloader import SapDownloader
from uploaders.sap_uploader import SapUploader


def main():
    main_download()
    #main_upload()


def main_upload():
    uploader = SapUploader('c:/data/powertracks-v3')
    uploader.start()


def main_download():
    base_url = 'https://www.sapsailing.com/sailingserver/api/v1'
    target_path = 'c:/data/powertracks-v3'
    downloader = SapDownloader(base_url, target_path)
    downloader.start()


if __name__ == "__main__":
    main()
