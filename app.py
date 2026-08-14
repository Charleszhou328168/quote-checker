import streamlit as st
import pandas as pd
import pypdf
import re

st.set_page_config(page_title="印厂报价单自动比对工具", layout="wide")

st.title("📄 印厂报价单自动比对工具")
st.write("请分别上传 **Excel 需求基准单** 与 **印厂 PDF 报价单**，系统将自动解析并比对关键字段。")

col1, col2 = st.columns(2)

with col1:
    excel_file = st.file_uploader("1. 上传 Excel 基准单 (Requests_Printer)", type=["xlsx", "xls"])

with col2:
    pdf_file = st.file_uploader("2. 上传 PDF 报价单 (Offer Sheet)", type=["pdf"])

def extract_pdf_text(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if excel_file and pdf_file:
    st.success("文件上传成功，正在比对中...")
    
    # 读取 Excel
    df_excel = pd.read_excel(excel_file)
    
    # 读取 PDF
    pdf_text = extract_pdf_text(pdf_file)
    
    st.subheader("🔍 比对结果明细")
    
    # 解析 Excel 并展示
    comparison_data = []
    
    for idx, row in df_excel.iterrows():
        kba = str(row.get('Article No. / \nKBA', ''))
        product_name = str(row.get('Design description / Article name', ''))
        dieline = str(row.get('Die line number', ''))
        size = str(row.get('Dimensions \n(L x W or L x W x H) in mm', ''))
        color = str(row.get('Colour', ''))
        qty = str(row.get('Quantity / \npieces', ''))
        
        # 简单在 PDF 中匹配关键词
        dieline_found = dieline in pdf_text if dieline and str(dieline) != 'nan' else False
        size_found = size in pdf_text if size and str(size) != 'nan' else False
        
        comparison_data.append({
            "KBA/编号": kba,
            "产品名称": product_name,
            "Excel 刀版号": dieline,
            "PDF 匹配刀版号": "✅ 找到" if dieline_found else "❌ 未找到",
            "Excel 尺寸": size,
            "PDF 匹配尺寸": "✅ 找到" if size_found else "❌ 未找到",
            "Excel 颜色": color,
            "需求数量": qty
        })
        
    result_df = pd.DataFrame(comparison_data)
    st.dataframe(result_df, use_container_width=True)
    
    with st.expander("📄 查看 PDF 提取的完整文本"):
        st.text(pdf_text)
