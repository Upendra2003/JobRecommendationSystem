from flask import Flask,render_template,request,redirect
import pickle
import pandas as pd
import ast

app=Flask(__name__)

#open pickle files
jobs_list_dict=pickle.load(open('jobs.pkl','rb'))
urls_list_dict=pickle.load(open('urls.pkl','rb'))
similarity=pickle.load(open('similarity.pkl','rb'))
jobs_list_df=pd.DataFrame(jobs_list_dict)
urls_list_df=pd.DataFrame(urls_list_dict)

def recommend(job_role,location,salary_range,status):
    try:
        # Ensure salary_range is a tuple with two elements
        salary_range=ast.literal_eval(salary_range)
        lower_bound, upper_bound = salary_range
        print(lower_bound,upper_bound)
        print(type(lower_bound),type(upper_bound))
        filtered_df = jobs_list_df[
            (jobs_list_df['Job Roles'] == job_role) &
            (jobs_list_df['Location'] == location) &
            (jobs_list_df['Salary'].between(lower_bound,upper_bound)) &
            (jobs_list_df['Employment Status'] == status)
        ]

        # print("Filtered data:")
        # print(filtered_df)

        if filtered_df.empty:
            print("No matching jobs found.")
            return []

        job_index = filtered_df.index[0]
        print("Job index:", job_index)

        distances = similarity[job_index]
        jobs_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

        index_list = [i[0] for i in jobs_list]
        return index_list
    except Exception as e:
        print(f"Error: {e}")
        return []




@app.route('/')
def home():
    job_roles=jobs_list_df['Job Roles'].unique()
    job_locations=jobs_list_df['Location'].unique()
    job_status=jobs_list_df['Employment Status'].unique()
    salary_range=[
        (0, 50000),
        (50001, 100000),
        (100001, 150000),
        (150001, 200000),
        (200001, 300000),
        (300001, 500000),
        (500001, 1000000),
        (1000001, 2000000)
    ]
    return render_template('index.html',job_roles=job_roles,job_locations=job_locations,job_status=job_status,salary_range=salary_range)

@app.route('/recommend',methods=['GET','POST'])
def recommend_job():
    if request.method=='POST':
        selected_role_option = request.form.get('selected_role_option')
        selected_loc_option = request.form.get('selected_loc_option')
        selected_stat_option = request.form.get('selected_stat_option')
        selected_sal_option = request.form.get('selected_sal_option')
        # print(selected_loc_option,selected_role_option,selected_stat_option,selected_sal_option)
        job_list=recommend(selected_role_option,selected_loc_option,selected_sal_option,selected_stat_option)
        job_details={}
        msg=''
        if job_list==[]:
            msg='No Valid Job Found'
        else:
            for i in job_list:
                job_details[i] = {
                    'Company Name': jobs_list_df.iloc[i]['Company Name'],
                    'Job Title': jobs_list_df.iloc[i]['Job Title'],
                    'Salary': jobs_list_df.iloc[i]['Salary'],
                    'Location': jobs_list_df.iloc[i]['Location'],
                    'Employment Status': jobs_list_df.iloc[i]['Employment Status'],
                    'Company Logo':urls_list_df.iloc[i]['Company Logo'],
                    'Company Url':urls_list_df.iloc[i]['Company Url'],
                }
        return render_template('recommendations.html',job_details=job_details,msg=msg)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)