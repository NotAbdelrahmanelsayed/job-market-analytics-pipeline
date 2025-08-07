from seleniumbase import SB
import random
import sys

sys.argv.append("-n")
from pathlib import Path
import json
import pprint


CLS_BTN_SEL = 'button[class="CloseButton"]'
LEFT_CARD_SEL = 'li[data-test="jobListing"][data-jobid]'
JOB_ID_SEL = "data-jobid"
TITLE_SEL = 'a[class^="JobCard_jobTitle_"]'
LOCATION_SEL = 'div[class^="JobCard_location__"]'
SALARY_SEL = 'div[class^="JobCard_salaryEstimate_"]'
DESC_SEL = '[class^="JobDetails_jobDescription_"]'
LOAD_MORE_BTN = 'button[data-test="load-more"]'
DATA_DIR = "data"
DATA_PATH = Path.joinpath(DATA_DIR, "glassador.json")


def write_job(record, path=DATA_PATH):
    # Make sure the data file exist
    Path.touch(DATA_PATH, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


with SB(uc=True, ad_block=True) as sb:
    url = "https://www.glassdoor.com/Job/data-engineer-jobs-SRCH_KO0,13.htm"

    # Open the link in stealthy mode
    sb.activate_cdp_mode(url)
    sb.sleep(10)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
    sb.cdp.scroll_to_bottom()
    sb.sleep(2)
    sb.cdp.scroll_to_top()
    visited = set()

    job_count = 0
    while True:
        sb.cdp.click_if_visible(CLS_BTN_SEL)
        jobs = sb.cdp.find_elements(LEFT_CARD_SEL)
        jobs = jobs[job_count:]  # Ignore scraped jobs
        for job in jobs:

            try:
                # Close AD
                sb.cdp.click_if_visible(CLS_BTN_SEL)

                # Assert job is unique
                job_id = job.get_attribute(JOB_ID_SEL)
                if not job_id or job_id in visited:
                    print(f"job_id {job_id} already scrapped skipping it....")
                    continue

                # Get job title
                title_el = job.query_selector(TITLE_SEL)
                title = title_el.text if title_el else "NA"

                # Get job link
                link = title_el.get_attribute("href") if title_el else "NA"

                # Get job location
                location_el = job.query_selector(LOCATION_SEL)
                location = location_el.text if location_el else "NA"

                # Get job salary
                salary_el = job.query_selector(SALARY_SEL)
                salary = str(salary_el.text) if salary_el else "NA"

                # Scroll into job and click on it
                job.scroll_into_view()
                job.flash(duration=0.5, color="EE4488")
                job.gui_click()
                sb.sleep(4)

                # Get job description
                description_el = sb.cdp.find_element(DESC_SEL)
                description = description_el.text if description_el else "NA"

                job_info = {
                    "id": job_id,
                    "date": "",
                    "title": title,
                    "link": link,
                    "location": location,
                    "salary": salary,
                    "description": description,
                }

                # Write job on the desk
                write_job(job_info)

                # Debug
                # print(title, link, location, salary, description)
                print("-" * 30, job_count, "-" * 30)
                pprint.pprint(job_info)

                job_count += 1
                visited.add(job_id)

            except Exception as e:
                print(f"[!] Skipping job #{job_count} due to error: {e}")

        if job_count >= 300:
            break

        next_page = sb.cdp.scroll_into_view(LOAD_MORE_BTN)

        sb.sleep(random.uniform(2.5, 4.5))
        sb.cdp.scroll_to_bottom()
        sb.sleep(random.uniform(1.5, 2.5))

        sb.cdp.scroll_into_view(LOAD_MORE_BTN)
        sb.cdp.gui_hover_element(LOAD_MORE_BTN)
        sb.sleep(random.uniform(1.2, 2.0))

        sb.cdp.click_if_visible(LOAD_MORE_BTN)

    sb.save_screenshot("full_page.png")