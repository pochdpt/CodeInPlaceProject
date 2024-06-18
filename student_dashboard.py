import csv
from datetime import datetime
import pandas as pd
import streamlit as st

def read_csv_to_dict(file_path):
    student_dict = {}
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        sorted_data = sorted(csv_reader, key=lambda row: datetime.strptime(row[5], '%m/%d/%y'))

    for row in sorted_data:
        name = row[0]
        digital_score = int(row[1])
        verbal_score = int(row[2])
        math_score = int(row[3])
        test_number = int(row[4])
        test_date = row[5]
        verbal_tutor = row[6]
        math_tutor = row[7]
        counselor = row[8]

        if name not in student_dict:
            student_dict[name] = {
                'tests': [],
                'predicted_score_range': None,
                'score_improvement': None,
                'verbal_tutor': verbal_tutor,
                'math_tutor': math_tutor,
                'counselor': counselor
            }

        student_dict[name]['tests'].append({
            'digital_score': digital_score,
            'verbal_score': verbal_score,
            'math_score': math_score,
            'test_number': test_number,
            'test_date': test_date
        })
    
    return student_dict, sorted_data[-1][5]

def calculate_max_score(student_data):
    max_scores = {}
    for student, data in student_data.items():
        tests = data['tests']
        max_score = max(tests, key=lambda x: x['digital_score'])['digital_score']
        max_scores[student] = max_score
    return max_scores

def calculate_average_score(student_data):
    total_score = 0
    total_tests = 0
    for data in student_data.values():
        for test in data['tests']:
            total_score += test['digital_score']
            total_tests += 1
    return total_score / total_tests if total_tests > 0 else 0

def calculate_score_improvement(student_data):
    score_improvement = {}
    for student, data in student_data.items():
        tests = data['tests']
        if tests:
            first_score = tests[0]['digital_score']
            max_score = max(tests, key=lambda x: x['digital_score'])['digital_score']
            improvement = max_score - first_score
            score_improvement[student] = improvement
    return score_improvement

def add_calculated_values(student_data, max_scores, average_score, score_improvements):
    for student, data in student_data.items():
        max_score = max_scores[student]
        score_improvement = score_improvements[student]
        predicted_score_range = (average_score, max_score)
        
        data['predicted_score_range'] = predicted_score_range
        data['score_improvement'] = score_improvement

def create_performance_dict(student_data, average_score, last_date):
    performance_dict = {
        'average_score': average_score,
        'last_test_date': last_date,
        'scores_by_year': {}
    }

    for student, data in student_data.items():
        for test in data['tests']:
            year = datetime.strptime(test['test_date'], '%m/%d/%y').year
            if year not in performance_dict['scores_by_year']:
                performance_dict['scores_by_year'][year] = []

            performance_dict['scores_by_year'][year].append(test['digital_score'])

    for year, scores in performance_dict['scores_by_year'].items():
        performance_dict['scores_by_year'][year] = sum(scores) / len(scores) if scores else 0

    return performance_dict

def display_student_results(student_data, student_name):
    if student_name not in student_data:
        st.write(f"No data available for student: {student_name}")
        return

    student_tests = student_data[student_name]['tests']
    student_tests_sorted = sorted(student_tests, key=lambda x: datetime.strptime(x['test_date'], '%m/%d/%y'))

    st.write(f"Results for {student_name}:")

    df = pd.DataFrame(student_tests_sorted)
    st.dataframe(df)

    total_score = sum(test['digital_score'] for test in student_tests_sorted)
    average_score = total_score / len(student_tests_sorted) if student_tests_sorted else 0
    predicted_score_range = student_data[student_name]['predicted_score_range']

    st.write(f"**Average Digital Score:** {average_score:.2f}")
    st.write(f"**Predicted Score Range:** {predicted_score_range}")

def generate_alerts(student_data):
    verbal_tutor_alerts = []
    math_tutor_alerts = []
    counselor_alerts = []

    for student, data in student_data.items():
        tests = data['tests']
        if len(tests) < 2:
            continue
        
        first_score = tests[0]['digital_score']
        last_score = tests[-1]['digital_score']
        if last_score < first_score:
            if data['verbal_tutor']:
                verbal_tutor_alerts.append((student, data['verbal_tutor']))
            if data['math_tutor']:
                math_tutor_alerts.append((student, data['math_tutor']))
            if data['counselor']:
                counselor_alerts.append((student, data['counselor']))
        else:
            score_improvement = last_score - first_score
            if score_improvement < 10:
                if data['verbal_tutor']:
                    verbal_tutor_alerts.append((student, data['verbal_tutor']))
                if data['math_tutor']:
                    math_tutor_alerts.append((student, data['math_tutor']))
                if data['counselor']:
                    counselor_alerts.append((student, data['counselor']))

    return verbal_tutor_alerts, math_tutor_alerts, counselor_alerts

def list_student_names(student_data):
    return list(student_data.keys())

# Streamlit app
st.title("Student Performance Dashboard")

file_path = '/Users/danielpozuelo/desktop/CID/Tests.csv'

student_scores, last_test_date = read_csv_to_dict(file_path)

max_scores = calculate_max_score(student_scores)
average_score = calculate_average_score(student_scores)
score_improvements = calculate_score_improvement(student_scores)

add_calculated_values(student_scores, max_scores, average_score, score_improvements)

performance_dict = create_performance_dict(student_scores, average_score, last_test_date)

verbal_tutor_alerts, math_tutor_alerts, counselor_alerts = generate_alerts(student_scores)

st.subheader("Performance Dictionary")
performance_df = pd.DataFrame({
    'Year': performance_dict['scores_by_year'].keys(),
    'Average Score': performance_dict['scores_by_year'].values()
})
performance_df['Last Test Date'] = performance_dict['last_test_date']
performance_df['Company Average Score'] = performance_dict['average_score']
st.dataframe(performance_df)

st.subheader("Verbal Tutor Alerts")
for alert in verbal_tutor_alerts:
    st.write(f"Student: {alert[0]}, Verbal Tutor: {alert[1]}")

st.subheader("Math Tutor Alerts")
for alert in math_tutor_alerts:
    st.write(f"Student: {alert[0]}, Math Tutor: {alert[1]}")

st.subheader("Counselor Alerts")
for alert in counselor_alerts:
    st.write(f"Student: {alert[0]}, Counselor: {alert[1]}")

st.subheader("List of Students")
student_names = list_student_names(student_scores)
st.write(", ".join(student_names))

student_name = st.text_input("Enter the student's name to see the results")

if student_name:
    display_student_results(student_scores, student_name)
