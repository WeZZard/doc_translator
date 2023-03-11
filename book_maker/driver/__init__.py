from book_maker.driver.epub_driver import EPUBBookDriver
from book_maker.driver.txt_loader import TXTDriver

DRIVER_TYPE_FOR_FILE_EXTENSION = {
    ".epub": EPUBBookDriver,
    ".txt": TXTDriver,
}
