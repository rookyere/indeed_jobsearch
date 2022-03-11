from bs4 import BeautifulSoup
import requests, sys,time,os  
import pandas as pd


try:

    job_role_to_search = input('\nWhat job role do you want to search?: ')

    experience_level_criteria = input('\nChoose experience level: \n'
                        '\t1. Entry level \n'
                        '\t2. Mid level \n'
                        '\t3. Senior level \n'
                        '\t4. Any \n'
                        '>: '
                        ) or '4'
    if len(experience_level_criteria) == 0:
        sys.exit('\nError: Experience level field cannot be empty\n')
    elif experience_level_criteria == '1':
        exp_level = 'entry_level'
    elif experience_level_criteria == '2':
        exp_level = 'mid_level'
    elif experience_level_criteria == '3':
        exp_level = 'senior_level'
    elif experience_level_criteria == '4':
        exp_level = ' '
    else: sys.exit('\nError: Invalid input specified\n')

    date_posted_criteria = input('\nSearch for jobs posted within the last: \n' 
                        '\tChoose from below options: \n'
                        '\t1. 24 hrs \n'
                        '\t2. 3 days \n'
                        '\t3. 7 days \n'
                        '\t4. 14 days \n'
                        '\t5. Any\n'
                        '>: '
                        ) or '5'
    if date_posted_criteria == '1':
        date_posted = '1'
    elif date_posted_criteria == '2':
        date_posted = '3'
    elif date_posted_criteria == '3':
        date_posted = '7'
    elif date_posted_criteria == '4':
        date_posted = '14'
    elif date_posted_criteria == '5':
        date_posted = ' '
    else: sys.exit('\nError: Invalid input specified\n')    

    job_location = input('\nChoose job location:\n:'
                        '\t1. Any \n'
                        '\t2. Remote \n'
                        '\t3. Other \n'
                        '>: '
                        ).lower() or '1'
    if job_location == '1' or job_location == 'Any':
        job_location = ' '
    if job_location == '2':
        job_location = 'Remote'
    if job_location == '3' or job_location == 'other':
        job_location = input('\nPlease provide job location to search >: ')


    def extract_job_info(job,job_link,job_info_dict):
        job_role     = job.h2.text.strip('new')
        company_name = job.find('span','companyName').text
        location     = job.find('div','companyLocation').text
        
        salary_div = job.find_all('div', 'heading6 tapItem-gutter metadataContainer noJEMChips salaryOnly')
        salary = ' '
        try:
            for div in salary_div:
                salary = div.find('div', 'metadata salary-snippet-container').text
        except:
            salary = ' '

        published_date = job.find('div','heading6 tapItem-gutter result-footer').span.text.lstrip('Posted')

        job_info_dict['Role']             = job_role
        job_info_dict['Company_name']     = company_name
        job_info_dict['Location']         = location
        job_info_dict['Salary']           = salary
        job_info_dict['Published_date']   = published_date
        job_info_dict['Further_info']     = job_link

        details_url_list.append(job_info_dict)
    
        print(f'''
                Role                : {job_role}
                Company name        : {company_name}
                Location            : {location}
                Salary              : {salary}
                Published date      : {published_date}
                Further_info        : {job_link}
                ''')
    

    jobs_info_list = []
    details_url_list = []
    page_num = 0
    total_job_count = 0

    for page in range(0, 1000, 10):
        page_num=page_num + 1
        print(f'\n********************* PAGE {page_num} **************************')
        url = f'https://www.indeed.com/jobs?q={job_role_to_search}&l={job_location}&explvl={exp_level}&fromage={date_posted}&start={page}'
        
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        div_tag = soup.find('div', id='mosaic-zone-jobcards')

        a_tag = div_tag.find_all('a')
        job_count_on_page = 0
        for a in a_tag:
            
            if a.has_attr('data-mobtk'):
                job_info_dict = dict()

                job_count_on_page = job_count_on_page + 1
                print(f'\n=====================')
                job_link = 'https://www.indeed.com' + a.get('href')
                job_div_tag = a.find_all('div', class_='job_seen_beacon')
                for job_info in job_div_tag:
                    extract_job_info(job_info,job_link,job_info_dict)

        total_job_count = total_job_count + job_count_on_page
            
        if job_count_on_page < 15:
            break

    print(f'Total jobs found: {total_job_count}')

    dt = time.localtime()
    dt_fmt = time.strftime('%d-%m-%Y-%H:%M', dt)
    date_time = dt_fmt.replace(':', '-')

    excel_dir = 'Indeed-jobs'
    excel_fn = f'{excel_dir}/{job_role_to_search}' + '-'+ date_time + '.xlsx'

    if os.path.exists(excel_dir):
        pass
    else:
        p=os.makedirs(excel_dir)

    df = pd.DataFrame.from_dict(details_url_list)
    df.to_excel(excel_fn)


except KeyboardInterrupt:
    sys.exit('\n\nProgram terminated successfully.\n')
except AttributeError:
    print('\n@@@@@@@@@@ SORRY!!! @@@@@@@@@@')
    sys.exit('\nNo results found for search criteria. Please adjust the criteria and try again.\n')
