import pandas as pd

def process_excel_file(file_path):
    """
    Read an Excel file and extract questions.
    
    Parameters:
        file_path: Path to the Excel file
    
    Returns:
        List of question texts (strings)
    """
    # Read the Excel file
    excel_data = pd.read_excel(file_path)
    
    # Get the first column (where questions are)
    first_column = excel_data.columns[0]
    
    # Extract questions
    questions_list = []


    
    for row_index, row_data in excel_data.iterrows():
        # Get the question text
        question_text = str(row_data[first_column])
        question_text = question_text.strip()  # Remove extra spaces
        
        # Skip empty rows
        is_empty = pd.isna(row_data[first_column])
        if is_empty or question_text == '' or question_text == 'nan':
            continue
        

        # Add to list
        questions_list.append(question_text)
    
    return questions_list


def check_if_excel_file(filename):
    """
    Check if a file is an Excel file (.xlsx or .xls).
    
    Parameters:
        filename: Name of the file
    
    Returns:
        True if Excel file, False otherwise
    """
    # Check if filename has a dot
    if '.' not in filename:
        return False
    
    # Get the file extension
    file_extension = filename.rsplit('.', 1)[1].lower()
    
    # Check if it's xlsx or xls
    if file_extension in {'xlsx', 'xls'}:
        return True
    else:
        return False