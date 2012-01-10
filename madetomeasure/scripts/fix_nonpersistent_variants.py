import transaction
from BTrees.OOBTree import OOBTree

from madetomeasure.scripts.worker import ScriptWorker
from madetomeasure.interfaces import IOrganisation


def fix_nonpersistent_variants(*args):
    """ Organisations stored language variants in a regular dict that isn't persistent
        This fixes that.
    """
    worker = ScriptWorker('fix_nonpersistent_variants')
    
    orgs = [x for x in worker.root.values() if IOrganisation.providedBy(x)]
    for org in orgs:
        for (q_uid, value) in org.variants.items():
            if not isinstance(org.variants[q_uid], dict):
                continue
            org.variants[q_uid] = OOBTree(value)
            print "Fixing variant in %s" % org

    transaction.commit()
    print "Done"
    
    worker.shutdown()
    