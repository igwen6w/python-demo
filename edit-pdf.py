import fitz
import os
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

@dataclass
class PDFConfig:
    footer_height: int = 50
    new_url: Optional[str] = None
    first_page_pdf_path: Optional[str] = None
    temp_dir: str = "temp"

class PDFProcessor:
    def __init__(self, config: PDFConfig):
        self.config = config
        self._setup_logging()
        self._setup_temp_dir()
    
    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_temp_dir(self) -> None:
        if not os.path.exists(self.config.temp_dir):
            os.makedirs(self.config.temp_dir)
            self.logger.info(f"Created temporary directory: {self.config.temp_dir}")

    def process_pdf(self, input_path: str, output_path: str) -> None:
        try:
            document = fitz.open(input_path)
            self._process_pages(document)
            
            if self.config.first_page_pdf_path:
                self._replace_first_page(document)
            
            self._save_document(document, output_path)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise
        finally:
            if 'document' in locals():
                document.close()

    def _process_pages(self, document: fitz.Document) -> None:
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            self._remove_footer_images(page, page_num)
            self._process_links(page, page_num)

    def _remove_footer_images(self, page: fitz.Page, page_num: int) -> None:
        page_height = page.rect.height
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            img_rect = page.get_image_rects(xref)
            
            if img_rect and img_rect[0].y1 > page_height - self.config.footer_height:
                page.delete_image(xref)
                self.logger.info(f"Removed image {xref} from page {page_num + 1}")

    def _process_links(self, page: fitz.Page, page_num: int) -> None:
        links = page.get_links()
        
        for link in links:
            if self.config.new_url:
                self._update_link(page, link)
            else:
                page.delete_link(link)
                self.logger.info(f"Deleted link on page {page_num + 1}")

    def _update_link(self, page: fitz.Page, link: dict) -> None:
        old_url = link.get('uri', '')
        link['uri'] = self.config.new_url
        page.update_link(link)
        self.logger.info(f"Updated link from {old_url} to {self.config.new_url}")

    def _replace_first_page(self, document: fitz.Document) -> None:
        try:
            new_document = fitz.open(self.config.first_page_pdf_path)
            new_page = new_document.load_page(0)
            new_page_rect = new_page.rect
            
            document.insert_page(0, width=new_page_rect.width, height=new_page_rect.height)
            document.delete_page(1)
            
            page = document.load_page(0)
            page.show_pdf_page(new_page_rect, new_document, 0)
            
            self.logger.info("Successfully replaced first page")
        except Exception as e:
            self.logger.error(f"Error replacing first page: {str(e)}")
            raise
        finally:
            if 'new_document' in locals():
                new_document.close()

    def _save_document(self, document: fitz.Document, output_path: str) -> None:
        output_file = os.path.join(self.config.temp_dir, output_path)
        document.save(output_file)
        self.logger.info(f"Saved modified PDF to {output_file}")

def main():
    # 配置参数
    config = PDFConfig(
        footer_height=100,
        new_url="https://lwsite.com",
        first_page_pdf_path="example_pdf/new.pdf"
    )

    # 输入输出路径
    input_pdf = "example_pdf/input.pdf"
    output_pdf = f"modified_example-{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # 处理 PDF
    processor = PDFProcessor(config)
    processor.process_pdf(input_pdf, output_pdf)

if __name__ == "__main__":
    main()