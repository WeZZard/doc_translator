from book_maker.driver.epub_driver import EPUBBookDriver
from book_maker.driver.txt_loader import TXTDriver
from book_maker.driver.simple_md_loader import SimpleMDDriver

DRIVER_TYPE_FOR_FILE_EXTENSION = {
    ".epub": EPUBBookDriver,
    ".txt": TXTDriver,
    ".md": SimpleMDDriver,
}
