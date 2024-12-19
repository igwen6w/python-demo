import fitz
import os
from datetime import datetime

def remove_footer_images(pdf_path, output_path, footer_height=50, new_url=None, first_page_pdf_path=None):
    # 打开 PDF 文件
    document = fitz.open(pdf_path)
    
    # 遍历所有页面
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        image_list = page.get_images(full=True)
        
        # 获取页面尺寸
        page_height = page.rect.height

        # 获取页面中的所有链接
        links = page.get_links()
        
        # 遍历所有图片
        for img_index, img in enumerate(image_list):
            xref = img[0]
            img_rect = page.get_image_rects(xref)
            
            # 检查图片位置是否在页脚区域
            if img_rect and img_rect[0].y1 > page_height - footer_height:
                page.delete_image(xref)
                print(f"Removed image {xref} from page {page_num + 1}")
        
        # 遍历所有链接
        for link in links:
            # 如果提供了新的 URL，将链接替换为新 URL
            if new_url:
                print(f"Update link {link}")
                link['uri'] = new_url
                page.update_link(link)
            # 否则，移除链接
            else:
                page.delete_link(link)

    # 设置新的封面
    if first_page_pdf_path:
        new_document = fitz.open(first_page_pdf_path)

        # 获取新的封面
        new_page = new_document.load_page(0)

        new_page_rect = new_page.rect
        document.insert_page(0, width=new_page_rect.width, height=new_page_rect.height)
    
        # 删除旧的第一页（注意删除的是插入后的第二页）
        document.delete_page(1)
    
        # 获取插入的新空白页面
        page = document.load_page(0)
    
        # 将新页面的内容复制到插入的新空白页面
        page.show_pdf_page(new_page_rect, new_document, 0)

    # 创建临时输出目录
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # 保存修改后的 PDF 文件
    document.save(temp_dir + "/" + output_path)

# 示例使用
input_pdf = "example_pdf/input.pdf"
new_pdf = "example_pdf/new.pdf"
output_pdf = f"modified_example-{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
remove_footer_images(input_pdf, output_pdf, 100, "https://lwsite.com", "new.pdf")