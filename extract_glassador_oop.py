from pathlib import Path
from seleniumbase import SB
import json
import random

class ExtractGlassador:
    CLS_BTN_SEL = 'button[class="CloseButton"]'
    LEFT_CARD_SEL = 'li[data-test="jobListing"][data-jobid]'
    JOB_ID_SEL = "data-jobid"
    TITLE_SEL = 'a[class^="JobCard_jobTitle_"]'
    LOCATION_SEL = 'div[class^="JobCard_location__"]'
    SALARY_SEL = 'div[class^="JobCard_salaryEstimate_"]'
    DESC_SEL = '[class^="JobDetails_jobDescription_"]'
    LOAD_MORE_BTN = 'button[data-test="load-more"]'
    DATA_DIR = Path("data")
    DATA_PATH = DATA_DIR.joinpath("glassador.json")
    URL = "https://www.glassdoor.com/Job/data-engineer-jobs-SRCH_KO0,13.htm"

    def __init__(self):
        self.job_count = 0
        self.visited = set()

    def write_job(self, record, path=DATA_PATH):
        # Make sure the data file exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_PATH.touch(exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def extract_job_data(self, sb, job):
        # Assert job is unique
        job_id = job.get_attribute(self.JOB_ID_SEL)
        if not job_id or job_id in self.visited:
            print(f"job_id {job_id} already scrapped skipping it....")
            return None

        # Get job title
        title_el = job.query_selector(self.TITLE_SEL)
        title = title_el.text if title_el else "NA"

        # Get job link
        link = title_el.get_attribute("href") if title_el else "NA"

        # Get job location
        location_el = job.query_selector(self.LOCATION_SEL)
        location = location_el.text if location_el else "NA"

        # Get job salary
        salary_el = job.query_selector(self.SALARY_SEL)
        salary = str(salary_el.text) if salary_el else "NA"

        # Scroll into job and click on it
        job.scroll_into_view()
        job.flash(duration=0.5, color="EE4488")
        job.gui_click()
        sb.sleep(4)

        # Get job description
        description_el = sb.cdp.find_element(self.DESC_SEL)
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

        return job_info

        

    def run(self):
        with SB(uc=True, ad_block=True, window_size='1280, 720') as sb:
            # Open the link in stealthy mode
            sb.activate_cdp_mode(self.URL)
            sb.sleep(10) # Safe wait time to load captcha if exist
            sb.uc_gui_click_captcha()
            sb.sleep(random.uniform(1, 3))
            sb.cdp.scroll_to_bottom()
            sb.sleep(random.uniform(1, 3))
            sb.cdp.scroll_to_top()

            while True:
                sb.cdp.click_if_visible(self.CLS_BTN_SEL)
                jobs = sb.cdp.find_elements(self.LEFT_CARD_SEL)
                jobs = jobs[self.job_count:]  # Ignore scraped jobs
                for job in jobs:
                    try:
                        sb.cdp.click_if_visible(self.CLS_BTN_SEL)
                        job_info = self.extract_job_data(sb, job)
                        
                        if not job_info:
                            continue

                        # Write job on the desk
                        self.write_job(job_info)
                        self.job_count += 1
                        self.visited.add(job_info['id'])
                        print(f"[+] Job {job_info['id']} scraped and saved.")

                    except Exception as e:
                        print(f"[!] Skipping job #{self.job_count} due to error: {e}")

                if not sb.cdp.is_element_visible(self.LOAD_MORE_BTN):
                    break

                # Try loading more jobs
                sb.sleep(random.uniform(2.5, 4.5))
                sb.cdp.scroll_to_bottom()
                sb.sleep(random.uniform(1.5, 2.5))
                sb.cdp.scroll_into_view(self.LOAD_MORE_BTN)
                sb.cdp.gui_hover_element(self.LOAD_MORE_BTN)
                sb.sleep(random.uniform(1.2, 2.0))

                sb.cdp.click_if_visible(self.LOAD_MORE_BTN)

            sb.save_screenshot("full_page.png")

if __name__ == "__main__":
    extractor = ExtractGlassador()
    extractor.run()