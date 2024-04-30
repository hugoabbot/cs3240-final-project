import logging
from django.conf import settings

logging.basicConfig(format=None, level=logging.DEBUG)
logging.debug("Logging started on %s for %s" % (logging.root.name, logging.getLevelName(logging.root.level)))