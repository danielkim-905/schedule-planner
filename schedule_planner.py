import pandas as pd
import fitz  # PyMuPDF
import re
from dateutil import parser
import os

def get_user_tasks():
    """
    Collects manual task inputs from the user via command line.
    Returns a pandas DataFrame with task information.
    """
    tasks = []
    print("\nEnter your tasks one by one. Type 'done' when finished.")
    
    while True:
        task_name = input("Task name (or 'done'): ").strip()
        if task_name.lower() == "done":
            break
            
        day = input("Day of the week (e.g., Monday): ").strip().capitalize()
        start_time = input("Start time (HH:MM, 24hr format): ").strip()
        end_time = input("End time (HH:MM, 24hr format): ").strip()
        description = input("Optional description: ").strip()

        tasks.append({
            "Task": task_name,
            "Day": day,
            "Start Time": start_time,
            "End Time": end_time,
            "Description": description
        })
    
    return pd.DataFrame(tasks)

def extract_dates_from_pdf(pdf_path):
    """
    Extracts dates from a PDF syllabus file.
    Returns a list of parsed date objects.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        # Look for any month-day patterns
        date_matches = re.findall(
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
            r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2}(?:,\s+\d{4})?',
            text, re.IGNORECASE
        )

        parsed_dates = []
        for date_str in date_matches:
            try:
                parsed_date = parser.parse(date_str)
                parsed_dates.append(parsed_date.date())
            except:
                continue

        return parsed_dates
    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

def display_schedule(schedule_df):
    """
    Display the schedule in a formatted way.
    """
    if schedule_df.empty:
        print("No schedule items to display.")
        return
    
    print("\n" + "="*80)
    print("                        FULL SCHEDULE")
    print("="*80)
    
    # Group by day for better organization
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days_order:
        day_tasks = schedule_df[schedule_df['Day'] == day]
        if not day_tasks.empty:
            print(f"\n📅 {day.upper()}")
            print("-" * 40)
            for _, task in day_tasks.iterrows():
                time_str = f"{task['Start Time']} - {task['End Time']}" if task['Start Time'] != 'N/A' else "All Day"
                print(f"  {time_str:<15} | {task['Task']}")
                if task['Description']:
                    print(f"  {'':<15} | Description: {task['Description']}")
            print()

def save_schedule_to_csv(schedule_df, filename="my_schedule.csv"):
    """
    Save the schedule to a CSV file.
    """
    try:
        schedule_df.to_csv(filename, index=False)
        print(f"\n✅ Schedule saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving schedule: {e}")

def main():
    """
    Main function that orchestrates the schedule planning process.
    """
    print("🗓️  Welcome to the Schedule Planner!")
    print("This tool helps you combine manual tasks with syllabus events.")
    
    # Step 1: Get user tasks
    print("\n" + "="*50)
    print("STEP 1: Manual Task Input")
    print("="*50)
    task_df = get_user_tasks()
    
    if not task_df.empty:
        print("\n✅ Your Manual Tasks:")
        print(task_df.to_string(index=False))
    else:
        print("\n📝 No manual tasks entered.")
    
    # Step 2: Get syllabus dates
    print("\n" + "="*50)
    print("STEP 2: Syllabus PDF Processing")
    print("="*50)
    
    syllabus_df = pd.DataFrame()
    process_syllabus = input("Do you want to process a syllabus PDF? (y/n): ").strip().lower()
    
    if process_syllabus == 'y':
        while True:
            syllabus_path = input("Enter the filename of your syllabus PDF: ").strip()
            
            if not os.path.exists(syllabus_path):
                print(f"❌ File '{syllabus_path}' not found. Please check the path and try again.")
                continue
            
            print(f"📄 Processing {syllabus_path}...")
            dates = extract_dates_from_pdf(syllabus_path)
            
            if dates:
                print(f"\n✅ Found {len(dates)} dates in the syllabus:")
                for i, d in enumerate(dates, 1):
                    print(f"  {i}. {d.strftime('%A, %B %d, %Y')}")
                
                syllabus_df = pd.DataFrame({
                    "Task": ["Syllabus Event"] * len(dates),
                    "Day": [d.strftime('%A') for d in dates],
                    "Start Time": ["N/A"] * len(dates),
                    "End Time": ["N/A"] * len(dates),
                    "Description": [d.strftime('%B %d, %Y') for d in dates]
                })
                break
            else:
                print("❌ No dates found in the PDF. Please check the file or try a different one.")
                retry = input("Try another file? (y/n): ").strip().lower()
                if retry != 'y':
                    break
    
    # Step 3: Combine and display
    print("\n" + "="*50)
    print("STEP 3: Combined Schedule")
    print("="*50)
    
    # Combine the dataframes
    if not task_df.empty and not syllabus_df.empty:
        full_schedule = pd.concat([task_df, syllabus_df], ignore_index=True)
    elif not task_df.empty:
        full_schedule = task_df
    elif not syllabus_df.empty:
        full_schedule = syllabus_df
    else:
        full_schedule = pd.DataFrame()
    
    if not full_schedule.empty:
        display_schedule(full_schedule)
        
        # Option to save
        save_option = input("Would you like to save this schedule to a CSV file? (y/n): ").strip().lower()
        if save_option == 'y':
            filename = input("Enter filename (press Enter for 'my_schedule.csv'): ").strip()
            if not filename:
                filename = "my_schedule.csv"
            if not filename.endswith('.csv'):
                filename += '.csv'
            save_schedule_to_csv(full_schedule, filename)
    else:
        print("📭 No schedule items to display.")
    
    print("\n🎉 Thanks for using the Schedule Planner!")

if __name__ == "__main__":
    main()
