
def evolve(root):
    """ This script contained buggs """
    from madetomeasure.models.survey_section import TextSection

    organisations = [x for x in root.values() if x.content_type == 'Organisation']
    for org in organisations:
        surveys = [x for x in org['surveys'].values() if x.content_type == 'Survey']
        for survey in surveys:
            welcome_text = getattr(survey, '__welcome_text__', None)
            if welcome_text:
                ts = TextSection(title = u"Welcome text", description = welcome_text)
                name = ts.suggest_name(survey)
                survey[name] = ts
                delattr(survey, '__welcome_text__')
            finished_text = getattr(survey, '__finished_text__', None)
            if finished_text:
                ts = TextSection(title = u"Finished text", description = finished_text)
                name = ts.suggest_name(survey)
                survey[name] = ts
                delattr(survey, '__finished_text__')
