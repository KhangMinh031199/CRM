import api
import settings
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size = 15)


shop_id_select = "64946c9b5c897ede7f85aaae"
page = 1

list_survey = []
list_survey_splash = api.list_survey_splash(shop_id_select,
                                            page=page,
                                            page_size=settings.ITEMS_PER_PAGE)

for survey in list_survey_splash:
    survey_type = survey.get('survey_type')
    ans_dig = []
    if survey_type == 'multi_select' or survey_type == 'one_select':
        answers = survey.get('answers')
        for ans in answers:
            ans_item = []
            total_res = api.count_result_survery(survey['_id'], survey_type,
                                                 shop_id_select, ans.get('id'))
            ans_item.append(api.remove_accents(str(ans.get('value'))))
            ans_item.append(total_res)
            ans_dig.append(ans_item)

    if survey_type == 'rating':
        min_point = survey.get('min_point', 1)
        max_point = survey.get('max_point', 10)
        for ans in range(int(min_point), int(max_point) + 1):
            ans_item = []
            total_res = api.count_result_survery(survey['_id'], survey_type,
                                                 shop_id_select, ans)
            ans_item.append(ans)
            ans_item.append(total_res)
            ans_dig.append(ans_item)
    survey['_id'] = str(survey['_id'])
    survey['shop_id'] = str(survey['shop_id'])
    survey['ans_dig'] = ans_dig
    if survey_type == 'comment':
        comment_count = api.count_result_survey_by_survey_id(
            survey['_id'], survey_type, shop_id_select)
        survey['comment_count'] = comment_count
    list_survey.append(survey)
for page in list_survey:
    question = page.get('question')
    pdf.cell(50, 10, txt = question.encode('latin-1', 'ignore').decode('latin-1'))
    pdf.ln()
    ans_dig = page.get('ans_dig')
    with pdf.table() as table:
        for dig in ans_dig:
                row = table.row()
                for datum in dig:
                    row.cell(datum)

pdf.output("survey.pdf")  
