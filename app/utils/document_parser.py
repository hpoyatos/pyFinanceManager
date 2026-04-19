import io
import re
from pypdf import PdfReader

def identify_document(file_content, filename):
    filename_lower = filename.lower()
    
    # Padroes iniciais
    tipo = 'Documento'
    icone = 'fa-file'
    
    # Se for XML
    if filename_lower.endswith('.xml'):
        content_str = ""
        try:
            content_str = file_content.decode('utf-8', errors='ignore').lower()
        except:
            pass
            
        if 'nfeproc' in content_str or 'infnfe' in content_str:
            tipo = 'Nota Fiscal (XML)'
            icone = 'fa-file-code'
        else:
            tipo = 'Arquivo XML'
            icone = 'fa-code'
        return tipo, icone

    # Se for PDF
    if filename_lower.endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(file_content))
            # Le apenas o texto da primeira pagina para performance
            first_page_text = reader.pages[0].extract_text().lower()
            
            if 'danfe' in first_page_text or 'nota fiscal' in first_page_text:
                tipo = 'Nota Fiscal (PDF)'
                icone = 'fa-file-invoice'
            elif 'energia' in first_page_text or 'cpfl' in first_page_text or 'elektro' in first_page_text or 'enel' in first_page_text:
                tipo = 'Conta de Luz'
                icone = 'fa-bolt'
            elif 'água' in first_page_text or 'sabesp' in first_page_text or 'sanasa' in first_page_text:
                tipo = 'Conta de Água'
                icone = 'fa-faucet-drip'
            elif 'internet' in first_page_text or 'vivo' in first_page_text or 'claro' in first_page_text or 'net virtual' in first_page_text:
                tipo = 'Conta de Internet/TV'
                icone = 'fa-wifi'
            elif 'boleto' in first_page_text or 'pagável em' in first_page_text:
                tipo = 'Boleto Bancário'
                icone = 'fa-barcode'
            else:
                tipo = 'Documento PDF'
                icone = 'fa-file-pdf'
        except Exception as e:
            tipo = 'Documento PDF'
            icone = 'fa-file-pdf'
        return tipo, icone

    # Imagens
    if filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        tipo = 'Imagem/Recibo'
        icone = 'fa-file-image'
        return tipo, icone
        
    return tipo, icone
