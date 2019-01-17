import json
from urllib.request import Request, urlopen
from urllib import parse
from bs4 import BeautifulSoup

def get_clean_html(url):
    """Returns 'clean_html' (i.e BeautifulSoup processed html) for a given link"""
    
    req = Request(url, headers={"User-Agent":"Mozilla/5.0"})
    raw_html = urlopen(req).read()
    clean_html = BeautifulSoup(raw_html, "html5lib")
    return clean_html
    
    

def is_new_jobs(job_field_dict):
    """Given a dictionary with "url" and "data_list" keys; this function checks 
       the url to see if there are any new jobs (i.e jobs on the website that 
       are not in "data_list". Returns true if one or more new jobs exist, 
       otherwise false."""
    
    html = get_clean_html(job_field_dict["url"])
    #need to account for the initial case where there are no jobs    
    compare_link = job_field_dict["data_list"][0][2] if len(job_field_dict["data_list"]) > 0 else None 
    
    #remember jobs are sorted by most recent on yudu, so we only need to check the first one
    job_title = html.find("div", class_="job-toplink")
    if job_title != None:
        job_link = "https://www.yudu.co.nz" + job_title.find("a")["href"]
    
        if job_link == compare_link:
            return False
        else:
            return True
    
    #no jobs on the site at all
    else:
        return False
    
    

def copy_new_jobs(job_field_dict):
    """Write something here"""
    
    html = get_clean_html(job_field_dict["url"])
    new_jobs = []
    job_containers = html.find_all("div", class_="job-holder")
    
    #if the data_list is empty to start with it will fail if we try to index it, so we need to do this
    compare_link = job_field_dict["data_list"][0][2] if len(job_field_dict["data_list"]) > 0 else None 
    
    i = 0
    link = "https://www.yudu.co.nz" + job_containers[i].find("div", class_="job-toplink").find("a")["href"]
    
    #warning! this relies on the assumption that the most recent link we viewed in the last session has not been taken down
    while link != compare_link and i < len(job_containers):
        
        job_title = job_containers[i].find("div", class_="job-toplink").find("a").text
        job_location = job_containers[i].find("span", class_="jxt-result-loc").text
        job_date = job_containers[i].find("span", class_="dateText").text
        
        new_jobs.append((job_title, job_location, link, job_date))
        
        i += 1
        if i < len(job_containers): #to avoid index errors
            link = "https://www.yudu.co.nz" + job_containers[i].find("div", class_="job-toplink").find("a")["href"]

    job_field_dict["data_list"] = new_jobs + job_field_dict["data_list"]
    
    return job_field_dict



def print_size_warning(job_field_dict, num_jobs_added):
    """Write something here"""
    
    #our bot doesn't check past the first page, so if more than 12 jobs are added since we last checked there may be new posts
    #that we can't see on the next page (remember there are 12 posts per page)
    if num_jobs_added >= 12:
        print("WARNING!: There may be more listings since you last checked on page 2.\nI recommend you check page 2 of this link: {}".format(job_field_dict["url"]))
        
        if num_jobs_added < len(job_field_dict["data_list"]):
            print("The most recent job I added to my database in the previous session was \"{}\"\n".format(job_field_dict["data_list"][num_jobs_added][0]))
        
    else:
        print("")
    
    
    
def main():
    is_change = False
    
    with open("webscraping_data.json", "r") as filehandle:
        webscraping_data = json.load(filehandle)   
    
    for title in webscraping_data.keys():
        heading = "{} Positions".format(title.title())
        print(heading.center(80, "*"))
        
        if is_new_jobs(webscraping_data[title]):
            print("New {} positions found!".format(title))
            is_change = True
            
            old_num_jobs = len(webscraping_data[title]["data_list"])
            webscraping_data[title] = copy_new_jobs(webscraping_data[title])
            num_new_jobs = len(webscraping_data[title]["data_list"]) - old_num_jobs
            
            print("Found {} new position(s)\n".format(num_new_jobs))
            for i in range(num_new_jobs):
                print("Title: {}\nLocation: {}\nLink: {}\n".format(*webscraping_data[title]["data_list"][i]))
                
            print_size_warning(webscraping_data[title], num_new_jobs)
            
        else:
            print("No new positions found.\n")
            
    if is_change:
        with open("webscraping_data.json", "w") as filehandle:
            json.dump(webscraping_data, filehandle)
        pass
        
    

main()
