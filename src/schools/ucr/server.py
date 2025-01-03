from src.schools.ucr.extract import Course
from langchain_text_splitters import CharacterTextSplitter
import asyncio
import httpx
from bs4 import BeautifulSoup
from .extract import extract
from asyncio import Semaphore
from typing import List
from src.models import UCRCourseDB, BaseDB
from sqlalchemy import insert
from tqdm import tqdm
from src.dataset import AsyncSessionLocal
from src.process import post_process
urls = ['https://classes.usc.edu/term-20251/classes/drns/', 'https://classes.usc.edu/term-20251/classes/ali/', 'https://classes.usc.edu/term-20251/classes/amst/', 'https://classes.usc.edu/term-20251/classes/anth/', 'https://classes.usc.edu/term-20251/classes/arcg/', 'https://classes.usc.edu/term-20251/classes/arab/', 'https://classes.usc.edu/term-20251/classes/ahis/', 'https://classes.usc.edu/term-20251/classes/astr/', 'https://classes.usc.edu/term-20251/classes/bisc/', 'https://classes.usc.edu/term-20251/classes/cgsc/', 'https://classes.usc.edu/term-20251/classes/chem/', 'https://classes.usc.edu/term-20251/classes/clas/', 'https://classes.usc.edu/term-20251/classes/colt/', 'https://classes.usc.edu/term-20251/classes/core/', 'https://classes.usc.edu/term-20251/classes/cslc/', 'https://classes.usc.edu/term-20251/classes/scdc/', 'https://classes.usc.edu/term-20251/classes/ealc/', 'https://classes.usc.edu/term-20251/classes/easc/', 'https://classes.usc.edu/term-20251/classes/econ/', 'https://classes.usc.edu/term-20251/classes/engl/', 'https://classes.usc.edu/term-20251/classes/enst/', 'https://classes.usc.edu/term-20251/classes/gsec/', 'https://classes.usc.edu/term-20251/classes/fren/', 'https://classes.usc.edu/term-20251/classes/fsem/', 'https://classes.usc.edu/term-20251/classes/geol/', 'https://classes.usc.edu/term-20251/classes/germ/', 'https://classes.usc.edu/term-20251/classes/swms/', 'https://classes.usc.edu/term-20251/classes/gr/', 'https://classes.usc.edu/term-20251/classes/hebr/', 'https://classes.usc.edu/term-20251/classes/hist/', 'https://classes.usc.edu/term-20251/classes/hbio/', 'https://classes.usc.edu/term-20251/classes/inds/', 'https://classes.usc.edu/term-20251/classes/ir/', 'https://classes.usc.edu/term-20251/classes/iran/', 'https://classes.usc.edu/term-20251/classes/ital/', 'https://classes.usc.edu/term-20251/classes/js/', 'https://classes.usc.edu/term-20251/classes/lat/', 'https://classes.usc.edu/term-20251/classes/ling/', 'https://classes.usc.edu/term-20251/classes/math/', 'https://classes.usc.edu/term-20251/classes/mda/', 'https://classes.usc.edu/term-20251/classes/mdes/', 'https://classes.usc.edu/term-20251/classes/neur/', 'https://classes.usc.edu/term-20251/classes/nsci/', 'https://classes.usc.edu/term-20251/classes/os/', 'https://classes.usc.edu/term-20251/classes/phed/', 'https://classes.usc.edu/term-20251/classes/phil/', 'https://classes.usc.edu/term-20251/classes/phys/', 'https://classes.usc.edu/term-20251/classes/poir/', 'https://classes.usc.edu/term-20251/classes/port/', 'https://classes.usc.edu/term-20251/classes/posc/', 'https://classes.usc.edu/term-20251/classes/psyc/', 'https://classes.usc.edu/term-20251/classes/qbio/', 'https://classes.usc.edu/term-20251/classes/rel/', 'https://classes.usc.edu/term-20251/classes/rnr/', 'https://classes.usc.edu/term-20251/classes/russ/', 'https://classes.usc.edu/term-20251/classes/sll/', 'https://classes.usc.edu/term-20251/classes/smgt/', 'https://classes.usc.edu/term-20251/classes/soci/', 'https://classes.usc.edu/term-20251/classes/span/', 'https://classes.usc.edu/term-20251/classes/ssci/', 'https://classes.usc.edu/term-20251/classes/usc/', 'https://classes.usc.edu/term-20251/classes/viss/', 'https://classes.usc.edu/term-20251/classes/writ/', 'https://classes.usc.edu/term-20251/classes/actn/', 'https://classes.usc.edu/term-20251/classes/acct/', 'https://classes.usc.edu/term-20251/classes/arch/', 'https://classes.usc.edu/term-20251/classes/arch/', 'https://classes.usc.edu/term-20251/classes/acad/', 'https://classes.usc.edu/term-20251/classes/acad/', 'https://classes.usc.edu/term-20251/classes/idsn/', 'https://classes.usc.edu/term-20251/classes/prin/', 'https://classes.usc.edu/term-20251/classes/bus/', 'https://classes.usc.edu/term-20251/classes/baep/', 'https://classes.usc.edu/term-20251/classes/buad/', 'https://classes.usc.edu/term-20251/classes/buco/', 'https://classes.usc.edu/term-20251/classes/dso/', 'https://classes.usc.edu/term-20251/classes/fbe/', 'https://classes.usc.edu/term-20251/classes/gsba/', 'https://classes.usc.edu/term-20251/classes/mkt/', 'https://classes.usc.edu/term-20251/classes/mor/', 'https://classes.usc.edu/term-20251/classes/risk/', 'https://classes.usc.edu/term-20251/classes/bvc/', 'https://classes.usc.edu/term-20251/classes/cj/', 'https://classes.usc.edu/term-20251/classes/em/', 'https://classes.usc.edu/term-20251/classes/hrm/', 'https://classes.usc.edu/term-20251/classes/ht/', 'https://classes.usc.edu/term-20251/classes/lim/', 'https://classes.usc.edu/term-20251/classes/pjmt/', 'https://classes.usc.edu/term-20251/classes/cnma/', 'https://classes.usc.edu/term-20251/classes/cmpp/', 'https://classes.usc.edu/term-20251/classes/cntv/', 'https://classes.usc.edu/term-20251/classes/ctan/', 'https://classes.usc.edu/term-20251/classes/ctcs/', 'https://classes.usc.edu/term-20251/classes/ctin/', 'https://classes.usc.edu/term-20251/classes/ctpr/', 'https://classes.usc.edu/term-20251/classes/ctwr/', 'https://classes.usc.edu/term-20251/classes/iml/', 'https://classes.usc.edu/term-20251/classes/ctxa/', 'https://classes.usc.edu/term-20251/classes/ansc/', 'https://classes.usc.edu/term-20251/classes/ascj/', 'https://classes.usc.edu/term-20251/classes/cmgt/', 'https://classes.usc.edu/term-20251/classes/comm/', 'https://classes.usc.edu/term-20251/classes/dmm/', 'https://classes.usc.edu/term-20251/classes/dsm/', 'https://classes.usc.edu/term-20251/classes/jour/', 'https://classes.usc.edu/term-20251/classes/pr/', 'https://classes.usc.edu/term-20251/classes/prsm/', 'https://classes.usc.edu/term-20251/classes/pubd/', 'https://classes.usc.edu/term-20251/classes/dncr/', 'https://classes.usc.edu/term-20251/classes/danc/', 'https://classes.usc.edu/term-20251/classes/dntr/', 'https://classes.usc.edu/term-20251/classes/adnt/', 'https://classes.usc.edu/term-20251/classes/bite/', 'https://classes.usc.edu/term-20251/classes/bmdd/', 'https://classes.usc.edu/term-20251/classes/dent/', 'https://classes.usc.edu/term-20251/classes/dmat/', 'https://classes.usc.edu/term-20251/classes/coh/', 'https://classes.usc.edu/term-20251/classes/cby/', 'https://classes.usc.edu/term-20251/classes/dpbl/', 'https://classes.usc.edu/term-20251/classes/endo/', 'https://classes.usc.edu/term-20251/classes/gden/', 'https://classes.usc.edu/term-20251/classes/gpr/', 'https://classes.usc.edu/term-20251/classes/ofp/', 'https://classes.usc.edu/term-20251/classes/ofpm/', 'https://classes.usc.edu/term-20251/classes/opr/', 'https://classes.usc.edu/term-20251/classes/oper/', 'https://classes.usc.edu/term-20251/classes/orth/', 'https://classes.usc.edu/term-20251/classes/pedo/', 'https://classes.usc.edu/term-20251/classes/peri/', 'https://classes.usc.edu/term-20251/classes/pthl/', 'https://classes.usc.edu/term-20251/classes/rest/', 'https://classes.usc.edu/term-20251/classes/surg/', 'https://classes.usc.edu/term-20251/classes/dram/', 'https://classes.usc.edu/term-20251/classes/thte/',
        'https://classes.usc.edu/term-20251/classes/thtr/', 'https://classes.usc.edu/term-20251/classes/edcr/', 'https://classes.usc.edu/term-20251/classes/edco/', 'https://classes.usc.edu/term-20251/classes/edhp/', 'https://classes.usc.edu/term-20251/classes/edpt/', 'https://classes.usc.edu/term-20251/classes/educ/', 'https://classes.usc.edu/term-20251/classes/edue/', 'https://classes.usc.edu/term-20251/classes/engv/', 'https://classes.usc.edu/term-20251/classes/ame/', 'https://classes.usc.edu/term-20251/classes/aste/', 'https://classes.usc.edu/term-20251/classes/bme/', 'https://classes.usc.edu/term-20251/classes/che/', 'https://classes.usc.edu/term-20251/classes/ce/', 'https://classes.usc.edu/term-20251/classes/csci/', 'https://classes.usc.edu/term-20251/classes/dsci/', 'https://classes.usc.edu/term-20251/classes/ee/', 'https://classes.usc.edu/term-20251/classes/eis/', 'https://classes.usc.edu/term-20251/classes/ene/', 'https://classes.usc.edu/term-20251/classes/engr/', 'https://classes.usc.edu/term-20251/classes/ise/', 'https://classes.usc.edu/term-20251/classes/itp/', 'https://classes.usc.edu/term-20251/classes/masc/', 'https://classes.usc.edu/term-20251/classes/pte/', 'https://classes.usc.edu/term-20251/classes/sae/', 'https://classes.usc.edu/term-20251/classes/fine/', 'https://classes.usc.edu/term-20251/classes/art/', 'https://classes.usc.edu/term-20251/classes/crit/', 'https://classes.usc.edu/term-20251/classes/des/', 'https://classes.usc.edu/term-20251/classes/fdn/', 'https://classes.usc.edu/term-20251/classes/gep/', 'https://classes.usc.edu/term-20251/classes/wct/', 'https://classes.usc.edu/term-20251/classes/gct/', 'https://classes.usc.edu/term-20251/classes/scin/', 'https://classes.usc.edu/term-20251/classes/scis/', 'https://classes.usc.edu/term-20251/classes/arlt/', 'https://classes.usc.edu/term-20251/classes/si/', 'https://classes.usc.edu/term-20251/classes/gepn/', 'https://classes.usc.edu/term-20251/classes/arts/', 'https://classes.usc.edu/term-20251/classes/hinq/', 'https://classes.usc.edu/term-20251/classes/sana/', 'https://classes.usc.edu/term-20251/classes/life/', 'https://classes.usc.edu/term-20251/classes/psc/', 'https://classes.usc.edu/term-20251/classes/qrea/', 'https://classes.usc.edu/term-20251/classes/gpg/', 'https://classes.usc.edu/term-20251/classes/gph/', 'https://classes.usc.edu/term-20251/classes/gesm/', 'https://classes.usc.edu/term-20251/classes/dcl/', 'https://classes.usc.edu/term-20251/classes/gerd/', 'https://classes.usc.edu/term-20251/classes/gero/', 'https://classes.usc.edu/term-20251/classes/grsc/', 'https://classes.usc.edu/term-20251/classes/grsc/', 'https://classes.usc.edu/term-20251/classes/law/', 'https://classes.usc.edu/term-20251/classes/law/', 'https://classes.usc.edu/term-20251/classes/medk/', 'https://classes.usc.edu/term-20251/classes/acmd/', 'https://classes.usc.edu/term-20251/classes/adsc/', 'https://classes.usc.edu/term-20251/classes/ias/', 'https://classes.usc.edu/term-20251/classes/anst/', 'https://classes.usc.edu/term-20251/classes/bioc/', 'https://classes.usc.edu/term-20251/classes/cbg/', 'https://classes.usc.edu/term-20251/classes/dsr/', 'https://classes.usc.edu/term-20251/classes/hp/', 'https://classes.usc.edu/term-20251/classes/intd/', 'https://classes.usc.edu/term-20251/classes/mbph/', 'https://classes.usc.edu/term-20251/classes/mded/', 'https://classes.usc.edu/term-20251/classes/med/', 'https://classes.usc.edu/term-20251/classes/medb/', 'https://classes.usc.edu/term-20251/classes/meds/', 'https://classes.usc.edu/term-20251/classes/micb/', 'https://classes.usc.edu/term-20251/classes/mphy/', 'https://classes.usc.edu/term-20251/classes/neum/', 'https://classes.usc.edu/term-20251/classes/niin/', 'https://classes.usc.edu/term-20251/classes/ohns/', 'https://classes.usc.edu/term-20251/classes/pain/', 'https://classes.usc.edu/term-20251/classes/path/', 'https://classes.usc.edu/term-20251/classes/pbhs/', 'https://classes.usc.edu/term-20251/classes/phbi/', 'https://classes.usc.edu/term-20251/classes/pm/', 'https://classes.usc.edu/term-20251/classes/pcpa/', 'https://classes.usc.edu/term-20251/classes/scrm/', 'https://classes.usc.edu/term-20251/classes/trgn/', 'https://classes.usc.edu/term-20251/classes/mus/', 'https://classes.usc.edu/term-20251/classes/artl/', 'https://classes.usc.edu/term-20251/classes/mtec/', 'https://classes.usc.edu/term-20251/classes/mscr/', 'https://classes.usc.edu/term-20251/classes/mtal/', 'https://classes.usc.edu/term-20251/classes/mucm/', 'https://classes.usc.edu/term-20251/classes/muco/', 'https://classes.usc.edu/term-20251/classes/mucd/', 'https://classes.usc.edu/term-20251/classes/muen/', 'https://classes.usc.edu/term-20251/classes/muhl/', 'https://classes.usc.edu/term-20251/classes/muin/', 'https://classes.usc.edu/term-20251/classes/mujz/', 'https://classes.usc.edu/term-20251/classes/mpem/', 'https://classes.usc.edu/term-20251/classes/mpgu/', 'https://classes.usc.edu/term-20251/classes/mpks/', 'https://classes.usc.edu/term-20251/classes/mppm/', 'https://classes.usc.edu/term-20251/classes/mpst/', 'https://classes.usc.edu/term-20251/classes/mpva/', 'https://classes.usc.edu/term-20251/classes/mpwp/', 'https://classes.usc.edu/term-20251/classes/musc/', 'https://classes.usc.edu/term-20251/classes/scor/', 'https://classes.usc.edu/term-20251/classes/nurs/', 'https://classes.usc.edu/term-20251/classes/nurs/', 'https://classes.usc.edu/term-20251/classes/ocst/', 'https://classes.usc.edu/term-20251/classes/ot/', 'https://classes.usc.edu/term-20251/classes/phar/', 'https://classes.usc.edu/term-20251/classes/bpmk/', 'https://classes.usc.edu/term-20251/classes/bpsi/', 'https://classes.usc.edu/term-20251/classes/cxpt/', 'https://classes.usc.edu/term-20251/classes/hcda/', 'https://classes.usc.edu/term-20251/classes/mptx/', 'https://classes.usc.edu/term-20251/classes/phrd/', 'https://classes.usc.edu/term-20251/classes/pmep/', 'https://classes.usc.edu/term-20251/classes/psci/', 'https://classes.usc.edu/term-20251/classes/rsci/', 'https://classes.usc.edu/term-20251/classes/rxrs/', 'https://classes.usc.edu/term-20251/classes/bkn/', 'https://classes.usc.edu/term-20251/classes/pt/', 'https://classes.usc.edu/term-20251/classes/ppdp/', 'https://classes.usc.edu/term-20251/classes/aest/', 'https://classes.usc.edu/term-20251/classes/hmgt/', 'https://classes.usc.edu/term-20251/classes/ms/', 'https://classes.usc.edu/term-20251/classes/naut/', 'https://classes.usc.edu/term-20251/classes/nsc/', 'https://classes.usc.edu/term-20251/classes/ppd/', 'https://classes.usc.edu/term-20251/classes/ppde/', 'https://classes.usc.edu/term-20251/classes/plus/', 'https://classes.usc.edu/term-20251/classes/red/', 'https://classes.usc.edu/term-20251/classes/swdp/', 'https://classes.usc.edu/term-20251/classes/swkc/', 'https://classes.usc.edu/term-20251/classes/swko/', 'https://classes.usc.edu/term-20251/classes/pdf/', 'https://classes.usc.edu/term-20251/classes/ptbk/']


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="o200k_base", chunk_size=200, chunk_overlap=30
)


def from_pydantic(course: Course):
    return UCRCourseDB(
        source_url=course._source_url,
        section=course.section,
        units=course.units,
        offering_title=course.offering_title,
        instructor_name=course.instructor,
        days=course.days,
        time=course.time,
        location=course.location,
        grade_scheme=course.grade_scheme,
        registered=course.registered,
        total_seats=course.total_seats
    )


async def process_url(client: httpx.AsyncClient, url: str, sem: Semaphore) -> list:
    retries = 3
    while retries > 0:
        try:
            async with sem:
                response = await client.get(url, timeout=20)
                text = response.text
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.get_text()
            segments = text.split('\n')
            result = await extract(segments, url)
            return result
        except Exception as e:
            print(f"Error processing {url}: {e}")
            retries -= 1
            if retries > 0:
                print(f"Retrying... {retries} attempts left")
                await asyncio.sleep(1)  # Wait 1 second before retrying
    return []


async def main() -> List[BaseDB]:
    all_courses: list = []
    sem = Semaphore(5)  # Limit to 10 concurrent requests
    progress = tqdm(total=len(urls), desc="Fetching courses")
    async with httpx.AsyncClient() as client:
        tasks: list = []
        for url in urls:
            async def process_with_progress(url):
                result = await process_url(client, url, sem)
                progress.update(1)
                return result
            tasks.append(process_with_progress(url))
        results: list = await asyncio.gather(*tasks)
        for courses in results:
            all_courses.extend(courses)
    progress.close()
    all_courses_db: List[UCRCourseDB] = list(
        map(from_pydantic, all_courses))
    all_courses_db = await post_process(all_courses_db, [course.offering_title for course in all_courses], [
        course.offering_title for course in all_courses])
    return all_courses_db


if __name__ == "__main__":
    asyncio.run(main())
