
def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = bootstrap_root()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


def bootstrap_root():
    from madetomeasure.models.root import SiteRoot
    from madetomeasure.models.users import User
    from madetomeasure.models.users import Users
    from madetomeasure.models.surveys import Surveys
    from madetomeasure.models.participants import Participants
    from madetomeasure.models.questions import Questions

    root = SiteRoot()
    root['users'] = Users()
    #Create admin user with password admin as standard
    admin = User()
    admin.set_password('admin')
    admin.set_title('Administrator')
    root['users']['admin'] = admin
    
    root['surveys'] = Surveys()
    root['participants'] = Participants()
    root['questions'] = Questions()
    
    return root
